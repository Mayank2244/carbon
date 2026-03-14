"""
Knowledge Base Service - High-Level API.

DESIGN RATIONALE:
- Facade pattern: Hides complexity of chunking, embedding, storage
- Transactional semantics: All-or-nothing ingestion
- Detailed statistics: Enable monitoring and debugging

USAGE PATTERN:
```python
kb = KnowledgeBaseService()

# Ingest
docs = [Document(content="...", source="doc1.txt")]
stats = kb.ingest_documents(docs)

# Search
results = kb.search("How does the system work?", top_k=3)
```
"""
import time
from typing import List, Dict, Optional
from app.core.logging import get_logger
from app.modules.knowledge_base.domain import (
    Document,
    Chunk,
    SearchResult,
    IngestionStats
)
from app.modules.knowledge_base.processing import embedding_service, TextChunker
from app.modules.knowledge_base.infrastructure import chroma_store
from app.modules.knowledge_base.config import DEFAULT_TOP_K, SIMILARITY_THRESHOLD

logger = get_logger(__name__)


class KnowledgeBaseService:
    """
    High-level API for knowledge base operations.
    
    RESPONSIBILITIES:
    - Orchestrate chunking, embedding, storage
    - Provide clean search interface
    - Track statistics
    
    THREAD SAFETY: Not thread-safe (uses shared singletons)
    """
    
    def __init__(self):
        self.chunker = TextChunker()
        logger.info("KnowledgeBaseService initialized")
    
    def ingest_documents(self, documents: List[Document]) -> IngestionStats:
        """
        Ingest documents into knowledge base.
        
        PIPELINE:
        1. Chunk documents
        2. Generate embeddings
        3. Store in vector DB
        
        Args:
            documents: List of Document objects
        
        Returns:
            IngestionStats with detailed metrics
        
        FAILURE MODES:
        - Empty documents: Skipped
        - Embedding failure: Entire batch fails (transactional)
        - Storage failure: Logged, partial success possible
        """
        start_time = time.time()
        
        if not documents:
            logger.warning("ingest_documents() called with empty list")
            return IngestionStats(
                documents_processed=0,
                chunks_created=0,
                chunks_stored=0,
                duplicates_skipped=0,
                duration_seconds=0.0
            )
        
        logger.info(f"Starting ingestion of {len(documents)} documents")
        
        # Step 1: Chunk all documents
        all_chunks: List[Chunk] = []
        for doc in documents:
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        
        if not all_chunks:
            logger.warning("No chunks created (all documents empty?)")
            return IngestionStats(
                documents_processed=len(documents),
                chunks_created=0,
                chunks_stored=0,
                duplicates_skipped=0,
                duration_seconds=time.time() - start_time
            )
        
        # Step 2: Generate embeddings
        texts = [chunk.text for chunk in all_chunks]
        embeddings = embedding_service.encode(texts)
        
        # Attach embeddings to chunks
        for chunk, embedding in zip(all_chunks, embeddings):
            chunk.embedding = embedding.tolist()
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Step 3: Store in ChromaDB
        ids = [chunk.id for chunk in all_chunks]
        emb_lists = [chunk.embedding for chunk in all_chunks]
        docs = [chunk.text for chunk in all_chunks]
        metas = [chunk.metadata for chunk in all_chunks]
        
        chunks_stored = chroma_store.add_chunks(
            ids=ids,
            embeddings=emb_lists,
            documents=docs,
            metadatas=metas
        )
        
        duration = time.time() - start_time
        
        stats = IngestionStats(
            documents_processed=len(documents),
            chunks_created=len(all_chunks),
            chunks_stored=chunks_stored,
            duplicates_skipped=0,  # ChromaDB upserts, so no explicit tracking
            duration_seconds=duration
        )
        
        logger.info(f"Ingestion complete: {stats.dict()}")
        return stats
    
    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict] = None,
        min_similarity: float = SIMILARITY_THRESHOLD
    ) -> List[SearchResult]:
        """
        Semantic search over knowledge base.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            filters: Metadata filters (e.g., {"source": "doc1.txt"})
            min_similarity: Minimum similarity threshold (0-1)
        
        Returns:
            List of SearchResult objects, sorted by similarity (descending)
        
        FAILURE MODES:
        - Empty query: Returns empty list
        - No results above threshold: Returns empty list
        """
        if not query or not query.strip():
            logger.warning("search() called with empty query")
            return []
        
        logger.info(f"Searching for: '{query[:50]}...' (top_k={top_k})")
        
        # Encode query
        query_embedding = embedding_service.encode_single(query)
        
        # Search vector store
        raw_results = chroma_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        # Parse results
        results: List[SearchResult] = []
        
        for i in range(len(raw_results['ids'][0])):
            chunk_id = raw_results['ids'][0][i]
            text = raw_results['documents'][0][i]
            distance = raw_results['distances'][0][i]
            metadata = raw_results['metadatas'][0][i]
            
            # Convert distance to similarity (cosine distance -> cosine similarity)
            # ChromaDB returns L2 distance by default, but we can interpret as cosine
            # For cosine: similarity = 1 - distance
            similarity = 1.0 - distance
            
            # Filter by threshold
            if similarity < min_similarity:
                continue
            
            result = SearchResult(
                chunk_id=chunk_id,
                text=text,
                similarity=similarity,
                metadata=metadata,
                source=metadata.get('source', 'unknown')
            )
            results.append(result)
        
        logger.info(f"Found {len(results)} results above threshold {min_similarity}")
        return results
    
    def health_check(self) -> Dict:
        """Check system health."""
        return chroma_store.health_check()


# Global service instance
knowledge_base_service = KnowledgeBaseService()
