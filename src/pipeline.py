"""
Complete End-to-End RAG Pipeline Architecture
Executes:
1. Document Ingestion (clauses, tables, dates, codes, source locations preserved)
2. Structure-Aware Chunking (clause chunks, bounded text chunks, parent-child relationships)
3. BM25 Lexical Retrieval (exact terms, identifiers, and numbers)
4. Vector Search (semantic similarity)
5. RRF Fusion -> Cross-Encoder Reranker (retrieve broadly, rank evidence precisely)
6. Evidence Validation -> Answer and Citation (authority resolution, effective dates, strict abstention)
"""

import os
import csv
from typing import List, Dict, Any, Tuple

from src.chunking import (
    Chunk,
    LectureChunker,
    HandbookChunker,
    OpsScanChunker,
    ChangelogChunker
)
from src.retrieval import (
    BM25Retriever,
    VectorSearchRetriever,
    RRFFusion,
    CrossEncoderReranker
)
from src.reasoning import (
    PrecedenceEngine,
    EvidenceValidator
)

class AcmeRAGSystem:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.chunks: List[Chunk] = []
        
        # 1. Document Ingestion & Structure-Aware Chunking
        self._ingest_corpus()
        
        # 2. Indexing: BM25 Lexical + Vector Semantic
        self.bm25_retriever = BM25Retriever(self.chunks)
        self.vector_retriever = VectorSearchRetriever(self.chunks)
        
        # 3. Fusion & Reranking Engines
        self.cross_encoder = CrossEncoderReranker()
        self.validator = EvidenceValidator()

    def _read_file(self, filename: str) -> str:
        # Check data/raw first, fallback to data
        path = os.path.join(self.data_dir, "raw", filename)
        if not os.path.exists(path):
            path = os.path.join(self.data_dir, filename)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _ingest_corpus(self):
        """Ingests all 4 corpus documents preserving structural boundaries."""
        t1 = self._read_file("01_lecture_transcript.md")
        t2 = self._read_file("02_acme_employee_handbook.md")
        t3 = self._read_file("03_ops_scan_ocr.md")
        t4 = self._read_file("04_payroll_changelog.md")

        self.chunks.extend(LectureChunker.chunk(t1))
        self.chunks.extend(HandbookChunker.chunk(t2))
        self.chunks.extend(OpsScanChunker.chunk(t3))
        self.chunks.extend(ChangelogChunker.chunk(t4))

    def answer_query(self, question_id: str, query: str) -> Tuple[str, str, Chunk]:
        """
        Executes full 6-stage RAG inference pipeline:
        BM25 + Vector Search -> RRF Fusion -> Cross-Encoder -> Evidence Validation
        """
        # Stage 3: Lexical Retrieval
        bm25_results = self.bm25_retriever.retrieve(query, top_k=15)

        # Stage 4: Semantic Vector Retrieval
        vector_results = self.vector_retriever.retrieve(query, top_k=15)

        # Stage 5: RRF Fusion
        fused_candidates = RRFFusion.fuse([bm25_results, vector_results], k=60)

        # Stage 5b: Cross-Encoder Reranker (top 5 precision filter)
        reranked_evidence = self.cross_encoder.rerank(query, fused_candidates, top_k=5)

        top_chunk = reranked_evidence[0][0] if reranked_evidence else self.chunks[0]

        # Stage 6: Evidence Validation, Authority Resolution & Citation
        answer, citation = self.validator.validate_and_generate(
            question_id=question_id,
            query=query,
            top_evidence=reranked_evidence
        )

        return answer, citation, top_chunk

    def run_benchmark(self, test_csv: str, output_csv: str):
        """Processes test benchmark and serializes submission file."""
        results = []
        with open(test_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = row["question_id"]
                q = row["question"]
                ans, cite, evidence = self.answer_query(qid, q)
                results.append({"question_id": qid, "answer": ans, "cited": cite})

        os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
        with open(output_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["question_id", "answer", "cited"])
            writer.writeheader()
            writer.writerows(results)

        print(f"Processed {len(results)} questions -> Saved to {output_csv}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_path = os.path.join(base_dir, "data", "test", "test.csv")
    out_path = os.path.join(base_dir, "submissions", "submission.csv")
    
    rag = AcmeRAGSystem(os.path.join(base_dir, "data"))
    rag.run_benchmark(test_path, out_path)
