"""
Configuration for Knowledge Base (RAG) System.

DESIGN RATIONALE:
- Centralized config prevents scattered magic strings
- Pathlib for OS-agnostic path handling
- Explicit typing for IDE support and runtime validation
"""
from pathlib import Path
from typing import Final

# Persistence
VECTOR_STORE_PATH: Final[Path] = Path(__file__).parent.parent.parent.parent / "data" / "vector_store"
COLLECTION_NAME: Final[str] = "carbon_knowledge"

# Embedding Model
EMBEDDING_MODEL_NAME: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION: Final[int] = 384  # MiniLM-L6-v2 produces 384-dim vectors

# Chunking Strategy
CHUNK_SIZE: Final[int] = 512  # Characters per chunk
CHUNK_OVERLAP: Final[int] = 64  # Overlap to preserve context across boundaries

# Search
DEFAULT_TOP_K: Final[int] = 5
SIMILARITY_THRESHOLD: Final[float] = 0.2  # Cosine similarity in [0,1]; 0.2 = loosely relevant

def ensure_vector_store_exists() -> Path:
    """
    Ensure vector store directory exists.
    
    FAILURE MODE: If parent directories don't exist, create them.
    RATIONALE: Defensive against missing data/ folder.
    """
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    return VECTOR_STORE_PATH
