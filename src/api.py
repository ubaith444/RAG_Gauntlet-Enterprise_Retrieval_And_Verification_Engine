"""
FastAPI Service for RAG Gauntlet System
Provides REST endpoints for:
- /query: Grounded RAG query answering with Ollama / Evidence Validator
- /ingest: Multi-format document ingestion (PDF, Markdown, DOCX, TXT)
- /benchmark: Evaluates the 23-question test set and writes submission.csv
- /health: System health and Ollama connection status
"""

import os
import csv
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from src.pipeline import AcmeRAGSystem
from src.generation import OllamaRAGGenerator
from src.ingestion import DocumentIngestionPipeline

app = FastAPI(
    title="Acme Rulebook RAG API",
    description="Production-grade RAG service featuring hybrid retrieval, cross-encoder reranking, and Ollama LLM generation.",
    version="1.0.0"
)

# Initialize singletons
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
SUBMISSION_CSV_PATH = os.path.join(BASE_DIR, "submissions", "submission.csv")

rag_system = AcmeRAGSystem(DATA_DIR)
ollama_gen = OllamaRAGGenerator()
ingestion_pipe = DocumentIngestionPipeline()

# Schemas
class QueryRequest(BaseModel):
    question: str
    question_id: Optional[str] = "user-query"

class QueryResponse(BaseModel):
    question_id: str
    question: str
    answer: str
    cited: str
    top_sources: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    total_indexed_chunks: int
    ollama_online: bool

# Web UI and Static Endpoints
@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
@app.get("/ui", response_class=HTMLResponse, tags=["Web UI"])
@app.get("/index.html", response_class=HTMLResponse, tags=["Web UI"])
def get_ui():
    """Serves the interactive light-mode RAG console."""
    if os.path.exists(STATIC_HTML_PATH):
        with open(STATIC_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h2>Acme RAG Console</h2><p>Static UI file not found.</p>")

@app.get("/api/info", tags=["Info"])
def api_info():
    """Returns system metadata and health."""
    return {
        "service": "Acme Rulebook RAG System",
        "version": "1.0.0",
        "docs": "/docs",
        "ui": "/",
        "status": "operational",
        "total_indexed_chunks": len(rag_system.chunks)
    }

@app.get("/api/benchmark-results", tags=["Benchmark"])
def get_benchmark_results():
    """Returns the 23 evaluation questions and answers from submission.csv as JSON."""
    if not os.path.exists(SUBMISSION_CSV_PATH):
        test_path = os.path.join(DATA_DIR, "test", "test.csv")
        rag_system.run_benchmark(test_path, SUBMISSION_CSV_PATH)

    results = []
    with open(SUBMISSION_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results

@app.get("/download/submission", tags=["Benchmark"])
def download_submission():
    """Downloads the canonical submissions/submission.csv file."""
    if not os.path.exists(SUBMISSION_CSV_PATH):
        test_path = os.path.join(DATA_DIR, "test", "test.csv")
        rag_system.run_benchmark(test_path, SUBMISSION_CSV_PATH)
    return FileResponse(
        path=SUBMISSION_CSV_PATH,
        filename="submission.csv",
        media_type="text/csv"
    )

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """Graceful 404 handler that redirects browser users to the Web UI."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/")
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found", "available_endpoints": ["/", "/docs", "/query", "/health", "/benchmark"]}
    )

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    return HealthResponse(
        status="healthy",
        total_indexed_chunks=len(rag_system.chunks),
        ollama_online=ollama_gen.is_available()
    )

@app.post("/query", response_model=QueryResponse, tags=["RAG"])
def query(req: QueryRequest):
    """
    Executes 6-stage RAG inference pipeline:
    1. BM25 Lexical Retrieval
    2. Dense Vector Retrieval
    3. RRF Consensus Fusion
    4. Cross-Encoder Reranking
    5. Ollama Generation with Citation Validation & NOT_IN_CONTEXT preservation
    """
    answer, citation, top_chunk = rag_system.answer_query(
        question_id=req.question_id,
        query=req.question
    )

    # Gather top retrieved source summaries
    bm25_res = rag_system.bm25_retriever.retrieve(req.question, top_k=3)
    top_sources = [
        {"chunk_id": c.chunk_id, "citation": c.citation, "score": round(score, 3)}
        for c, score, _ in bm25_res
    ]

    return QueryResponse(
        question_id=req.question_id,
        question=req.question,
        answer=answer,
        cited=citation,
        top_sources=top_sources
    )

@app.post("/ingest", tags=["Ingestion"])
async def ingest_document(file: UploadFile = File(...)):
    """
    Accepts uploaded document (PDF, Markdown, DOCX, TXT)
    Detects format -> extracts text via PyMuPDF / native parser -> chunks -> adds to index.
    """
    upload_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    temp_path = os.path.join(upload_dir, file.filename)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    new_chunks = ingestion_pipe.extract_and_chunk(temp_path)
    rag_system.chunks.extend(new_chunks)
    
    # Re-index retrievers with new chunks
    rag_system.bm25_retriever = type(rag_system.bm25_retriever)(rag_system.chunks)
    rag_system.vector_retriever = type(rag_system.vector_retriever)(rag_system.chunks)

    return {
        "filename": file.filename,
        "format": ingestion_pipe.detector.detect_format(temp_path),
        "chunks_extracted": len(new_chunks),
        "total_index_size": len(rag_system.chunks)
    }

@app.post("/benchmark", tags=["Benchmark"])
def run_benchmark():
    """
    Evaluates official 23 hidden questions from data/test/test.csv
    Writes canonical submissions/submission.csv
    """
    test_path = os.path.join(DATA_DIR, "test", "test.csv")
    out_path = os.path.join(BASE_DIR, "submissions", "submission.csv")

    rag_system.run_benchmark(test_path, out_path)

    # Read preview rows
    preview = []
    with open(out_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 5:
                preview.append(row)

    return {
        "status": "success",
        "output_path": out_path,
        "total_rows": 23,
        "preview": preview
    }
