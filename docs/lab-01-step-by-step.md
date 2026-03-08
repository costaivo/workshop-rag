# RAG Project: Step-by-Step Setup

This guide walks you through building a complete **Retrieval-Augmented Generation (RAG)** system using the code in this project. You will set up the environment, ingest documents into a search index, and run a question-answering loop that uses only your documents as context.

The flow follows the same structure as the archived RAG workshop: **project setup → configuration → ingestion → retrieval → generation → run and test**. All code below is taken from the current `lab-01` project.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed.
- A **Google AI (Gemini) API key**. You can create one at [Google AI Studio](https://aistudio.google.com/apikey).

---

## Phase 1: Project Setup

Create the project directory, virtual environment, and install dependencies.

### 1.1 Create the project directory

create a new folder:

```bash
mkdir rag-lab
cd rag-lab
```

### 1.2 Set up a virtual environment

Isolate dependencies to avoid conflicts with other projects.

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 1.3 Dependencies

Create a `requirements.txt` file with the following (as in `lab-01/requirements.txt`):

```text
# RAG pipeline dependencies
numpy>=1.24.0
faiss-cpu>=1.7.0
python-dotenv>=1.0.0
google-genai>=1.0.0
```

- **numpy** — Used for embedding arrays and FAISS.
- **faiss-cpu** — Builds and queries the vector index (CPU-only).
- **python-dotenv** — Loads the API key from a `.env` file.
- **google-genai** — Google’s Gemini client for embeddings and generation.

Install them:

```bash
pip install -r requirements.txt
```

### 1.4 Project structure

Your folder can look like this (matching `lab-01`):

```text
lab-01/
├── data/                 # Place your .txt documents here
│   ├── workshop-schedule.txt
│   └── ivo-biography.txt
├── ingestion.py          # Load, chunk, embed, build index
├── retrieval.py          # Embed query, search index, return chunks
├── generation.py         # Build prompt from chunks, call LLM for answer
├── app.py                # Main script: ingest → query loop → generate
├── requirements.txt
└── .env                  # GOOGLE_API_KEY (create in Phase 2)
```

---

## Phase 2: Configuration

Configure the API key so the pipeline can call Gemini for embeddings and generation.

### 2.1 Environment variables

Create a `.env` file in the project root (do not commit it to version control):

```env
GOOGLE_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual Gemini API key.

### 2.2 Loading the key in the app

The main app (`app.py`) loads the key at startup using `python-dotenv` and passes the client to ingestion and retrieval:

```python
import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
```

You will use this `client` for both embedding (ingestion and retrieval) and generation.

---

## Phase 3: Data

Place the documents you want the RAG system to answer from in the `data/` folder. The pipeline reads all **`.txt`** files in that folder.

**Example:** `data/workshop-schedule.txt` — a multi-day workshop schedule (e.g. React, topics, timings):

```text
📅 4‑Day Workshop Schedule

Day 1 — Introduction to React & Component-Based Development
9:45 – 10:15 — Inauguration
10:30 – 12:00 — Introduction & Setup
Topics: Overview of React & why it's used, Component‑based architecture...
```

**Example:** [`data/workshop_speakers.txt`](https://github.com/costaivo/workshop-rag/blob/main/lab-01/data/workshop_speakers.txt) — a multi-day workshop schedule (e.g. React, topics, timings):
```text
📅 4‑Day Workshop Schedule 

Day 1 — Introduction to React & Component-Based Development
Speaker: Joshua Pereira , Nikesh Singh
10:30 – 12:00 — Introduction & Setup
12:00 – 12:40 — React Basics
```

**Example:** `data/ivo-biography.txt` — a biography or any other `.txt` file.
```text
# Ivo Costa - Professional Biography
Linkedin Profile : https://www.linkedin.com/in/ivo-costa/

## Overview
Ivo Costa is the **Director of Development Services at Creative Capsule**, based in South Goa, India.
```

You can add as many `.txt` files as you like; the ingestion step will load and index all of them.

> **NOTE:** The contents for the file can be found at location [Lab-01](https://github.com/costaivo/workshop-rag/tree/main/lab-01/data)

---

## Phase 4: The Ingestion Pipeline

Ingestion runs **once** (at startup in this project). It loads documents, splits them into chunks, turns each chunk into an embedding, and builds a FAISS index. All of this is in `ingestion.py`.

### 4.1 Load text files

**Purpose:** Read every `.txt` file in a folder and return a list of document strings so they can be chunked and embedded.

```python
import os
import numpy as np
import faiss

def load_text_files(folder_path):
    """Read all .txt files in folder; return list of document strings."""
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                documents.append(f.read())
    return documents
```

- Scans `folder_path` for filenames ending in `.txt`.
- Reads each file as UTF-8 and appends its full text to a list.
- Returns a list of strings (one per file). No chunking or embedding yet.

### 4.2 Chunk text

**Purpose:** Split long documents into smaller segments so that each piece fits embedding limits and retrieval returns focused passages. Overlap helps avoid cutting sentences in the middle.

```python
def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
```

- Slides a window of `chunk_size` characters (default 500) over the text.
- Advances by `chunk_size - overlap` (default 400), so consecutive chunks overlap by 100 characters.
- Returns a list of chunk strings.

### 4.3 Embed texts

**Purpose:** Turn each chunk into a fixed-size vector (embedding) using Gemini so that similar meaning gets similar vectors and FAISS can do similarity search.

```python
def embed_texts(texts, client):
    """Turn chunk strings into vectors using the Gemini embedding API."""
    embeddings = []
    for text in texts:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=[{"text": text}],
        )
        embeddings.append(response.embeddings[0].values)
    return np.array(embeddings).astype("float32")
```

- For each chunk, calls the Gemini API with `gemini-embedding-001`.
- Collects embedding vectors into a NumPy array and casts to `float32` for FAISS.

### 4.4 Create FAISS index

**Purpose:** Build a search structure so that, given a query vector, you can quickly find the K nearest chunk vectors (by L2 distance).

```python
def create_faiss_index(embeddings):
    """Build a FAISS L2 index from embedding vectors."""
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index
```

- Uses the embedding dimension from `embeddings.shape[1]`.
- Creates an L2 (Euclidean) index and adds all chunk embeddings. Smaller L2 distance means more similar.

### 4.5 Run the full ingestion

**Purpose:** Tie loading, chunking, embedding, and indexing into one function used at startup.

```python
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
```

- Loads all `.txt` from `folder_path`, chunks every document, embeds all chunks, builds the FAISS index.
- Returns `(all_chunks, index)` so the main app can pass them to retrieval.

---

## Phase 5: Retrieval

Retrieval runs **for each question**. It embeds the query, searches the FAISS index, and returns the top-K chunk strings. This is in `retrieval.py`.

### 5.1 Retrieve top-K chunks

**Purpose:** For a user question, get the K chunks whose embeddings are closest to the question’s embedding.

```python
import numpy as np

def retrieve(query, index, chunks, client, top_k=3):
    """
    Find the chunks most similar to the query.
    Returns a list of chunk strings (length top_k).
    """
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[{"text": query}],
    )
    query_embedding = response.embeddings[0].values
    query_vector = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_vector, top_k)
    return [chunks[i] for i in indices[0]]
```

- Embeds the query with the same model as the chunks.
- Converts the embedding to a single-row `float32` vector.
- Calls `index.search(query_vector, top_k)` to get indices of the nearest chunks.
- Returns the corresponding chunk strings from the `chunks` list.

---

## Phase 6: Generation and Main App

Generation lives in **`generation.py`**: it builds a prompt from the retrieved chunks and calls the LLM. The main script (**`app.py`**) loads the API key, runs ingestion once, then enters a loop: ask a question → retrieve chunks → generate an answer → print the answer.

### 6.1 Generate answer (generation.py)

**Purpose:** Have the LLM answer the question using **only** the retrieved chunks as context, to keep answers grounded in your documents. The function takes the Gemini `client` as an argument so the module stays independent of configuration.

```python
def generate_answer(query, retrieved_chunks, client):
    """
    Answer the question using only the retrieved chunks as context.
    """
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
    Answer the question using ONLY the context below.

    Context:
    {context}

    Question:
    {query}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
```

- Joins the retrieved chunks into one `context` string.
- Builds a prompt that instructs the model to use only that context.
- Takes `client` so the caller (e.g. `app.py`) passes the configured Gemini client.
- Calls Gemini with `gemini-2.5-flash` and returns the generated text.

### 6.2 Main program (app.py)

**Purpose:** Wire ingestion, retrieval, and generation into a single run: ingest once, then answer questions until the user types `exit`. The app imports `generate_answer` from `generation` and passes `client` on each call.

```python
import os
from dotenv import load_dotenv
from google import genai

from generation import generate_answer
from ingestion import run_ingestion
from retrieval import retrieve

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# -------- MAIN --------
if __name__ == "__main__":

    print("🔄 Ingesting documents...")
    all_chunks, index = run_ingestion("data", client)
    print("✅ Ingestion complete.")
    print("--------------------------------")
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

- Imports `generate_answer` from `generation`, plus `run_ingestion` and `retrieve`.
- Runs `run_ingestion("data", client)` so `data/` is loaded, chunked, embedded, and indexed.
- In a loop: read a question, retrieve top-K chunks, call `generate_answer(query, retrieved, client)`, print the answer.
- Exits when the user types `exit`.

---

## Phase 7: Run and Test

### 7.1 Run the pipeline

From the project root (e.g. `lab-01/`), with the virtual environment activated:

```bash
python app.py
```

You should see:

```text
🔄 Ingesting documents...
✅ Ingestion complete.
--------------------------------
✅ Ready. Ask your question.

Ask (type 'exit' to quit):
```

### 7.2 Example questions

Try questions that match your documents, for example:

- **If you have `workshop-schedule.txt`:**  
  *“What is covered on Day 1?”* or *“When is the tea break?”* or *“What topics are in the React workshop?”*
- **If you have `ivo-biography.txt`:**  
  *“What is Ivo’s role at Creative Capsule?”* or *“Where is he based?”*

The system will retrieve the relevant chunks and answer using only that context. Type `exit` to quit.

---

## Summary

| Phase | What you did |
|-------|----------------|
| **1** | Project directory, virtual environment, `requirements.txt` |
| **2** | `.env` with `GOOGLE_API_KEY`, client in `app.py` |
| **3** | `.txt` documents in `data/` |
| **4** | Ingestion: load → chunk → embed → FAISS index (`ingestion.py`) |
| **5** | Retrieval: embed query → search index → top-K chunks (`retrieval.py`) |
| **6** | Generation: prompt with context + question → LLM → answer (`generation.py`); main loop in `app.py` |
| **7** | Run `python app.py` and ask questions |

You now have a working RAG pipeline: **documents → one-time ingestion → per-question retrieval → generation from context.** For a higher-level explanation of RAG, see `lab-01/rag-simplified.md`. For more detail on each code block and data flow, see `lab-01/rag-tutorial-basic.md`.
