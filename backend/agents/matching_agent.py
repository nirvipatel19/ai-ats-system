"""Matching Agent - Computes semantic similarity using sentence-transformers."""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def compute_similarity(resume_text: str, job_description: str) -> float:
    """
    Compute semantic similarity between resume and job description.
    Returns float in [0, 1] range.
    """
    logger.info("Running Matching Agent...")
    
    if not resume_text or not resume_text.strip():
        logger.info("Matching Agent complete. Empty resume, score=0.")
        return 0.0
    
    if not job_description or not job_description.strip():
        logger.info("Matching Agent complete. Empty JD, score=0.")
        return 0.0
    
    model = _get_model()
    
    # Truncate long texts to avoid token limits
    max_chars = 2000
    resume_snippet = resume_text[:max_chars] if len(resume_text) > max_chars else resume_text
    jd_snippet = job_description[:max_chars] if len(job_description) > max_chars else job_description
    
    embeddings = model.encode([resume_snippet, jd_snippet])
    resume_emb = embeddings[0]
    jd_emb = embeddings[1]
    
    # Cosine similarity
    import numpy as np
    cos_sim = np.dot(resume_emb, jd_emb) / (
        np.linalg.norm(resume_emb) * np.linalg.norm(jd_emb)
    )
    
    # Normalize to [0, 1] (cosine is typically in [-1, 1])
    score = float((cos_sim + 1) / 2)
    
    logger.info(f"Matching Agent complete. Similarity score: {score:.4f}")
    return round(score, 4)
