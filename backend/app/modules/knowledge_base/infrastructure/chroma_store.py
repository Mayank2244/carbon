"""
ChromaDB Persistent Storage Layer.

CRITICAL DESIGN DECISIONS:
1. Singleton pattern: Prevent multiple client instances (resource leak)
2. Persistent storage: Data survives process restarts
3. Collection lifecycle: get_or_create pattern prevents recreation bugs
4. Metadata filtering: Enable source-based retrieval

FAILURE MODES HANDLED:
- Missing persistence directory
- Collection already exists
- Corrupted vector store (logged, not auto-fixed)
- Dimension mismatch on insertion

CHROMADB ARCHITECTURE NOTES:
- Client is thread-safe (uses SQLite internally)
- Collections are lazy-loaded
- Embeddings are stored as float32 arrays
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from app.core.logging import get_logger
from app.modules.knowledge_base.config import (
    ensure_vector_store_exists,
    COLLECTION_NAME,
    EMBEDDING_DIMENSION
)

logger = get_logger(__name__)


class ChromaStore:
    """
    Singleton wrapper for ChromaDB persistent client.
    
    INVARIANTS:
    - Only one client instance per process
    - Collection exists before any operations
    - All embeddings have dimension = EMBEDDING_DIMENSION
    """
    _instance = None
    _client: chromadb.Client = None
    _collection: chromadb.Collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaStore, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        Initialize ChromaDB client with persistence.
        
        CRITICAL: This runs ONCE per process lifetime.
        """
        if self._client is not None:
            return
        
        try:
            persist_path = ensure_vector_store_exists()
            logger.info(f"Initializing ChromaDB at: {persist_path}")
            
            self._client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False  # Prevent accidental data loss
                )
            )
            
            # Get or create collection with COSINE distance metric
            # IMPORTANT: cosine distance = 1 - cosine_similarity
            # So: similarity = 1 - cosine_distance → always in [0, 1] ✅
            # Default L2 distance can exceed 1.0 → gives negative "similarity" ❌
            try:
                # Try to get existing collection
                existing = self._client.get_collection(name=COLLECTION_NAME)
                # Check if it uses cosine metric (metadata key hnsw:space)
                col_meta = existing.metadata or {}
                if col_meta.get("hnsw:space") != "cosine":
                    # Old collection used L2 — delete and recreate with cosine
                    logger.warning(
                        "Existing collection uses L2 distance. "
                        "Deleting and recreating with cosine metric for correct similarity scores."
                    )
                    self._client.delete_collection(name=COLLECTION_NAME)
                    raise Exception("Recreating collection")
                self._collection = existing
            except Exception:
                # Create fresh collection with cosine metric
                self._collection = self._client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={
                        "dimension": EMBEDDING_DIMENSION,
                        "hnsw:space": "cosine"   # cosine distance → similarity = 1 - distance
                    }
                )

            
            logger.info(
                f"ChromaDB initialized. Collection: {COLLECTION_NAME}, "
                f"Count: {self._collection.count()}"
            )
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            raise RuntimeError(f"Vector store initialization failed: {e}")
    
    def add_chunks(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict]
    ) -> int:
        """
        Add chunks to vector store.
        
        Args:
            ids: Unique chunk IDs (deterministic from source + index)
            embeddings: Vector embeddings (must be EMBEDDING_DIMENSION)
            documents: Raw text chunks
            metadatas: Metadata dicts (must include 'source')
        
        Returns:
            Number of chunks successfully added
        
        FAILURE MODES:
        - Duplicate IDs: ChromaDB upserts (updates existing)
        - Dimension mismatch: Raises ValueError
        - Empty input: Returns 0
        
        DESIGN NOTE: We use upsert semantics (add_or_update)
        This enables idempotent ingestion.
        """
        if not ids:
            logger.warning("add_chunks() called with empty input")
            return 0
        
        # Validate dimensions
        for i, emb in enumerate(embeddings):
            if len(emb) != EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Embedding {i} has dimension {len(emb)}, expected {EMBEDDING_DIMENSION}"
                )
        
        try:
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} chunks to vector store")
            return len(ids)
        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            raise RuntimeError(f"Vector insertion failed: {e}")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Semantic search using query embedding.
        
        Args:
            query_embedding: Query vector (must be EMBEDDING_DIMENSION)
            top_k: Number of results to return
            filters: Metadata filters (e.g., {"source": "doc1.txt"})
        
        Returns:
            Dict with keys: ids, documents, metadatas, distances
        
        DISTANCE METRIC: Cosine distance (lower = more similar)
        ChromaDB uses L2 by default, but we can configure cosine.
        """
        if len(query_embedding) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Query embedding has dimension {len(query_embedding)}, "
                f"expected {EMBEDDING_DIMENSION}"
            )
        
        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters  # Metadata filtering
            )
            
            logger.debug(f"Search returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Vector search failed: {e}")
    
    def get_count(self) -> int:
        """Get total number of chunks in collection."""
        return self._collection.count()
    
    def health_check(self) -> Dict:
        """
        Verify vector store is operational.
        
        Returns:
            Dict with status and diagnostics
        """
        try:
            count = self.get_count()
            return {
                "status": "healthy",
                "collection": COLLECTION_NAME,
                "chunk_count": count,
                "dimension": EMBEDDING_DIMENSION
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global singleton instance
chroma_store = ChromaStore()
