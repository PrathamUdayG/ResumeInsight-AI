"""
retriever.py - RAG retrieval module.

Implements hybrid search combining FAISS semantic search with BM25 keyword search.
Uses Reciprocal Rank Fusion (RRF) to merge results from both retrieval methods.
"""

from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import faiss
from rank_bm25 import BM25Okapi

from core.embeddings import generate_embeddings, load_embedding_model, compute_similarity
from utils.constants import TOP_K, SIMILARITY_THRESHOLD


class ResumeRetriever:
    """
    Hybrid retriever combining semantic search (FAISS) with keyword search (BM25).
    
    The retriever stores resume chunks in a FAISS index for dense retrieval
    and builds a BM25 index for sparse retrieval. Results are fused using
    Reciprocal Rank Fusion (RRF) to get the best of both approaches.
    """
    
    def __init__(self, chunks: List[Dict[str, Any]] = None):
        """
        Initialize the retriever.
        
        Args:
            chunks: Optional list of chunk dictionaries to index immediately.
        """
        self.chunks = []
        self.faiss_index = None
        self.bm25_index = None
        self.embeddings = None
        self.model = load_embedding_model()
        
        if chunks:
            self.add_chunks(chunks)
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add chunks to both FAISS and BM25 indices.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'.
        """
        self.chunks.extend(chunks)
        
        # Build FAISS index
        texts = [chunk["text"] for chunk in self.chunks]
        self.embeddings = generate_embeddings(texts, model=self.model)
        
        if len(self.embeddings) > 0:
            dimension = self.embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product (cosine sim for normalized vectors)
            self.faiss_index.add(self.embeddings)
        
        # Build BM25 index
        tokenized_texts = [text.lower().split() for text in texts]
        self.bm25_index = BM25Okapi(tokenized_texts)
    
    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        section_filter: Optional[str] = None,
        use_hybrid: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a query.
        
        Args:
            query: The search query.
            top_k: Number of results to return.
            section_filter: Optional section name to filter results.
            use_hybrid: Whether to use hybrid search (semantic + BM25).
        
        Returns:
            List of relevant chunk dictionaries with scores.
        """
        if not self.chunks:
            return []
        
        if use_hybrid and self.bm25_index is not None:
            results = self._hybrid_search(query, top_k * 2)
        else:
            results = self._semantic_search(query, top_k * 2)
        
        # Apply section filter if specified
        if section_filter:
            results = [
                r for r in results
                if r.get("metadata", {}).get("section", "").lower() == section_filter.lower()
            ]
        
        # Filter by similarity threshold
        results = [r for r in results if r.get("score", 0) >= SIMILARITY_THRESHOLD]
        
        return results[:top_k]
    
    def _semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Perform semantic search using FAISS.
        
        Encodes the query into a vector and finds the nearest neighbors
        in the FAISS index using inner product (cosine similarity).
        """
        if self.faiss_index is None:
            return []
        
        query_embedding = generate_embeddings([query], model=self.model)
        
        k = min(top_k, len(self.chunks))
        scores, indices = self.faiss_index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(score)
            chunk["retrieval_method"] = "semantic"
            results.append(chunk)
        
        return results
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Perform keyword search using BM25.
        
        BM25 uses term frequency and inverse document frequency to rank
        documents by keyword relevance.
        """
        if self.bm25_index is None:
            return []
        
        query_tokens = query.lower().split()
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Normalize BM25 scores to [0, 1]
        max_score = max(scores) if max(scores) > 0 else 1
        normalized_scores = scores / max_score
        
        # Get top-k indices
        top_indices = np.argsort(normalized_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if normalized_scores[idx] <= 0:
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(normalized_scores[idx])
            chunk["retrieval_method"] = "bm25"
            results.append(chunk)
        
        return results
    
    def _hybrid_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and BM25 results using RRF.
        
        Reciprocal Rank Fusion (RRF) merges rankings from multiple retrieval
        methods using the formula: score = Σ 1/(k + rank_i) where k=60.
        """
        semantic_results = self._semantic_search(query, top_k)
        bm25_results = self._bm25_search(query, top_k)
        
        # Reciprocal Rank Fusion with k=60
        rrf_k = 60
        rrf_scores = {}
        
        for rank, result in enumerate(semantic_results):
            chunk_id = result.get("chunk_id", id(result))
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (rrf_k + rank + 1)
        
        for rank, result in enumerate(bm25_results):
            chunk_id = result.get("chunk_id", id(result))
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (rrf_k + rank + 1)
        
        # Merge and sort
        all_results = {}
        for result in semantic_results + bm25_results:
            chunk_id = result.get("chunk_id", id(result))
            if chunk_id not in all_results:
                all_results[chunk_id] = result
        
        # Apply RRF scores
        final_results = []
        for chunk_id, result in all_results.items():
            result["score"] = rrf_scores.get(chunk_id, 0)
            result["retrieval_method"] = "hybrid"
            final_results.append(result)
        
        # Sort by RRF score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        
        return final_results[:top_k]
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Return statistics about the retriever's state."""
        return {
            "total_chunks": len(self.chunks),
            "has_faiss_index": self.faiss_index is not None,
            "has_bm25_index": self.bm25_index is not None,
            "embedding_dim": self.embeddings.shape[1] if self.embeddings is not None and len(self.embeddings) > 0 else 0,
        }
