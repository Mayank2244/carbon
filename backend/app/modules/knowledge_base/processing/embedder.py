"""
Embedding Model Singleton.

CRITICAL DESIGN DECISIONS:
1. Singleton pattern: Model loading is expensive (~500MB RAM + 2-3s init)
2. Lazy loading: Only load when first encode() is called
3. Batch processing: Encode multiple texts in one forward pass
4. Dimension validation: Fail fast if embedding size mismatches config

FAILURE MODES HANDLED:
- Model download failure (network issues)
- OOM during encoding (batch size limits)
- Dimension mismatch (config vs actual)
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.logging import get_logger
from app.modules.knowledge_base.config import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION

logger = get_logger(__name__)


class EmbeddingService:
    """
    Singleton wrapper for SentenceTransformer model.
    
    THREAD SAFETY: Not thread-safe. Use locks if multi-threaded.
    """
    _instance = None
    _model: SentenceTransformer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
            try:
                self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
                logger.info(f"Model loaded successfully. Dimension: {self._model.get_sentence_embedding_dimension()}")
                
                # CRITICAL: Validate dimension matches config
                actual_dim = self._model.get_sentence_embedding_dimension()
                if actual_dim != EMBEDDING_DIMENSION:
                    raise ValueError(
                        f"Embedding dimension mismatch! "
                        f"Config expects {EMBEDDING_DIMENSION}, model produces {actual_dim}"
                    )
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Embedding model initialization failed: {e}")
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding (tune based on GPU/CPU memory)
        
        Returns:
            numpy array of shape (len(texts), EMBEDDING_DIMENSION)
        
        FAILURE MODES:
        - Empty input: Returns empty array
        - OOM: Reduce batch_size
        """
        if not texts:
            logger.warning("encode() called with empty text list")
            return np.array([])
        
        self._load_model()
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            logger.debug(f"Encoded {len(texts)} texts into {embeddings.shape} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")
    
    def encode_single(self, text: str) -> List[float]:
        """Convenience method for encoding a single text."""
        if not text or not text.strip():
            raise ValueError("Cannot encode empty text")
        
        embedding = self.encode([text])[0]
        return embedding.tolist()


# Global singleton instance
embedding_service = EmbeddingService()
