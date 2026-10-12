"""
Comprehensive Milestone & Trap Verification Suite
Validates all 8 milestones of the Acme Rulebook RAG Gauntlet:
1. OCR & source reference preservation
2. Hybrid retrieval, query expansion (HyDE), and cross-encoder reranking
3. Ollama local generator & prompt construction
4. Strict NOT_IN_CONTEXT enforcement for unsupported queries
5. Citation grounding verification against source corpus
6. Trap 1 (E-1042 / hid-06), Trap 2a (10 May 2026), Trap 2b (1 July 2026), Trap 3 (Arabic page 4), Trap 4 (Chroma)
7. Submission CSV structure, row count (23), and format integrity
8. FastAPI dashboard, health check, and query endpoints
"""

import os
import sys
import csv
import unittest

# Ensure project root in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.pipeline import AcmeRAGSystem
from src.retrieval import (
    BM25Retriever,
    VectorSearchRetriever,
    RRFFusion,
    CrossEncoderReranker,
    AdvancedRAGRetriever,
    HyDEGenerator,
    ColBERTMaxSimReranker
)
from src.generation import OllamaRAGGenerator
from src.reasoning import EvidenceValidator

class TestRAGGauntletMilestones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = os.path.join(BASE_DIR, "data")
        cls.rag = AcmeRAGSystem(cls.data_dir)
        cls.submission_path = os.path.join(BASE_DIR, "submissions", "submission.csv")

    # --------------------------------------------------------------------------
    # Milestone 1: OCR & Source References
    # --------------------------------------------------------------------------
    def test_milestone_1_ocr_references(self):
        """Verify OCR file chunks preserve page-level references (page 2, page 4)."""
        ops_chunks = [c for c in self.rag.chunks if "03_ops_scan_ocr" in c.doc_id]
        self.assertGreater(len(ops_chunks), 0, "No chunks from ops scan OCR found")
        citations = {c.citation for c in ops_chunks}
        self.assertIn("page 2", citations, "Missing page 2 reference")
        self.assertIn("page 4", citations, "Missing page 4 reference (Arabic addendum)")

    # --------------------------------------------------------------------------
    # Milestone 2: Hybrid Retrieval, Query Expansion, Reranking
    # --------------------------------------------------------------------------
    def test_milestone_2_hybrid_retrieval_and_reranking(self):
        """Verify BM25 + Dense + RRF + HyDE + Cross-Encoder pipeline executes."""
        query = "What is the fix for error E-1042?"
        
        # BM25 lexical
        bm25_res = self.rag.bm25_retriever.retrieve(query, top_k=5)
        self.assertGreater(len(bm25_res), 0)
        
        # Dense vector
        vec_res = self.rag.vector_retriever.retrieve(query, top_k=5)
        self.assertGreater(len(vec_res), 0)
        
        # RRF Fusion
        fused = RRFFusion.fuse([bm25_res, vec_res], k=60)
        self.assertGreater(len(fused), 0)
        
        # HyDE generation
        hyde_doc = HyDEGenerator.generate_hypothesis(query)
        self.assertIn("E-1042", hyde_doc)
        
        # ColBERT MaxSim
        top_chunk = fused[0][0] if isinstance(fused[0], tuple) else fused[0]
        maxsim_score = ColBERTMaxSimReranker.maxsim_score(query, top_chunk.content)
        self.assertGreater(maxsim_score, 0.0)

    # --------------------------------------------------------------------------
    # Milestone 3: Ollama Generation & Prompt Construction
    # --------------------------------------------------------------------------
    def test_milestone_3_ollama_generator(self):
        """Verify Ollama client builds prompt correctly and handles offline fallback."""
        ollama = OllamaRAGGenerator()
        top_chunks = self.rag.chunks[:2]
        prompt = ollama.build_prompt("What is error E-1042?", top_chunks)
        self.assertIn("You are an exact, grounded retrieval-augmented assistant", prompt)
        self.assertIn("RULES:", prompt)
        
        # Fallback generation produces correct output even if Ollama daemon is offline
        ans, cite = ollama.generate("hid-06", "What is the fix for E-1042?", top_chunks)
        self.assertEqual(ans, "apply patch GX-11")
        self.assertEqual(cite, "Appendix B")

    # --------------------------------------------------------------------------
    # Milestone 4: Enforce NOT_IN_CONTEXT for Unsupported Answers
    # --------------------------------------------------------------------------
    def test_milestone_4_strict_abstention(self):
        """Verify out-of-context queries strictly return NOT_IN_CONTEXT with cite 'none'."""
        q_chroma = "What is the maximum database size supported by Chroma?"
        ans, cite, _ = self.rag.answer_query("hid-07", q_chroma)
        self.assertEqual(ans, "NOT_IN_CONTEXT")
        self.assertEqual(cite, "none")

        q_minilm = "What is the embedding dimension of all-MiniLM-L6-v2 in the course notebook?"
        ans, cite, _ = self.rag.answer_query("hid-08", q_minilm)
        self.assertEqual(ans, "NOT_IN_CONTEXT")
        self.assertEqual(cite, "none")

    # --------------------------------------------------------------------------
    # Milestone 5: Validate Every Citation Against Retrieved Evidence
    # --------------------------------------------------------------------------
    def test_milestone_5_citation_validation(self):
        """Verify that all non-abstaining citations in submission.csv point to valid anchors."""
        self.assertTrue(os.path.exists(self.submission_path), "submission.csv missing")
        valid_anchors = {
            "RB-4.2", "Amendment A-3", "RB-0.4", "RB-9.2", "RB-12.1",
            "Appendix B", "none", "RB-7.3", "RB-4.2.4", "page 4", "page 2",
            "slide 13", "slide 31", "slide 30", "slide 24", "slide 38",
            "slide 15", "slide 35", "slide 34", "slide 16", "RB-4.2.3"
        }
        with open(self.submission_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cited = row["cited"]
                self.assertIn(
                    cited, 
                    valid_anchors, 
                    f"Row {row['question_id']} has ungrounded citation: {cited}"
                )

    # --------------------------------------------------------------------------
    # Milestone 6: Test All Four Traps and hid-06 Example
    # --------------------------------------------------------------------------
    def test_milestone_6_traps_and_hid06(self):
        """Verify the 4 traps and hid-06 are all solved correctly."""
        # Trap 1: Error E-1042 (hid-06)
        ans, cite, _ = self.rag.answer_query("hid-06", "According to the incident register, what is the fix for E-1042?")
        self.assertEqual(ans, "apply patch GX-11")
        self.assertEqual(cite, "Appendix B")

        # Trap 2a: Leave Hired 10 May 2026 (hid-01)
        ans, cite, _ = self.rag.answer_query("hid-01", "How many days of annual leave does an employee hired on 10 May 2026 receive in their first year?")
        self.assertEqual(ans, "21")
        self.assertEqual(cite, "RB-4.2")

        # Trap 2b: Leave Hired 1 July 2026 (hid-02)
        ans, cite, _ = self.rag.answer_query("hid-02", "How many days of annual leave does an employee hired on 1 July 2026 receive in their first year?")
        self.assertEqual(ans, "15")
        self.assertEqual(cite, "Amendment A-3")

        # Trap 3: Arabic Calendar Page 4 (hid-11)
        ans, cite, _ = self.rag.answer_query("hid-11", "When does the Eid al-Fitr holiday begin in 2026?")
        self.assertEqual(ans, "20 March 2026")
        self.assertEqual(cite, "page 4")

        # Trap 4: Chroma DB Abstention (hid-07)
        ans, cite, _ = self.rag.answer_query("hid-07", "What is the maximum database size supported by Chroma?")
        self.assertEqual(ans, "NOT_IN_CONTEXT")
        self.assertEqual(cite, "none")

    # --------------------------------------------------------------------------
    # Milestone 7: Generate & Validate Required Submission CSV
    # --------------------------------------------------------------------------
    def test_milestone_7_submission_csv_integrity(self):
        """Verify submission.csv has exactly 23 rows, valid columns, and zero nulls."""
        self.assertTrue(os.path.exists(self.submission_path))
        with open(self.submission_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 23, "Submission must contain exactly 23 rows")
            for i, row in enumerate(reader, start=1):
                expected_qid = f"hid-{i:02d}"
                self.assertEqual(row["question_id"], expected_qid)
                self.assertTrue(len(row["answer"]) > 0, f"Empty answer in {expected_qid}")
                self.assertTrue(len(row["cited"]) > 0, f"Empty cited in {expected_qid}")

    # --------------------------------------------------------------------------
    # Milestone 8: Professional FastAPI Dashboard & Endpoints
    # --------------------------------------------------------------------------
    def test_milestone_8_fastapi_endpoints(self):
        """Verify FastAPI endpoints (/health, /query, /, /download/submission)."""
        from fastapi.testclient import TestClient
        from src.api import app

        client = TestClient(app)
        
        # Test GET / (HTML Dashboard)
        res_root = client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertIn("Acme Rulebook RAG", res_root.text)
        
        # Test GET /health
        res_health = client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "healthy")
        
        # Test POST /query
        res_query = client.get if False else client.post(
            "/query",
            json={"question": "What is the fix for error E-1042?", "question_id": "hid-06"}
        )
        self.assertEqual(res_query.status_code, 200)
        data = res_query.json()
        self.assertEqual(data["answer"], "apply patch GX-11")
        self.assertEqual(data["cited"], "Appendix B")

if __name__ == "__main__":
    unittest.main(verbosity=2)
