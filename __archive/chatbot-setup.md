# Build Your RAG Chatbot: Step-by-Step Guide

This guide walks you through building a Streamlit chatbot that talks to your RAG API. By the end, you'll have a chat interface where users can ask questions and see answers with source citations.

## Prerequisites

Before starting, ensure you have:
*   **Python 3.10+** installed.
*   A **running RAG API** (e.g. the one from the RAG step-by-step guide) available at `http://localhost:8000/api/v2`.
*   The RAG API must expose:
    *   `GET /api/v2/health` — health check
    *   `POST /api/v2/ask` — accepts `{"question": "...", "k": 3, "score_threshold": null}` and returns `{"answer": "...", "sources": [...]}`.

---

## Phases

Follow the phases in order. Each phase is in its own document:

| Phase | Document | Description |
|-------|----------|-------------|
| **1** | [Phase 1: Setup](chatbot-phase-1-setup.md) | Project directory, virtual environment, dependencies, configuration, and CSS |
| **2** | [Phase 2: Chatbot](chatbot-phase-2-chatbot.md) | Session state, sidebar, chat UI, and placeholder response |
| **3** | [Phase 3: RAG Integration](chatbot-phase-3-rag-integration.md) | Call the RAG API, display answers and sources, error handling |
| **4** | [Phase 4: Run & Test](chatbot-phase-4-run-and-test.md) | Start the API and chatbot and verify the flow |

---

## Conclusion

Once you've completed all phases, you have a RAG-powered chatbot that:
*   Keeps conversation history in Streamlit session state.
*   Lets users tune retrieval (k, score threshold) from the sidebar.
*   Calls your RAG API and displays answers with source citations.
*   Handles backend-offline and API errors gracefully.

Next steps: add streaming responses, persist history to disk, or add authentication.
