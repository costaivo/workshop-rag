# Chatbot — Phase 3: RAG Integration

**Previous:** [Phase 2: Chatbot](chatbot-phase-2-chatbot.md)

Replace the placeholder assistant response with a real call to your RAG API: send the user's question and retrieval parameters, then display the answer and sources (or errors).

---

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

**Next:** [Phase 4: Run & Test](chatbot-phase-4-run-and-test.md) — Start the API and chatbot and verify everything works.
