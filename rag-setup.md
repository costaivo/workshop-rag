# Build Your Own RAG System: Step-by-Step Student Guide

This guide will walk you through building a complete Retrieval-Augmented Generation (RAG) system using Python, Google Gemini, and FAISS. By the end, you'll have a working API that can answer questions based on your own documents.

## Prerequisites

Before starting, ensure you have:
*   **Python 3.10+** installed.
*   A **Google Cloud Project** with the Gemini API enabled.
*   An **API Key** for Google Gemini.

---

## Phases

Follow the phases in order. Each phase is in its own document:

| Phase | Document | Description |
|-------|----------|-------------|
| **1** | [Phase 1: Project Setup](phase-1-project-setup.md) | Project directory, virtual environment, dependencies, folder structure |
| **2** | [Phase 2: Configuration & Core Components](phase-2-configuration.md) | Environment variables, config, Gemini client |
| **3** | [Phase 3: The Ingestion Pipeline](phase-3-ingestion.md) | Document loader, chunker, vector store, ingestion script |
| **4** | [Phase 4: The RAG Service](phase-4-rag-service.md) | Retrieval + generation logic |
| **5** | [Phase 5: The API](phase-5-api.md) | FastAPI routes and main app entry |
| **6** | [Phase 6: Run & Test](phase-6-run-and-test.md) | Start the server and test the API |

---

## Conclusion

Once you've completed all phases, you have successfully built a RAG system! You now understand how to:
*   Process and embed unstructured text.
*   Store vectors efficiently.
*   Retrieve context semantically.
*   Generate grounded answers with an LLM.
