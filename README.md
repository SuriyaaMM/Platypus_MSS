# Platypus: A Semantic Document Search and Indexing Platform for MongoDB

I wrote this to Learn about Retrieval Augmented Generation and Similarity Search.
Initially I though to develop this into an Full Fledged app using streamlit, but then
due to time constraints, I am just converting this into one that supports
FAISS for MongoDB

## **NOTE**:
- Currently it stores only Arxiv Database, which this was made for, in future maybe
we can plan to support multiple databases

## Current Stage Features

At its current stage, Platypus provides the following core functionalities:

1.  **PDF Text Extraction:**
    * Utilizes `PyMuPDF` to extract raw text and specific sections (like abstracts) from PDF documents.
    * Handles temporary file management during extraction.

2.  **Document Management with MongoDB:**
    * `MongoDBManager` facilitates seamless connection to a MongoDB instance.
    * Supports inserting and managing documents (e.g., Arxiv paper metadata) within specified collections.
    * Designed to store and retrieve rich document information.

3.  **Semantic Embedding Generation:**
    * `Embedder` class initializes and manages Sentence Transformer models (e.g., `all-MiniLM-L6-v2`) to convert text into high-dimensional numerical vectors (embeddings).
    * `ChunkVectorizer` handles chunking of longer texts using LangChain's `RecursiveCharacterTextSplitter` and then vectorizes these chunks using the `Embedder`. This allows for fine-grained semantic representation.

4.  **FAISS Indexing and Search:**
    * `FAISSIndexer` builds and manages a FAISS (Facebook AI Similarity Search) index.
    * Efficiently adds document embeddings to a flat L2 index (`IndexFlatL2`).
    * **Persistence:** Supports saving the FAISS index and its corresponding document metadata (Title, URL) to disk, and loading them back for persistent search capabilities without re-indexing.
    * **Semantic Search:** Enables performing semantic similarity searches using natural language queries against the indexed document embeddings, returning the most relevant results based on vector distance.

5.  **Language Model Integration (Basic):**
    * `Infer` class includes a basic setup for interacting with a large language model (LLM) for query generation based on document analysis. This is a foundational element for future AI-powered enhancements.

## Architecture Highlights

The project follows a modular architecture, with clear separation of concerns:

* `platypus/PDFAnalyzer/`: Contains modules for PDF extraction (`Extractor.py`) and text vectorization (`Vectorizer.py`).
* `platypus/Database/`: Manages MongoDB interactions (`Database.py`) and FAISS indexing (`Indexer.py`).
* `platypus/LLM/`: Houses the language model inference capabilities (`Infer.py`).
* `platypus/Utils/`: Provides foundational utilities and configurations (`Foundation.py`).
* `platypus/Similarity/`: Contains components for similarity detection (`Similarity.py`).

## Getting Started (Prerequisites)

To run this project, you will need:

* Python 3.11+ & `conda`
* MongoDB installed and running locally (or access to a remote instance).
* Use `Environment.yaml` to install pre-requisites, git clone and run Main.py