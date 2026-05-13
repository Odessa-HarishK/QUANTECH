# 📘 QuanTech – Integration Knowledge Assistant

QuanTech is an AI-powered knowledge assistant that enables teams to ask natural-language questions about enterprise integrations (ICS, Paynet, SmartComm, etc.) and retrieve grounded answers from internal documentation such as HLDs, mappings, and samples.

The project uses a **Retrieval-Augmented Generation (RAG)** architecture with:
- ChromaDB (vector store)
- Python backend
- Streamlit UI

---

## 🧩 Architecture Overview

- **Data Ingestion** → Integration docs are parsed and embedded
- **Vector Store** → ChromaDB (persisted locally)
- **Query Layer** → Semantic search over vectors
- **UI** → Streamlit-based web application

> ⚠️ Note: Large documents, embeddings, and environment files are intentionally excluded from the Git repository.

---

## ✅ Prerequisites

Ensure the following are installed:

- Python **3.9+**
- Git
- (Optional) VS Code

---

## How to Run the Project Locally

### 1️⃣ Clone the repository

git clone https://github.com/Odessa-HarishK/QUANTECH.git

### 2️⃣ Create and activate a virtual environment

python -m venv env
env\Scripts\activate

### 3️⃣ Install dependencies

pip install --force-reinstall --no-cache-dir \
  --trusted-host pypi.org \
  --trusted-host files.pythonhosted.org \
  -r requirements.txt
### 4️⃣ Prepare local folder for Integration documents

QUANTECH/
    data/ # Integration documents (HLDs, mappings, samples)
    
### 5️⃣ Run vector store

python vector_store.py

### 6️⃣ Run the application

streamlit run app.py
