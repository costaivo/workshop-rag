# Build Your RAG Chatbot: Step-by-Step Guide

This guide walks you through building a Streamlit chatbot that talks to your RAG API. By the end, you'll have a chat interface where users can ask questions and see answers with source citations.

The application is built in **three phases**:

1. **Setup** — Project structure, environment, and base configuration.
2. **Chatbot** — Session state, sidebar, chat UI, and conversation flow (with a placeholder response).
3. **RAG integration** — Connect to your RAG API, call `/ask`, and display answers with source citations.

---

## Prerequisites

Before starting, ensure you have:
*   **Python 3.10+** installed.
*   A **running RAG API** (e.g. the one from the RAG step-by-step guide) available at `http://localhost:8000/api/v2`.
*   The RAG API must expose:
    *   `GET /api/v2/health` — health check
    *   `POST /api/v2/ask` — accepts `{"question": "...", "k": 3, "score_threshold": null}` and returns `{"answer": "...", "sources": [...]}`.

---

## Phase 1: Setup

Get the project and app skeleton ready: directory, virtual environment, dependencies, and initial `app.py` with configuration and styling.

### 1. Create the Chatbot Directory
Create a folder for the chatbot app (e.g. next to your RAG project or inside the same repo).
```bash
mkdir chatbot
cd chatbot
```

### 2. Set Up a Virtual Environment
Isolate dependencies to avoid conflicts.
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Create a `requirements.txt` file with:
```text
streamlit
requests
```

Install them:
```bash
pip install -r requirements.txt
```

### 4. Project Structure
Your chatbot folder can look like this:
```
chatbot/
├── app.py           # Single-file Streamlit app (or split later)
└── requirements.txt
```

### 5. Configuration and Page Config
Create `app.py` and add imports, API base URL, and Streamlit page config at the top.
```python
import streamlit as st
import requests
import json
from typing import Dict, List

# --- Configuration ---
API_BASE_URL = "http://localhost:8000/api/v2"  # Adjust if your backend runs elsewhere
PAGE_TITLE = "RAG Workshop Assistant"
PAGE_ICON = "🤖"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
```

*   **Why `layout="wide"`?** Gives more room for chat messages and source boxes.

### 6. Add Custom CSS (Optional)
Style the source citations and chat bubbles.
```python
# --- Custom CSS ---
st.markdown("""
<style>
    .source-box {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-top: 5px;
        font-size: 0.85em;
        border-left: 3px solid #ff4b4b;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)
```

At this point you can run `streamlit run app.py`; the page will load with title and styling but no chat yet.

---

## Phase 2: Chatbot

Build the chat UI: session state for conversation history, sidebar with controls, main area with title and chat history, and chat input. Use a **placeholder** assistant response so the conversation flow works before we connect to the RAG API.

### 7. Initialize Chat History in Session State
Streamlit reruns the script on every interaction. Use `st.session_state` to keep chat history across reruns.
```python
# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
```

Each message is a dict: `{"role": "user"|"assistant", "content": "...", "sources": [...]}` (sources only for assistant).

### 8. Build the Sidebar
Put retrieval parameters and controls in the sidebar. The Status section will show backend state once RAG is integrated.
```python
# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    
    st.subheader("Retrieval Parameters")
    k_chunks = st.slider("Number of Chunks (k)", min_value=1, max_value=10, value=3)
    score_threshold = st.slider("Similarity Threshold", min_value=0.0, max_value=1.0, value=0.0, step=0.05)
    
    st.divider()
    
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("### Status")
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("Backend Online ✅")
        else:
            st.warning(f"Backend Status: {health.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("Backend Offline ❌")
        st.caption("Ensure the RAG API is running on port 8000")
```

*   **k_chunks** and **score_threshold** will be sent with each `/ask` request once RAG is integrated.

### 9. Main Interface — Title and Caption
```python
# --- Main Interface ---
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.caption("Ask questions about the workshop materials, speakers, and AI concepts.")
```

### 10. Render Chat History
Loop over `st.session_state.messages` and show each message; show sources for assistant messages.
```python
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Sources", expanded=False):
                for idx, source in enumerate(message["sources"], 1):
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source {idx}:</strong> {source['source']} (Page {source['page']})<br>
                        <em>Relevance: {source['score']:.2f}</em>
                    </div>
                    """, unsafe_allow_html=True)
```

*   Adjust `source['source']`, `source['page']`, and `source['score']` if your API returns different field names.

### 11. Chat Input and Placeholder Assistant Response
Use `st.chat_input` so the user types in the chat bar. On submit, append the user message, show it, then add a **placeholder** assistant reply so the conversation flow works. In Phase 3 we'll replace this with the real RAG API call.
```python
# Chat Input
if prompt := st.chat_input("What would you like to know?"):
    # 1. Add and show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Placeholder assistant response (replace in Phase 3 with RAG API call)
    with st.chat_message("assistant"):
        placeholder_reply = "_(RAG response will appear here once integrated.)_"
        st.markdown(placeholder_reply)
    st.session_state.messages.append({
        "role": "assistant",
        "content": placeholder_reply,
        "sources": []
    })
```

Run the app now: you can type messages and see them with a placeholder reply. Next, we wire in the real RAG API.

---

## Phase 3: RAG Integration

Replace the placeholder assistant response with a real call to your RAG API: send the user's question and retrieval parameters, then display the answer and sources (or errors).

### 12. Call the RAG API and Display the Response
Replace the placeholder block (the `# 2. Placeholder assistant response` section) with the following. It POSTs to `/ask`, shows a spinner, and renders the answer and sources.
```python
# Chat Input
if prompt := st.chat_input("What would you like to know?"):
    # 1. Add and show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get assistant response from RAG API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        sources = []
        
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "question": prompt,
                    "k": k_chunks,
                    "score_threshold": score_threshold if score_threshold > 0 else None
                }
                
                response = requests.post(f"{API_BASE_URL}/ask", json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    full_response = data["answer"]
                    sources = data.get("sources", [])
                    
                    message_placeholder.markdown(full_response)
                    
                    if sources:
                        with st.expander("📚 View Sources", expanded=False):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"""
                                <div class="source-box">
                                    <strong>Source {idx}:</strong> {source['source']} (Page {source['page']})<br>
                                    <em>Relevance: {source['score']:.2f}</em>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    message_placeholder.error(error_msg)
                    full_response = error_msg
                    
            except requests.exceptions.ConnectionError:
                error_msg = "❌ Could not connect to the backend. Is it running?"
                message_placeholder.error(error_msg)
                full_response = error_msg
            except Exception as e:
                error_msg = f"❌ An error occurred: {str(e)}"
                message_placeholder.error(error_msg)
                full_response = error_msg

    # 3. Persist assistant message in session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "sources": sources
    })
```

The sidebar **Status** (from Phase 2) already uses `API_BASE_URL` for the health check, so you can confirm the backend is reachable before asking questions.

---

## Run & Test

### 13. Start the RAG API (if not already running)
From your RAG project directory:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Confirm that `GET http://localhost:8000/api/v2/health` returns 200.

### 14. Start the Chatbot
From the **chatbot** directory:
```bash
streamlit run app.py
```

### 15. Use the Chatbot
1.  Open the URL Streamlit prints (e.g. `http://localhost:8313`).
2.  Check the sidebar: **Status** should show "Backend Online ✅".
3.  Type a question in the chat input and press Enter.
4.  Verify the answer and expand "📚 View Sources" to see citations.
5.  Use **Clear Chat History** to reset the conversation.
6.  Adjust **Number of Chunks (k)** and **Similarity Threshold** and ask again to see how retrieval behavior changes.

---

## Conclusion

You now have a RAG-powered chatbot that:
*   Keeps conversation history in Streamlit session state.
*   Lets users tune retrieval (k, score threshold) from the sidebar.
*   Calls your RAG API and displays answers with source citations.
*   Handles backend-offline and API errors gracefully.

Next steps: add streaming responses, persist history to disk, or add authentication.
