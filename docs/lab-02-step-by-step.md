# Lab 02: RAG Pipeline with FastAPI — Step-by-Step Guide

This guide walks you through **lab-02**: the same RAG pipeline as lab-01 (ingestion, retrieval, generation) plus a **FastAPI** server that exposes it via a **POST /ask** endpoint. You can run the pipeline as a **CLI** (interactive loop) or as an **API** (HTTP) and connect other clients to it.

The flow is: **project setup → configuration → data → ingestion → retrieval → generation → API layer → run and test**. The ingestion and retrieval logic is shared with lab-01; this document focuses on what lab-02 adds and how to run both modes.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed.
- A **Google AI (Gemini) API key**. Create one at [Google AI Studio](https://aistudio.google.com/apikey).

---

## Phase 1: Project Setup

Create the project directory, virtual environment, and install dependencies.

### 1.1 Create the project directory

Use the existing `lab-02` folder or create one:

```bash
mkdir lab-02
cd lab-02
```

### 1.2 Set up a virtual environment

```bash
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 1.3 Dependencies

Create a `requirements.txt` with the following (as in `lab-02/requirements.txt`):

```text
# RAG pipeline dependencies
numpy>=1.24.0
faiss-cpu>=1.7.0
python-dotenv>=1.0.0
google-genai>=1.0.0

# API
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
```

- **numpy**, **faiss-cpu**, **python-dotenv**, **google-genai** — Same as lab-01 (RAG pipeline).
- **fastapi** — Web framework for the `/ask` API.
- **uvicorn** — ASGI server to run the FastAPI app.

Install them:

```bash
pip install -r requirements.txt
```

### 1.4 Project structure

Your folder should look like this:

```text
lab-02/
├── data/                 # Place your .txt documents here
│   └── *.txt
├── ingestion.py          # Load, chunk, embed, build index (same as lab-01)
├── retrieval.py          # Embed query, search index, return chunks (same as lab-01)
├── app.py                # CLI: ingest → query loop → generate (also defines generate_answer)
├── api.py                # FastAPI app: lifespan ingestion + POST /ask
├── requirements.txt
└── .env                  # GOOGLE_API_KEY (create in Phase 2)
```

---

## Phase 2: Configuration

Same as lab-01: configure the Gemini API key.

### 2.1 Environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_here
```

### 2.2 Loading the key

Both `app.py` (CLI) and `api.py` (API) load the key:

- **app.py** — Loads at import time and creates the Gemini client for the interactive loop.
- **api.py** — Loads in the module and creates the client inside the **lifespan** when the API starts (see Phase 6).

---

## Phase 3: Data

Place the documents you want the RAG system to answer from in the **`data/`** folder. The pipeline reads all **`.txt`** files in that folder. You can use the same data as in lab-01 (e.g. `workshop-schedule.txt`, other `.txt` files).

---

## Phase 4: Ingestion and Phase 5: Retrieval

Lab-02 uses the **same** `ingestion.py` and `retrieval.py` as lab-01:

- **Ingestion:** `load_text_files` → `chunk_text` → `embed_texts` (Gemini) → `create_faiss_index` → `run_ingestion(folder_path, client)` returns `(all_chunks, index)`.
- **Retrieval:** `retrieve(query, index, chunks, client, top_k=3)` embeds the query, searches the FAISS index, and returns the top-K chunk strings.

For a full walkthrough of each function, see **`docs/lab-01-step-by-step.md`** (Phases 4 and 5).

---

## Phase 6: Generation and API Layer

Lab-02 adds two ways to use the pipeline: **CLI** (`app.py`) and **API** (`api.py`). Both reuse the same generation logic.

### 6.1 Generate answer (app.py)

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

### 6.2 CLI main program (app.py)

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

### 6.3 FastAPI app and lifespan (api.py)

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

## Phase 7: Run and Test

You can run lab-02 in two ways: **CLI** or **API**.

### 7.1 Run the CLI

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

### 7.2 Run the API

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
| **1** | Project directory, venv, `requirements.txt` (including FastAPI and uvicorn) |
| **2** | `.env` with `GOOGLE_API_KEY` |
| **3** | `.txt` documents in `data/` |
| **4–5** | Same ingestion and retrieval as lab-01 (`ingestion.py`, `retrieval.py`) |
| **6** | Generation in `app.py` (with optional client); CLI loop in `app.py`; FastAPI app in `api.py` with lifespan and **POST /ask** |
| **7** | Run **CLI:** `python app.py` — or **API:** `uvicorn api:app --reload` and call **POST /ask** |

You now have a RAG pipeline that can be used from the command line or over HTTP. For the Streamlit chatbot that talks to this API, see **`docs/lab-03-step-by-step.md`**.
