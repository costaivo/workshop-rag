# Chatbot — Phase 2: Chatbot

**Previous:** [Phase 1: Setup](chatbot-phase-1-setup.md)

Build the chat UI: session state for conversation history, sidebar with controls, main area with title and chat history, and chat input. Use a **placeholder** assistant response so the conversation flow works before we connect to the RAG API.

---

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

**Next:** [Phase 3: RAG Integration](chatbot-phase-3-rag-integration.md) — Call the RAG API and display answers with sources.
