"""FastAPI app exposing the RAG pipeline via /ask."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel

from app import generate_answer
from ingestion import run_ingestion
from retrieval import retrieve

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load index and chunks at startup."""
    print("🔄 Ingesting documents...")
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    all_chunks, index = run_ingestion("data", client)
    app.state.client = client
    app.state.all_chunks = all_chunks
    app.state.index = index
    print("✅ RAG index ready.")
    yield
    # no cleanup needed


app = FastAPI(title="RAG API", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """Run RAG: retrieve relevant chunks and generate an answer."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must be non-empty")

    client = app.state.client
    index = app.state.index
    all_chunks = app.state.all_chunks

    retrieved = retrieve(question, index, all_chunks, client)
    answer = generate_answer(question, retrieved, client)
    return AskResponse(answer=answer)
