"""Ingestion pipeline: load documents, chunk, embed, and build the search index."""

import os
import numpy as np
import faiss


def load_text_files(folder_path):
    """Read all .txt files in folder; return list of document strings."""
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            print(f"  - Loading {filename}...")
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                documents.append(f.read())
    return documents


def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    print(f"  - Chunking text of length {len(text)}...")
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def embed_texts(texts, client):
    """Turn chunk strings into vectors using the Gemini embedding API."""
    embeddings = []
    print(f"  - Embedding {len(texts)} texts...")
    for text in texts:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=[{"text": text}],
        )
        embeddings.append(response.embeddings[0].values)
    return np.array(embeddings).astype("float32")


def create_faiss_index(embeddings):
    """Build a FAISS L2 index from embedding vectors."""
    print(f"  - Creating FAISS index with {embeddings.shape[0]} embeddings...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def run_ingestion(folder_path, client):
    """
    Run the full ingestion pipeline: load → chunk → embed → index.
    Returns (all_chunks, index) for use in the query loop.
    """
    documents = load_text_files(folder_path)
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_text(doc))
    embeddings = embed_texts(all_chunks, client)
    index = create_faiss_index(embeddings)
    return all_chunks, index
