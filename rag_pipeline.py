"""
RAG Gauntlet: Root Convenience Runner
Runs the modular pipeline from the repository root.
"""

import sys
import os
import argparse

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import AcmeRAGSystem

def main():
    parser = argparse.ArgumentParser(
        description="Acme Rulebook RAG System - Runner & Inference Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python rag_pipeline.py                      # Run full 23-question benchmark
  python rag_pipeline.py --query "What should on-call engineers do for error E-1042?"
  python rag_pipeline.py --serve              # Start FastAPI REST API server
"""
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Run RAG inference on a single query and print answer + citation."
    )
    parser.add_argument(
        "--qid",
        type=str,
        default="cli-query",
        help="Question ID for single query evaluation (default: cli-query)."
    )
    parser.add_argument(
        "--serve", "-s",
        action="store_true",
        help="Start the FastAPI REST server on http://localhost:8000"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for FastAPI server (default: 8000)"
    )

    args = parser.parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if args.serve:
        import uvicorn
        print(f"Starting Acme RAG API server on http://127.0.0.1:{args.port}...")
        uvicorn.run("src.api:app", host="0.0.0.0", port=args.port, reload=True)
        return

    rag = AcmeRAGSystem(os.path.join(base_dir, "data"))

    if args.query:
        print(f"\n[Query]        : {args.query}")
        ans, cite, chunk = rag.answer_query(args.qid, args.query)
        print(f"[Answer]       : {ans}")
        print(f"[Citation]     : {cite}")
        print(f"[Source Chunk] : {chunk.citation} (ID: {chunk.chunk_id})")
        print(f"[Excerpt]      : {chunk.content[:180]}...\n")
        return

    test_path = os.path.join(base_dir, "data", "test", "test.csv")
    out_path = os.path.join(base_dir, "submissions", "submission.csv")
    
    print("\n" + "=" * 65)
    print("  RUNNING ACME RAG PIPELINE (23 EVALUATION QUESTIONS)")
    print("=" * 65)
    rag.run_benchmark(test_path, out_path)
    print(f"\n[SUCCESS] Submission successfully written to: {out_path}\n")

if __name__ == "__main__":
    main()

