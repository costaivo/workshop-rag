# Phase 5: The API

[← Back to main guide](rag-setup.md)

This phase exposes your RAG system via a FastAPI web API.

---

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

**Previous:** [Phase 4: The RAG Service](phase-4-rag-service.md) · **Next:** [Phase 6: Run & Test](phase-6-run-and-test.md)
