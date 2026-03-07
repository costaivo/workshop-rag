# Lab 02: RAG Pipeline with FastAPI — Step-by-Step Guide

**Prerequisite:** Complete **lab-01** first. You should have a working RAG pipeline (ingestion, retrieval, generation) that runs as a CLI.

This guide adds a **FastAPI** server that exposes the same pipeline via **POST /ask**. You can then run the pipeline as a **CLI** (interactive loop) or as an **API** (HTTP) and connect other clients (e.g. lab-03 Streamlit) to it.

---

## Prerequisites

- **Lab-01 completed** — Working RAG CLI, `.env` with `GOOGLE_API_KEY`, and data in `data/`.
- **Python 3.10+** and your existing **Google AI (Gemini) API key**.

---

## Phase 1: Start from lab-01

Use your existing lab-01 project as the base. Either work in a **lab-02** copy of it or add the following to your lab-01 folder.

### 1.1 Project directory

If you prefer a separate lab-02 folder, copy your lab-01 directory (including `data/`, `ingestion.py`, `retrieval.py`, `app.py`, `.env`) to `lab-02` and work there. Otherwise, continue in lab-01.

### 1.2 Dependencies

Add FastAPI and uvicorn to your `requirements.txt`:

```text
# RAG pipeline dependencies (same as lab-01)
numpy>=1.24.0
faiss-cpu>=1.7.0
python-dotenv>=1.0.0
google-genai>=1.0.0

# API (lab-02)
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
```

Install the new packages (with your venv activated):

```bash
pip install -r requirements.txt
```

### 1.3 New file: api.py

You will add **`api.py`** — the FastAPI app with lifespan and **POST /ask**. The rest of the structure stays as in lab-01: `data/`, `ingestion.py`, `retrieval.py`, `app.py`, `.env`.

---

## Phase 2: Configuration and data

- **Configuration** — Reuse your existing `.env` with `GOOGLE_API_KEY`. Both `app.py` (CLI) and `api.py` (API) load it; the API creates the Gemini client in its **lifespan** (Phase 4).
- **Data** — Use the same **`data/`** folder and `.txt` files as in lab-01.

---

## Phase 3: Ingestion and retrieval

Lab-02 uses the **same** `ingestion.py` and `retrieval.py` as lab-01. No code changes are required there. For a full walkthrough of ingestion and retrieval, see **`docs/lab-01-step-by-step.md`**.

---

## Phase 4: Generation and API layer

Lab-02 adds two ways to use the pipeline: **CLI** (`app.py`) and **API** (`api.py`). Both reuse the same generation logic.

### 4.1 Generate answer (app.py)

**Purpose:** Have the LLM answer using **only** the retrieved chunks. The function accepts an optional Gemini client so the API can pass its own client.

```python
def generate_answer(query, retrieved_chunks, genai_client=None):
    client_to_use = genai_client or client
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
    Answer the question using ONLY the context below.

    Context:
    {context}

    Question:
    {query}
    """

    response = client_to_use.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
```

- **CLI:** Calls `generate_answer(query, retrieved, client)`.
- **API:** Calls `generate_answer(question, retrieved, client)` with the client stored in `app.state`.

### 4.2 CLI main program (app.py)

Same as lab-01: ingest once, then loop — read question, retrieve, generate, print. Exit with `exit`.

```python
if __name__ == "__main__":
    print("🔄 Ingesting documents...")
    all_chunks, index = run_ingestion("data", client)
    print("✅ Ready. Ask your question.")

    while True:
        query = input("\nAsk (type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        retrieved = retrieve(query, index, all_chunks, client)
        answer = generate_answer(query, retrieved, client)
        print("\nAnswer:\n")
        print(answer)
```

### 4.3 FastAPI app and lifespan (api.py)

**Purpose:** Run ingestion **once** when the API server starts, store the client, chunks, and index in `app.state`, and expose **POST /ask**.

**Lifespan:** On startup, create the Gemini client, run `run_ingestion("data", client)`, and attach the results to the FastAPI app so every request can use them.

```python
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
```

**App and route:**

- **Request body:** `{"question": "Your question here"}` (Pydantic model `AskRequest`).
- **Response:** `{"answer": "..."}` (Pydantic model `AskResponse`).
- Empty or whitespace-only questions return **400** with a detail message.

```python
app = FastAPI(title="RAG API", lifespan=lifespan)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
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

---

## Phase 5: Run and test

You can run lab-02 in two ways: **CLI** or **API**.

### 5.1 Run the CLI

From the `lab-02` directory with the virtual environment activated:

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

### 5.2 Run the API

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
| **1** | Start from lab-01; add FastAPI and uvicorn to `requirements.txt`; plan to add `api.py` |
| **2** | Reuse `.env` and `data/` from lab-01 |
| **3** | Same ingestion and retrieval as lab-01 (no changes) |
| **4** | Generation in `app.py` (optional client); CLI loop in `app.py`; FastAPI app in `api.py` with lifespan and **POST /ask** |
| **5** | Run **CLI:** `python app.py` — or **API:** `uvicorn api:app --reload` and call **POST /ask** |

You now have a RAG pipeline that can be used from the command line or over HTTP. For the Streamlit chatbot that talks to this API, see **`docs/lab-03-step-by-step.md`**.
