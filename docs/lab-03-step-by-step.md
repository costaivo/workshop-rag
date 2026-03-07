# Lab 03: RAG Chatbot (Streamlit) — Step-by-Step Guide

**Prerequisite:** Complete **lab-02** first. You should have the RAG pipeline running as a **CLI** and as a **FastAPI** server (**POST /ask**).

This lab adds a **Streamlit** chatbot in the **same folder as lab-02**. One project then gives you: CLI, API, and a browser-based chat UI that calls the API. No separate lab-03 directory or venv — keep it simple.

---

## Prerequisites

- **Lab-02 completed** — Working RAG API (`uvicorn api:app --reload`).
- When you use the chatbot, the **lab-02 API must be running** in another terminal (same as now).

---

## Phase 1: Add dependencies and the chatbot file

Stay in your **lab-02** directory. Add the UI dependencies and one new file.

### 1.1 Update requirements.txt

Append the following to your existing **`requirements.txt`**:

```text
# Chatbot UI (lab-03)
streamlit>=1.40.0
requests>=2.32.0
```

- **streamlit** — Chat UI (messages, input, session state).
- **requests** — HTTP client to call **POST /ask**.

Install the new packages (venv activated):

```bash
pip install -r requirements.txt
```

### 1.2 New file: chatbot.py

Create **`chatbot.py`** in the lab-02 folder. This is the only new code for lab-03; it will call your existing API.

---

## Phase 2: Build the chatbot

The app is a single Streamlit script that: configures the API URL, calls **POST /ask** for each question, keeps chat history in session state, and shows a clear error if the API is not reachable.

**Full `chatbot.py`** (including imports):

```python
"""Streamlit chatbot that talks to the RAG API (POST /ask)."""

import os
import requests
import streamlit as st

# Default: API running in same project (lab-02)
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
    except requests.exceptions.RequestException:
        return None


st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")
st.title("💬 RAG Chatbot")
st.caption(f"Connected to: `{ASK_URL}` — change via `RAG_API_URL` env var.")

# Chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# New message input
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_api(prompt)
        if answer is not None:
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            err = "Could not reach the RAG API. Start it in another terminal: `uvicorn api:app --reload`"
            st.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})
```

**What this does:**

- **Imports** — `os` for env, `requests` for HTTP, `streamlit` for the UI.
- **API URL** — `RAG_API_URL` from the environment, or default `http://127.0.0.1:8000`. Requests go to `{API_URL}/ask`.
- **`ask_api(question)`** — POSTs `{"question": question}`, returns the answer string or `None` on failure (connection error, timeout, or non-2xx).
- **Page** — Title “RAG Chatbot”, caption shows the URL in use.
- **Session state** — `st.session_state.messages` holds `{"role": "user"|"assistant", "content": "..."}`; history is rendered above the input.
- **Input** — On each user message: append to history, call `ask_api` in an assistant bubble with “Thinking…”, then show the answer or an error telling the user to start the API.

---

## Phase 3: Run and test

### 3.1 Start the API (if not already running)

In one terminal, from the **lab-02** directory (venv activated):

```bash
uvicorn api:app --reload
```

Leave it running.

### 3.2 Start the chatbot

In another terminal, same **lab-02** directory (venv activated):

```bash
streamlit run chatbot.py
```

The browser opens the Streamlit app. You should see “RAG Chatbot” and the caption with the API URL.

### 3.3 Use the chat

- Type a question and press Enter.
- The app sends **POST /ask** to the API and shows the answer.
- Ask follow-up questions; history stays visible above the input.

### 3.4 Different API URL

If the API runs on another host or port:

```bash
export RAG_API_URL=http://localhost:8000   # or your API base URL
streamlit run chatbot.py
```

The caption in the app shows the URL in use.

### 3.5 If the API is not reachable

If you see “Could not reach the RAG API”:

- Start the API in another terminal: `uvicorn api:app --reload` (from the lab-02 directory).
- If the API is elsewhere, set `RAG_API_URL` to the correct base URL.

---

## Summary

| Phase | What you did |
|-------|----------------|
| **1** | Added `streamlit` and `requests` to lab-02 `requirements.txt`; created `chatbot.py` |
| **2** | Implemented `chatbot.py`: API URL, `ask_api`, session state, chat UI, error handling |
| **3** | Ran API in one terminal (`uvicorn api:app --reload`), chatbot in another (`streamlit run chatbot.py`) |

You now have the RAG pipeline available as CLI, API, and a browser chatbot — all from the **lab-02** folder. For lab-02 setup, see **`docs/lab-02-step-by-step.md`**.
