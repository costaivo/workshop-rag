# Chatbot — Phase 1: Setup

Get the project and app skeleton ready: directory, virtual environment, dependencies, and initial `app.py` with configuration and styling.

---

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

**Next:** [Phase 2: Chatbot](chatbot-phase-2-chatbot.md) — Session state, sidebar, chat UI, and placeholder response.
