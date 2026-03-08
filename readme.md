# RAG Labs

Hands-on labs for building **Retrieval-Augmented Generation (RAG)** systems. 
You learn by following step-by-step guides and running the code. 
Each lab builds on the previous one: 
- a basic RAG pipeline (CLI), 
- then a FastAPI service, 
- then a Streamlit chatbot that talks to the API.

**Completed code** for each lab lives in the **`lab-0X`** folders (`lab-01`, `lab-02`, `lab-03`). Use the docs to understand and recreate the flow; use the lab folders as reference or to run the working implementation.

---

## What is RAG?

**RAG** = **R**etrieval **A**ugmented **G**eneration: you **retrieve** relevant chunks from your documents, **augment** the user’s question with that context, and let an LLM **generate** an answer. The model answers from *your* data instead of only its training data.

- **[What is RAG? (Simplified)](docs/rag-simplified.md)** — Short, non-technical overview (no code).
- **[RAG Tutorial: Basic Pipeline](docs/rag-tutorial-basic.md)** — High-level blocks, process flow, and detailed steps with code references.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Lab 01](docs/lab-01-step-by-step.md) | Build a full RAG system: setup, ingestion (chunk + embed + FAISS), retrieval, generation, and a CLI question-answering loop. Code in `lab-01/`. |
| [Lab 02](docs/lab-02-step-by-step.md) | Same RAG pipeline plus a **FastAPI** server with a **POST /ask** endpoint. Run as CLI or API. Code in `lab-02/`. |
| [Lab 03](docs/lab-03-step-by-step.md) | **Streamlit** chatbot that calls the lab-02 API. Thin client; no RAG logic here. Code in `lab-03/`. |

---

## Quick start

1. **Prerequisites:** Python 3.10+ and a [Google AI (Gemini) API key](https://aistudio.google.com/apikey).
2. Pick a lab (e.g. `lab-01`), follow its step-by-step guide in `docs/`, or run the existing code in the corresponding `lab-0X` folder.
3. Put your `.txt` documents in that lab’s `data/` folder (for labs that use local files), set your API key in `.env`, then run ingestion and the app as described in the doc.

For the first-time RAG flow, start with [Lab 01](docs/lab-01-step-by-step.md) and the [simplified RAG overview](docs/rag-simplified.md).

---

## Student feedback

After completing the labs, please share your feedback via this form: **[Code to Career – Student responses](https://forms.gle/9xwsrGPbPmkWr7ea7)**.
