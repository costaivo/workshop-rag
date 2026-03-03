"""Streamlit chatbot that talks to the lab-02 RAG API."""

import os
import requests
import streamlit as st

# Default: lab-02 API running locally
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
            err = "Could not reach the RAG API. Is it running? Start it with: `cd lab-02 && uvicorn api:app --reload`"
            st.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})
