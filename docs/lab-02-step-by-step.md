# Lab 02: RAG Pipeline with FastAPI — Step-by-Step Guide

**Prerequisite:** Complete **lab-01** first. You should have a working RAG pipeline (ingestion, retrieval, generation) that runs as a CLI.

This lab adds a **FastAPI** server so the same pipeline is exposed over HTTP via **POST /ask**. You keep the existing CLI and gain an API that other clients (e.g. lab-03 Streamlit) can call.

---

## Prerequisites

- **Lab-01 completed** — Working RAG CLI, `.env` with `GOOGLE_API_KEY`, and data in `data/`.
- **Python 3.10+** and your existing Gemini API key.

---

## Phase 1: Add dependencies and the API file

Start from your lab-01 project (or a copy of it as `lab-02`). Reuse the same `.env`, `data/`, `ingestion.py`, `retrieval.py`, and `app.py`.

**1. Add FastAPI and uvicorn** to `requirements.txt`:

```text
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
```

Then install (with your venv activated):

```bash
pip install -r requirements.txt
```

**2. One small change in `app.py` (if needed):** Your `generate_answer` must accept an optional Gemini client so the API can pass its own. Use a signature like:

`generate_answer(query, retrieved_chunks, genai_client=None)` and inside use `client_to_use = genai_client or client`. If your lab-01 already has this, leave it as is.

**3. Create the new file `api.py`** — this is the only new code for lab-02. It will use your existing `run_ingestion`, `retrieve`, and `generate_answer`.

---

## Phase 2: Implement the API layer

Create **`api.py`** in the project root. It loads the index at startup (lifespan), then serves **POST /ask** by calling your existing retrieval and generation.

**Full `api.py`** (including imports):

```python
"""FastAPI app exposing the RAG pipeline via /ask."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel

from app import generate_answer
from ingestion import run_ingestion
from retrieval import retrieve

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load index and chunks at startup."""
    print("🔄 Ingesting documents...")
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    all_chunks, index = run_ingestion("data", client)
    app.state.client = client
    app.state.all_chunks = all_chunks
    app.state.index = index
    print("✅ RAG index ready.")
    yield


app = FastAPI(title="RAG API", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """Run RAG: retrieve relevant chunks and generate an answer."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must be non-empty")

    client = app.state.client
    index = app.state.index
    all_chunks = app.state.all_chunks

    retrieved = retrieve(question, index, all_chunks, client)
    answer = generate_answer(question, retrieved, client)
    return AskResponse(answer=answer)
```

**What this does:**

- **Imports** — FastAPI, lifespan, Pydantic for request/response, and your existing `generate_answer`, `run_ingestion`, `retrieve`.
- **Lifespan** — On server start: create the Gemini client, run ingestion once, store `client`, `all_chunks`, and `index` on `app.state` so every request can use them.
- **POST /ask** — Accepts `{"question": "..."}`; validates non-empty; runs retrieve → generate_answer; returns `{"answer": "..."}`. Empty questions return 400.

No changes are needed in `ingestion.py` or `retrieval.py`; they are reused as in lab-01.

---

## Phase 3: Run and test

You can run the pipeline in two ways: **CLI** (unchanged from lab-01) or **API** (new).

### 3.1 Run the CLI

From the project directory (venv activated):

```bash
python app.py
```

You should see:

```text
🔄 Ingesting documents...
✅ Ready. Ask your question.

Ask (type 'exit' to quit):
```

Type questions and press Enter; type `exit` to quit.

### 3.2 Run the API

Start the FastAPI server:

```bash
uvicorn api:app --reload
```

- **Interactive API docs:** http://127.0.0.1:8000/docs  
- **POST /ask:** Send a JSON body with `question` and receive `answer`.

Example with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is covered on Day 1?"}'
```

Response:

```json
{"answer": "..."}
```

Keep the API running if you want to use **lab-03** (Streamlit chatbot), which calls this endpoint.

---

## Summary

| Phase | What you did |
|-------|----------------|
| **1** | Add FastAPI and uvicorn to `requirements.txt`; ensure `generate_answer` accepts optional `genai_client`; create `api.py` |
| **2** | Implement `api.py` with imports, lifespan (ingestion at startup), and **POST /ask** using existing retrieval and generation |
| **3** | Run **CLI:** `python app.py` — or **API:** `uvicorn api:app --reload` and call **POST /ask** (e.g. http://127.0.0.1:8000/docs) |

You now have the same RAG pipeline available from the command line and over HTTP. For the Streamlit chatbot that calls this API, see **`docs/lab-03-step-by-step.md`**.
