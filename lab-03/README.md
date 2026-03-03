# Lab 03 — RAG Chatbot (Streamlit)

A simple Streamlit chatbot that sends your questions to the **lab-02** RAG API and displays the answers.

## Prerequisites

- The **lab-02 API** must be running. From the repo root:

  ```bash
  cd lab-02
  uvicorn api:app --reload
  ```

  Leave it running in one terminal. The chatbot expects the API at `http://127.0.0.1:8000` by default.

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

## Run the chatbot

From the `lab-03` folder:

```bash
streamlit run app.py
```

Your browser will open the chat UI. Type a question and press Enter; the app calls the lab-02 `/ask` endpoint and shows the RAG answer.

### Using a different API URL

If the RAG API runs on another host or port, set the environment variable before starting Streamlit:

```bash
export RAG_API_URL=http://localhost:8000   # or your API base URL
streamlit run app.py
```
