"""
Quality Evaluator for Prompt Optimization.
Uses Semantic Similarity to ensure compression doesn't lose meaning.
"""

try:
    from sentence_transformers import util
    from app.modules.knowledge_base.processing.embedder import embedding_service
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("! sentence-transformers not found, using string similarity fallback")

from app.core.logging import get_logger

logger = get_logger(__name__)

class QualityEvaluator:
    """Evaluates quality of response preservation."""
    
    def __init__(self):
        # Using shared embedding_service instead of local model
        pass

    def evaluate_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts using shared embedding service.
        """
        if not TRANSFORMERS_AVAILABLE:
            return self._fallback_similarity(text1, text2)
            
        try:
            import numpy as np
            # Use shared embedding service
            emb1 = np.array(embedding_service.encode_single(text1))
            emb2 = np.array(embedding_service.encode_single(text2))
            
            # Simple cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm_a = np.linalg.norm(emb1)
            norm_b = np.linalg.norm(emb2)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            return float(dot_product / (norm_a * norm_b))
        except Exception as e:
            logger.error(f"Semantic similarity failed, falling back: {e}")
            return self._fallback_similarity(text1, text2)

    def _fallback_similarity(self, text1: str, text2: str) -> float:
        """String-based fallback similarity."""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
