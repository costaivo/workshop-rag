# Phase 4: The RAG Service

[← Back to main guide](rag-setup.md)

This phase builds the logic that answers questions by retrieving context and generating responses.

---

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

**Previous:** [Phase 3: The Ingestion Pipeline](phase-3-ingestion.md) · **Next:** [Phase 5: The API](phase-5-api.md)
