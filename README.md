# 🦫 Platypus: Semantic Document Search and Indexing Engine

**Platypus** is a modular semantic search system designed to perform deep analysis on documents — currently optimized for Arxiv PDFs. It extracts, embeds, indexes, and enables similarity search using FAISS and Sentence Transformers, backed by MongoDB for document storage.

---

## 🚧 Current Status

> ⚠️ Currently supports **only Arxiv PDFs**. Support for other sources (e.g., Springer, IEEE) is planned for future versions.

---

## ✨ Core Features

### 1. 🧾 PDF Text Extraction

* Uses **PyMuPDF** to extract raw text and structured sections (e.g., abstracts).
* Handles temporary file management safely during extraction.

### 2. 📦 Document Management via MongoDB

* `MongoDBManager` provides seamless interaction with a MongoDB instance.
* Supports insertion and querying of rich document metadata (title, URL, abstract, etc.).
* Organizes documents into collections (e.g., `arxiv-papers`).

### 3. 🧠 Semantic Embedding Generation

* `Embedder`: Loads transformer models (e.g., `all-MiniLM-L6-v2`) to generate dense embeddings.
* `ChunkVectorizer`: Uses LangChain's `RecursiveCharacterTextSplitter` to break long texts into chunks, enabling fine-grained embedding.

### 4. 🔍 FAISS Indexing & Search

* `FAISSIndexer` builds and manages a **FAISS IndexFlatL2** for similarity search.
* Adds chunk embeddings to the index with associated metadata.
* **Persistence**: Index + metadata can be saved to disk and reloaded.
* **Semantic Search**: Natural language queries return top-k most semantically similar document chunks.

### 5. 🤖 Language Model Integration (Foundational)

* The `Infer` module introduces basic interaction with a large language model.
* Currently used for experimental query generation and understanding.
* Lays the groundwork for future AI-augmented querying.

---

## 🧱 Project Structure

```bash
platypus/
├── PDFAnalyzer/        
│   ├── Extractor.py
│   └── Vectorizer.py
├── Database/           
│   ├── Database.py
│   └── Indexer.py
├── LLM/               
│   └── Infer.py
├── Similarity/         
│   └── Similarity.py
├── Utils/              
│   └── Foundation.py
├── Main.py             
└── Environment.yaml    
```

---

## ⚙️ Setup Instructions

### 🧪 Prerequisites

* Python **3.11+**
* `conda`
* A running MongoDB instance (local or remote)

### 🔧 Installation

```bash
git clone https://github.com/yourusername/platypus.git
cd platypus
conda env create -f Environment.yaml
conda activate platypus
python Main.py
```

---

## 📌 Notes

* All vector indexing uses `FAISS IndexFlatL2` (L2 distance).
* Embeddings generated using HuggingFace Sentence Transformers.
* Chunks are associated with metadata (title, arxiv ID, etc.) for contextual search.

---
