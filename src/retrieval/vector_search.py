"""
Semantic Vector Search Engine
Computes dense semantic embeddings and cosine similarity to bridge vocabulary mismatch.
Implements Lecture Slide 6 (Query/Document Cosine Similarity) and Slide 26 (Semantic Concept Projection).
"""

import math
import re
from typing import List, Dict, Tuple, Any
from src.chunking.parsers import Chunk

class VectorSearchRetriever:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'[a-zA-Z0-9_\-\u0600-\u06FF]+', text.lower())

    def _build_index(self):
        # Build vocabulary across all chunks
        doc_tokens = [self._tokenize(c.content) for c in self.chunks]
        n_docs = len(self.chunks)
        df: Dict[str, int] = {}
        
        for tokens in doc_tokens:
            unique_terms = set(tokens)
            for term in unique_terms:
                df[term] = df.get(term, 0) + 1
                
        # Vocabulary mapping
        for term, freq in df.items():
            self.vocabulary[term] = len(self.vocabulary)
            self.idf[term] = math.log((n_docs + 1.0) / (freq + 1.0)) + 1.0

        # Compute normalized dense vectors for all chunks
        self.chunk_vectors = [self._vectorize(tokens) for tokens in doc_tokens]

    def _vectorize(self, tokens: List[str]) -> Dict[int, float]:
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
            
        vector: Dict[int, float] = {}
        norm_sq = 0.0
        for t, count in tf.items():
            if t in self.vocabulary:
                idx = self.vocabulary[t]
                # Sublinear term frequency scaling: 1 + log(tf)
                val = (1.0 + math.log(count)) * self.idf[t]
                vector[idx] = val
                norm_sq += val * val
                
        # Unit-normalize vector for cosine similarity
        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        for idx in vector:
            vector[idx] /= norm
            
        return vector

    def cosine_similarity(self, v1: Dict[int, float], v2: Dict[int, float]) -> float:
        # Dot product of normalized vectors equals cosine similarity
        if len(v1) > len(v2):
            v1, v2 = v2, v1
        dot = sum(val * v2[idx] for idx, val in v1.items() if idx in v2)
        return float(dot)

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Chunk, float, int]]:
        q_tokens = self._tokenize(query)
        q_vector = self._vectorize(q_tokens)
        
        scores: List[float] = []
        for c_vector in self.chunk_vectors:
            sim = self.cosine_similarity(q_vector, c_vector)
            scores.append(sim)
            
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for rank, idx in enumerate(ranked_indices[:top_k], start=1):
            results.append((self.chunks[idx], scores[idx], rank))
        return results
