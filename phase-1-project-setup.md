# Phase 1: Project Setup

[← Back to main guide](rag-setup.md)

This phase sets up your project directory, virtual environment, dependencies, and folder structure.

---

### 1. Create the Project Directory
Open your terminal and create a new folder for your project.
```bash
mkdir rag-workshop
cd rag-workshop
```

### 2. Set Up a Virtual Environment
Isolate your dependencies to avoid conflicts.
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
Create a `requirements.txt` file with the following libraries:
```text
fastapi
uvicorn
google-generativeai
faiss-cpu
numpy
python-dotenv
pydantic
pypdf
tenacity
```

Install them:
```bash
pip install -r requirements.txt
```

### 4. Project Structure
Create the following folder structure:
```
rag-workshop/
├── app/
│   ├── api/            # API routes
│   ├── core/           # Config and LLM setup
│   ├── services/       # Core logic (RAG, Vector Store)
│   └── utils/          # Helpers
├── data/
│   ├── documents/      # Place your PDFs/TXTs here
│   └── vector_store/   # Where the index will be saved
├── scripts/            # Ingestion scripts
└── .env                # API keys (keep secret!)
```

---

**Next:** [Phase 2: Configuration & Core Components](phase-2-configuration.md)
