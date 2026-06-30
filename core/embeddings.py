"""
embeddings.py - Embedding generation module.

Uses Sentence Transformers (all-MiniLM-L6-v2) to convert text chunks
into dense vector representations for semantic search.
"""

import hashlib
from typing import List, Dict, Any, Optional

import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

from utils.constants import EMBEDDING_MODEL, EMBEDDING_DIMENSION


@st.cache_resource(show_spinner=False)
def load_embedding_model(model_name: str = EMBEDDING_MODEL) -> SentenceTransformer:
    """
    Load and cache the sentence transformer model.
    
    Uses Streamlit's cache_resource to ensure the model is loaded only once
    per session, saving memory and startup time.
    """
    model = SentenceTransformer(model_name)
    return model


def generate_embeddings(
    texts: List[str],
    model: Optional[SentenceTransformer] = None,
    batch_size: int = 32,
    show_progress: bool = False,
) -> np.ndarray:
    """
    Generate embeddings for a list of texts.
    
    Args:
        texts: List of text strings to embed.
        model: Pre-loaded SentenceTransformer model. If None, loads default.
        batch_size: Number of texts to embed at once.
        show_progress: Whether to show a progress bar.
    
    Returns:
        NumPy array of shape (n_texts, embedding_dim).
    """
    if not texts:
        return np.array([])
    
    if model is None:
        model = load_embedding_model()
    
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,  # L2 normalize for cosine similarity
    )
    
    return np.array(embeddings, dtype=np.float32)


def generate_chunk_embeddings(
    chunks: List[Dict[str, Any]],
    model: Optional[SentenceTransformer] = None,
) -> List[Dict[str, Any]]:
    """
    Generate embeddings for resume chunks and attach them to chunk metadata.
    
    Args:
        chunks: List of chunk dictionaries from the chunking module.
        model: Pre-loaded model (optional).
    
    Returns:
        Updated chunks with 'embedding' field added.
    """
    if not chunks:
        return []
    
    if model is None:
        model = load_embedding_model()
    
    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts, model=model)
    
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
    
    return chunks


def compute_similarity(
    query_embedding: np.ndarray,
    document_embeddings: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between a query and document embeddings.
    
    Since embeddings are L2-normalized, cosine similarity = dot product.
    
    Args:
        query_embedding: Single query vector of shape (dim,).
        document_embeddings: Matrix of shape (n_docs, dim).
    
    Returns:
        Array of similarity scores of shape (n_docs,).
    """
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    
    similarities = np.dot(document_embeddings, query_embedding.T).flatten()
    return similarities


def get_text_hash(text: str) -> str:
    """
    Generate a hash for text content to detect duplicates.
    
    Used for caching: if the same resume is uploaded again, we can skip
    re-computing embeddings.
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()
