# Phase 3: The Ingestion Pipeline

[← Back to main guide](rag-setup.md)

This phase converts your documents into searchable vectors.

---

### 8. Document Loader & Chunker (`app/services/text_processing.py`)
Create a utility to read files and split them into smaller pieces.
*   **Why chunk?** LLMs have limited context windows, and smaller chunks improve retrieval accuracy.

```python
import os

def load_text_documents(directory: str):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            path = os.path.join(directory, filename)
            with open(path, "r", encoding="utf-8") as f:
                documents.append({"text": f.read(), "source": filename})
    return documents

def split_text(text: str, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
```

### 9. Vector Store (`app/services/vector_store.py`)
Implement FAISS to store and search embeddings. We need methods to save and load the index.

```python
import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, index_path, meta_path):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = faiss.IndexFlatL2(768) # 768 is Gemini's embedding dimension
        self.metadata = []

    def add_texts(self, texts, metadatas, embeddings):
        self.index.add(np.array(embeddings))
        self.metadata.extend(metadatas)

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            return True
        return False

    def search(self, query_embedding, k=3):
        distances, indices = self.index.search(np.array([query_embedding]), k)
        results = []
        for j, i in enumerate(indices[0]):
            if i != -1:  # -1 means no match found
                results.append((self.metadata[i], distances[0][j]))
        return results
```

### 10. Ingestion Script (`scripts/ingest.py`)
Write a script that ties it all together:
1.  Load all `.txt` files from `data/documents/`.
2.  Chunk the text.
3.  Generate embeddings using `get_embedding`.
4.  Add to `VectorStore`.
5.  Save the index to disk.

**Create `scripts/ingest.py`:**
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.llm import get_embedding
from app.services.text_processing import load_text_documents, split_text
from app.services.vector_store import VectorStore

def main():
    # 1. Load Documents
    print("Loading documents...")
    docs = load_text_documents("data/documents")
    
    # 2. Chunk Text
    all_chunks = []
    all_metadatas = []
    
    print("Chunking text...")
    for doc in docs:
        chunks = split_text(doc["text"])
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"text": chunk, "source": doc["source"]})

    # 3. Generate Embeddings
    print(f"Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = [get_embedding(chunk) for chunk in all_chunks]

    # 4. Store in Vector DB
    print("Saving to Vector Store...")
    os.makedirs(os.path.dirname(settings.VECTOR_STORE_INDEX_PATH), exist_ok=True)
    
    vector_store = VectorStore(settings.VECTOR_STORE_INDEX_PATH, settings.VECTOR_STORE_META_PATH)
    vector_store.add_texts(all_chunks, all_metadatas, embeddings)
    vector_store.save()
    
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
```

**Action:** Run this script now to populate your database!
```bash
python scripts/ingest.py
```

---

**Previous:** [Phase 2: Configuration & Core Components](phase-2-configuration.md) · **Next:** [Phase 4: The RAG Service](phase-4-rag-service.md)
