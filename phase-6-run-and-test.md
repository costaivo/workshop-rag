# Phase 6: Run & Test

[← Back to main guide](rag-setup.md)

This phase gets your server running and shows how to test the API.

---

### 14. Start the Server
```bash
uvicorn app.main:app --reload
```

### 15. Test Your API
Open your browser to `http://localhost:8000/docs`.
1.  Click on the **POST /api/ask** endpoint.
2.  Click **Try it out**.
3.  Enter a question related to your documents:
    ```json
    {
      "question": "What is the main topic of the uploaded document?"
    }
    ```
4.  Execute and watch the magic happen!

---

**Previous:** [Phase 5: The API](phase-5-api.md)
