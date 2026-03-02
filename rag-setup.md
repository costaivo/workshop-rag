# Build Your Own RAG System: Step-by-Step Student Guide

This guide will walk you through building a complete Retrieval-Augmented Generation (RAG) system using Python, Google Gemini, and FAISS. By the end, you'll have a working API that can answer questions based on your own documents.

## Prerequisites

Before starting, ensure you have:
*   **Python 3.10+** installed.
*   A **Google Cloud Project** with the Gemini API enabled.
*   An **API Key** for Google Gemini.

---

## Phase 1: Project Setup

### 1. Create the Project Directory
Open your terminal and create a new folder for your project.
```bash
mkdir rag-workshop
cd rag-workshop
```

### 2. Set Up a Virtual Environment
Isolate your dependencies to avoid conflicts.
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Create a `requirements.txt` file with the following libraries:
```text
fastapi
uvicorn
google-generativeai
faiss-cpu
numpy
python-dotenv
pydantic
pypdf
tenacity
```

Install them:
```bash
pip install -r requirements.txt
```

### 4. Project Structure
Create the following folder structure:
```
rag-workshop/
├── app/
│   ├── api/            # API routes
│   ├── core/           # Config and LLM setup
│   ├── services/       # Core logic (RAG, Vector Store)
│   └── utils/          # Helpers
├── data/
│   ├── documents/      # Place your PDFs/TXTs here
│   └── vector_store/   # Where the index will be saved
├── scripts/            # Ingestion scripts
└── .env                # API keys (keep secret!)
```

---

## Phase 2: Configuration & Core Components

### 5. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
RAG_EMBEDDING_MODEL=models/embedding-001
RAG_GENERATION_MODEL=gemini-pro
VECTOR_STORE_INDEX_PATH=data/vector_store/index.faiss
VECTOR_STORE_META_PATH=data/vector_store/index.pkl
```

### 6. Setup Configuration (`app/core/config.py`)
Create a settings class to load your `.env` variables safely.
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    RAG_EMBEDDING_MODEL: str = "models/embedding-001"
    VECTOR_STORE_INDEX_PATH: str = "data/vector_store/index.faiss"
    VECTOR_STORE_META_PATH: str = "data/vector_store/index.pkl"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 7. Initialize Gemini Client (`app/core/llm.py`)
Set up the connection to Google's AI models.
```python
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def get_embedding(text: str):
    return genai.embed_content(
        model=settings.RAG_EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document"
    )['embedding']

generation_model = genai.GenerativeModel('gemini-pro')
```

---

## Phase 3: The Ingestion Pipeline
This phase converts your documents into searchable vectors.

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

## Phase 4: The RAG Service
Now, let's build the logic that answers questions.

### 11. RAG Logic (`app/services/rag_service.py`)
Create the service that coordinates retrieval and generation.

```python
from app.core.llm import get_embedding, generation_model
from app.services.vector_store import VectorStore
from app.core.config import settings

# Initialize store once
vector_store = VectorStore(settings.VECTOR_STORE_INDEX_PATH, settings.VECTOR_STORE_META_PATH)
vector_store.load()

async def query_rag(question: str):
    # 1. Embed Question
    q_embedding = get_embedding(question)
    
    # 2. Retrieve
    results = vector_store.search(q_embedding, k=3)
    
    # 3. Augment
    context_text = "\n\n".join([f"Source ({r[0]['source']}): {r[0]['text']}" for r in results])
    
    prompt = f"""
    You are a helpful assistant. Answer the question using ONLY the context below.
    If the answer is not in the context, say "I don't know".
    
    Context:
    {context_text}
    
    Question: {question}
    """
    
    # 4. Generate
    response = generation_model.generate_content(prompt)
    
    return response.text, [r[0] for r in results]
```

---

## Phase 5: The API
Expose your RAG system to the world.

### 12. Create API Endpoints (`app/api/routes.py`)
Use FastAPI to create a `/ask` endpoint.
```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import query_rag

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QueryRequest):
    answer, sources = await query_rag(request.question)
    return {"answer": answer, "sources": sources}
```

### 13. Main Application Entry (`app/main.py`)
Wire everything together.
```python
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="RAG Workshop API")
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Phase 6: Run & Test

### 14. Start the Server
```bash
uvicorn app.main:app --reload
```

### 15. Test Your API
Open your browser to `http://localhost:8000/docs`.
1.  Click on the **POST /api/ask** endpoint.
2.  Click **Try it out**.
3.  Enter a question related to your documents:
    ```json
    {
      "question": "What is the main topic of the uploaded document?"
    }
    ```
4.  Execute and watch the magic happen!

## Conclusion
You have successfully built a RAG system! You now understand how to:
*   Process and embed unstructured text.
*   Store vectors efficiently.
*   Retrieve context semantically.
*   Generate grounded answers with an LLM.