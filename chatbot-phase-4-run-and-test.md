# Chatbot — Phase 4: Run & Test

**Previous:** [Phase 3: RAG Integration](chatbot-phase-3-rag-integration.md)

Start the RAG API and the Streamlit chatbot, then verify the full flow.

---

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

**Back to:** [Build Your RAG Chatbot — Step-by-Step Guide](chatbot-setup.md)
