import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from openai import AzureOpenAI

# -------------------------------
# CONFIG
# -------------------------------
load_dotenv()

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "integration_docs"
EMBED_MODEL = r"C:\models\all-MiniLM-L6-v2"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)
embedder = SentenceTransformer(EMBED_MODEL)

llm = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# -------------------------------
# SEMANTIC SEARCH
# -------------------------------
def semantic_search(query, top_k=8):
    q_emb = embedder.encode([query]).tolist()[0]
    res = collection.query(query_embeddings=[q_emb], n_results=top_k)

    results = []
    for doc, meta, dist in zip(
        res["documents"][0],
        res["metadatas"][0],
        res["distances"][0]
    ):
        results.append({
            "text": doc,
            "meta": meta,
            "score": round(1 - dist, 4)
        })
    return results

# -------------------------------
# LLM ANSWER
# -------------------------------
def answer_question(question, results):
    if not results:
        return "Insufficient information in the indexed Integration documents."

    context = "\n\n".join(
        f"[{i}] {r['meta']['doc_type']} | {r['meta']['path']}\n{r['text']}"
        for i, r in enumerate(results, 1)
    )

    prompt = f"""

u are an Integration Documentation Assistant.

Rules:
- Answer ONLY using the provided context.
- Do NOT say "Insufficient information" if partial or related information is available.
- If full architecture or end-to-end flow is not present:
  - Clearly state which parts are available
  - Clearly state which parts are missing
- Use Mapping details to explain data flow, fields, and interactions wherever possible.
"

Context:
{context}

Question:
{question}

Answer with:
- Summary
- Details
- Sources
"""

    response = llm.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "Answer using integration documents only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content