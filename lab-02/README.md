# Lab 02 — RAG pipeline

A small RAG (Retrieval-Augmented Generation) pipeline: ingest text documents, embed and index them with FAISS, then answer questions using retrieved chunks and Gemini.

## Prerequisites

- Python 3.10+
- A [Google AI API key](https://aistudio.google.com/apikey) (Gemini)

## Setup

1. **Create and activate a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   # or: venv\Scripts\activate   # Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API key.** Create a `.env` file in the `lab-02` folder:

   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

4. **Add documents.** Put `.txt` files in a `data/` folder next to the scripts. The pipeline loads all `.txt` files from `data/`, chunks them, embeds with Gemini, and builds a FAISS index.

## How to run

### CLI (interactive)

Run the app and type questions at the prompt:

```bash
python app.py
```

On first run it ingests from `data/`, then prompts you. Type your question and press Enter; type `exit` to quit.

### API (FastAPI)

Start the server:

```bash
uvicorn api:app --reload
```

- **Docs:** http://127.0.0.1:8000/docs  
- **Ask a question:** `POST /ask` with JSON body:

  ```bash
  curl -X POST http://127.0.0.1:8000/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "Your question here"}'
  ```

  Response: `{"answer": "..."}`.

Ingestion runs once at startup when you start the API server.
