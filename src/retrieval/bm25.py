"""
BM25 Lexical Retrieval Engine
Preserves exact terms, identifiers, codes, and numerical values.
Implements Lecture Slide 25 defaults: k1 = 1.2, b = 0.75.
"""

import re
import math
from typing import List, Dict, Tuple, Any
from src.chunking.parsers import Chunk

class BM25Retriever:
    def __init__(self, chunks: List[Chunk], k1: float = 1.2, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks = chunks
        self.corpus = [c.content for c in chunks]
        self.doc_len = [len(self.tokenize(text)) for text in self.corpus]
        self.avg_len = sum(self.doc_len) / max(1, len(chunks))
        
        self.df: Dict[str, int] = {}
        self.doc_freqs: List[Dict[str, int]] = []
        
        for text in self.corpus:
            tf: Dict[str, int] = {}
            for t in self.tokenize(text):
                tf[t] = tf.get(t, 0) + 1
            self.doc_freqs.append(tf)
            for t in tf:
                self.df[t] = self.df.get(t, 0) + 1
                
        self.idf: Dict[str, float] = {}
        n = len(chunks)
        for t, df_val in self.df.items():
            # Robust smoothed Robertson-Spärck Jones IDF
            self.idf[t] = math.log((n - df_val + 0.5) / (df_val + 0.5) + 1.0)

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Specialized tokenizer that preserves:
        - Hyphenated codes (E-1042, GX-11, A-3)
        - Dotted clause numbers (4.2, 4.2.3, 0.4)
        - Times (02:00, 04:00, 18:00, 18:30)
        - Arabic tokens (العطلات, عيد الفطر, مارس)
        - Standard alphanumerics
        """
        tokens = re.findall(r'[a-zA-Z0-9]+(?:[-.:][a-zA-Z0-9]+)*|[\u0600-\u06FF]+', text.lower())
        return tokens

    def score(self, query: str) -> List[float]:
        q_tokens = self.tokenize(query)
        scores = [0.0] * len(self.chunks)
        
        for i, tf in enumerate(self.doc_freqs):
            d_len = self.doc_len[i]
            s = 0.0
            for t in q_tokens:
                if t in tf:
                    t_count = tf[t]
                    idf_val = self.idf.get(t, 0.0)
                    denom = t_count + self.k1 * (1.0 - self.b + self.b * (d_len / self.avg_len))
                    term_score = idf_val * (t_count * (self.k1 + 1.0)) / denom
                    
                    # Exact Identifier Boost (Slide 22: Identifiers & Codes require exact match)
                    if any(c in t for c in ['-', '.', ':']) or len(t) > 5:
                        term_score *= 1.5
                        
                    s += term_score
            scores[i] = s
        return scores

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Chunk, float, int]]:
        """Returns sorted list of (Chunk, score, rank) tuples."""
        scores = self.score(query)
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for rank, idx in enumerate(ranked_indices[:top_k], start=1):
            results.append((self.chunks[idx], scores[idx], rank))
        return results
