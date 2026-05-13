import os
import hashlib
import pandas as pd
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from docx import Document
import chromadb

# -------------------------------
# CONFIG
# -------------------------------
DATA_ROOT = "data"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "integration_docs"
EMBED_MODEL = r"C:\models\all-MiniLM-L6-v2"

# -------------------------------
# INIT
# -------------------------------
embedder = SentenceTransformer(EMBED_MODEL)
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

# -------------------------------
# HELPERS
# -------------------------------
def sha_id(*values):
    return hashlib.sha1("|".join(values).encode()).hexdigest()

def read_pdf(path):
    reader = PdfReader(path)
    return [(p.extract_text() or "", {"page": i + 1}) for i, p in enumerate(reader.pages)]

def read_docx(path):
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [(text, {})]

def read_excel(path):
    xls = pd.ExcelFile(path)
    chunks = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet).fillna("")
        rows = [
            f"Row {i}: " + "; ".join(f"{k}={v}" for k, v in row.items() if str(v).strip())
            for i, row in enumerate(df.to_dict("records"), 1)
        ]
        if rows:
            chunks.append(("\n".join(rows), {"sheet": sheet}))
    return chunks

def read_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [(f.read(), {})]

def load_file(path, doc_type):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return read_pdf(path)
    if ext == ".docx":
        return read_docx(path)
    if ext in (".xlsx", ".xls"):
        return read_excel(path)
    if ext in (".txt", ".md", ".csv"):
        return read_txt(path)
    return []

# -------------------------------
# MAIN INDEXER
# -------------------------------
def index():
    docs, metas, ids = [], [], []

    for project in os.listdir(DATA_ROOT):
        p_path = os.path.join(DATA_ROOT, project)
        if not os.path.isdir(p_path):
            continue

        for integ in os.listdir(p_path):
            i_path = os.path.join(p_path, integ)
            if not os.path.isdir(i_path):
                continue

            for doc_type in ("HLD", "Mapping", "DOR"):
                d_path = os.path.join(i_path, doc_type)
                if not os.path.isdir(d_path):
                    continue

                for root, _, files in os.walk(d_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, DATA_ROOT)

                        chunks = load_file(full_path, doc_type)
                        for i, (text, extra) in enumerate(chunks):
                            if not text.strip():
                                continue

                            cid = sha_id(project, integ, doc_type, rel_path, str(i))
                            ids.append(cid)
                            docs.append(text)
                            meta = {
                                "project": project,
                                "integration": integ,
                                "doc_type": doc_type,
                                "file": file,
                                "path": rel_path,
                                "chunk": i
                            }
                            meta.update(extra)
                            metas.append(meta)

    print("Embedding & storing...")
    embeddings = embedder.encode(docs, show_progress_bar=True).tolist()
    collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
    print(f"Indexed {len(ids)} chunks")

if __name__ == "__main__":
    index()