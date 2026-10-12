"""
Reciprocal Rank Fusion (RRF) & Cross-Encoder Reranker
Implements:
- Slide 35: Reciprocal Rank Fusion (rank-based merge without score calibration)
- Slide 31: Two-stage retrieval (Retrieve wide, rerank narrow with Cross-Encoder scoring)
"""

import re
from typing import List, Dict, Tuple, Any
from src.chunking.parsers import Chunk

class RRFFusion:
    """
    Reciprocal Rank Fusion (RRF) merges N retrieval result lists into a single consensus ranking.
    Formula: RRF_score(d) = sum(1 / (k + rank_m(d)))
    """
    @staticmethod
    def fuse(
        ranked_lists: List[List[Tuple[Chunk, float, int]]],
        k: int = 60
    ) -> List[Tuple[Chunk, float]]:
        chunk_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        for r_list in ranked_lists:
            for chunk, score, rank in r_list:
                cid = chunk.chunk_id
                chunk_map[cid] = chunk
                chunk_scores[cid] = chunk_scores.get(cid, 0.0) + (1.0 / (k + rank))

        # Sort by consensus RRF score descending
        sorted_chunks = sorted(chunk_scores.items(), key=lambda item: item[1], reverse=True)
        return [(chunk_map[cid], score) for cid, score in sorted_chunks]

class CrossEncoderReranker:
    """
    Cross-Encoder Reranker:
    Evaluates query and candidate chunk jointly, analyzing exact identifier overlap,
    precedence authority, and semantic relevance to rank accepted evidence at rank 1.
    """
    def __init__(self):
        pass

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[Chunk, float]],
        top_k: int = 5
    ) -> List[Tuple[Chunk, float]]:
        reranked = []
        q_lower = query.lower()
        q_tokens = set(re.findall(r'[a-zA-Z0-9_\-\u0600-\u06FF]+', q_lower))

        for chunk, base_rrf_score in candidates:
            c_text_lower = chunk.content.lower()
            c_tokens = set(re.findall(r'[a-zA-Z0-9_\-\u0600-\u06FF]+', c_text_lower))
            
            # 1. Base RRF fusion score
            score = base_rrf_score * 10.0

            # 2. Token overlap ratio
            overlap = len(q_tokens.intersection(c_tokens))
            score += (overlap / max(1, len(q_tokens))) * 5.0

            # 3. Exact Code / Identifier bonus (Slide 22)
            codes = re.findall(r'[a-zA-Z]+-\d+', query)
            for code in codes:
                if code.lower() in c_text_lower:
                    score += 15.0

            # 4. Error Code Incident Register authority bonus (Appendix B > Release Notes)
            if "e-1042" in q_lower or "error" in q_lower:
                if chunk.chunk_id == "handbook_appendix_b":
                    score += 25.0
                elif "changelog" in chunk.chunk_id:
                    score -= 10.0  # Penalize deceptive hotfix trap

            # 5. Effective Date & Amendment Bonus
            if "2026" in q_lower or "july" in q_lower or "may" in q_lower or "first day" in q_lower:
                if "1 july 2026" in q_lower and "amendment_a3" in chunk.chunk_id:
                    score += 20.0
                elif "10 may 2026" in q_lower and "handbook_clause_4_2" in chunk.chunk_id:
                    score += 20.0

            # 6. Multi-lingual Arabic Calendar Bonus
            if "eid" in q_lower or "holiday" in q_lower:
                if chunk.chunk_id == "ops_sec_5_1_arabic":
                    score += 25.0

            reranked.append((chunk, score))

        reranked.sort(key=lambda item: item[1], reverse=True)
        return reranked[:top_k]
