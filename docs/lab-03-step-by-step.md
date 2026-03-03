# Lab 03: RAG Chatbot (Streamlit) — Step-by-Step Guide

This guide walks you through **lab-03**: a **Streamlit** chatbot that sends user questions to the **lab-02** RAG API (**POST /ask**) and displays the answers in a chat interface. No RAG logic lives in lab-03 — it is a thin client that connects to the API you built in lab-02.

The flow is: **prerequisites (lab-02 API running) → project setup → understand the app → run and test**.

---

## Prerequisites

Before starting lab-03, ensure:

- **Lab-02** is set up and the **RAG API** can be started (see **`docs/lab-02-step-by-step.md`**).
- The **lab-02 API** is **running** when you use the chatbot. Start it in a separate terminal:

  ```bash
  cd lab-02
  uvicorn api:app --reload
  ```

  The chatbot expects the API at **http://127.0.0.1:8000** by default. You can change this with the **`RAG_API_URL`** environment variable (see Phase 3).

---

## Phase 1: Project Setup

Create the lab-03 directory, virtual environment, and install dependencies.

### 1.1 Create the project directory

Use the existing `lab-03` folder or create one:

```bash
mkdir lab-03
cd lab-03
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

Create a `requirements.txt` with the following (as in `lab-03/requirements.txt`):

```text
streamlit>=1.40.0
requests>=2.32.0
```

- **streamlit** — Builds the chat UI (messages, input, session state).
- **requests** — HTTP client to call the lab-02 **POST /ask** endpoint.

Install them:

```bash
pip install -r requirements.txt
```

### 1.4 Project structure

Your folder should look like this:

```text
lab-03/
├── app.py                # Streamlit chatbot (single file)
├── requirements.txt
└── README.md             # Quick run instructions
```

---

## Phase 2: How the Chatbot Works

The app is a single Streamlit script that:

1. **Configures the API URL** — Uses `RAG_API_URL` from the environment, or defaults to `http://127.0.0.1:8000`. The request goes to `{API_URL}/ask`.
2. **Calls the RAG API** — For each user message, sends **POST /ask** with `{"question": "..."}` and reads **`answer`** from the JSON response.
3. **Keeps chat history** — Uses `st.session_state.messages` to show previous user and assistant messages.
4. **Handles errors** — If the request fails (e.g. API not running), shows a short error and suggests starting the lab-02 API.

### 2.1 API URL and request helper

```python
API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8000")
ASK_URL = f"{API_URL.rstrip('/')}/ask"

def ask_api(question: str) -> str | None:
    """Call the RAG /ask endpoint. Returns answer or None on error."""
    try:
        r = requests.post(
            ASK_URL,
            json={"question": question},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["answer"]
    except requests.exceptions.RequestException as e:
        return None
```

- **Success:** Returns the answer string from the API.
- **Failure:** Returns `None` (connection error, timeout, or non-2xx response).

### 2.2 Page config and chat state

- **Page:** Title “RAG Chatbot”, caption shows the current `ASK_URL` and mentions `RAG_API_URL`.
- **Session state:** `st.session_state.messages` is a list of `{"role": "user"|"assistant", "content": "..."}`. It is initialized once and appended to on each turn.

### 2.3 Rendering and input

- **History:** Loop over `messages` and render each with `st.chat_message(role)` and `st.markdown(content)`.
- **Input:** `st.chat_input("Ask a question...")`. When the user sends a message:
  - Append it to `messages` with role `"user"` and display it.
  - Call `ask_api(prompt)` in an assistant bubble with `st.spinner("Thinking...")`.
  - If the result is not `None`, show the answer and append it to `messages` as `"assistant"`.
  - If the result is `None`, show an error (e.g. “Could not reach the RAG API…”) and append that as the assistant message so the user knows to start lab-02.

---

## Phase 3: Run and Test

### 3.1 Start the lab-02 API (if not already running)

In one terminal:

```bash
cd lab-02
uvicorn api:app --reload
```

Leave it running.

### 3.2 Start the chatbot

In another terminal, from the repo root or from `lab-03`:

```bash
cd lab-03
streamlit run app.py
```

Your browser should open the Streamlit app. You should see the title “RAG Chatbot” and the caption with the API URL.

### 3.3 Use the chat

- Type a question in the input box and press Enter.
- The app sends **POST /ask** to the lab-02 API and displays the returned answer.
- Ask follow-up questions; the conversation history is shown above the input.

### 3.4 Using a different API URL

If the RAG API runs on another host or port:

```bash
export RAG_API_URL=http://localhost:8000   # or your API base URL
streamlit run app.py
```

The caption in the app shows the URL in use.

### 3.5 If the API is not reachable

If you see an error like “Could not reach the RAG API”, check:

- The lab-02 server is running (`uvicorn api:app --reload` in `lab-02`).
- The URL is correct (default `http://127.0.0.1:8000`; override with `RAG_API_URL` if needed).

---

## Summary

| Phase | What you did |
|-------|----------------|
| **1** | Project directory, venv, `requirements.txt` (Streamlit, requests) |
| **2** | Understood the app: API URL, `ask_api`, session state, chat UI, error handling |
| **3** | Started lab-02 API, ran `streamlit run app.py`, tested the chat and optional `RAG_API_URL` |

You now have a browser-based RAG chatbot that uses the lab-02 API for every answer. For full lab-02 setup and API details, see **`docs/lab-02-step-by-step.md`**.
