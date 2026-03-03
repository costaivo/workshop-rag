# Phase 2: Configuration & Core Components

[← Back to main guide](rag-setup.md)

This phase configures environment variables and sets up the Gemini client for embeddings and generation.

---

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

**Previous:** [Phase 1: Project Setup](phase-1-project-setup.md) · **Next:** [Phase 3: The Ingestion Pipeline](phase-3-ingestion.md)
