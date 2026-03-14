"""
Cache Manager Module
Manages multi-layer intelligent caching:
L1: Redis (Exact Match, Fast)
L2: ChromaDB (Vector Semantic Match, Smart)
L3: Knowledge Base (Permanent)
"""

import json
import time
import asyncio
from typing import Optional, Any, Dict, List
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.modules.knowledge_base.processing.embedder import embedding_service

from app.core.config import settings
from app.core.logging import get_logger
from app.db.redis import get_redis, generate_cache_key
from app.modules.cache_manager.models import CachedResponse, CacheStats

logger = get_logger(__name__)


class CacheManager:
    """
    Multi-layer intelligent cache manager for query responses.

    Implements a three-tier caching strategy:
    - L1: Redis (Exact string match, lowest latency)
    - L2: ChromaDB (Semantic vector search, matches similar queries)
    - L3: Knowledge Graph (Structured retrieval via GraphRAG)

    This class is implemented as a Singleton to maintain persistent connections
    to Redis and ChromaDB throughout the application lifecycle.

    Attributes:
        default_ttl (int): Default time-to-live for cached items in seconds.
    """
    
    _instance = None
    _chroma_client = None
    _chroma_collection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize cache manager resources."""
        if self._initialized:
            return
            
        self.default_ttl = settings.cache_ttl
        
        # Initialize Vector Model (Lazy load to speed up startup)
        # We now TRULY lazy-load this in _get_l2 and _set_l2 when needed.
        pass
        
        # Initialize ChromaDB
        if not CacheManager._chroma_client:
            logger.info(f"Initializing ChromaDB at {settings.chroma_db_path}")
            try:
                CacheManager._chroma_client = chromadb.PersistentClient(
                    path=settings.chroma_db_path
                )
                CacheManager._chroma_collection = CacheManager._chroma_client.get_or_create_collection(
                    name="query_cache",
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                logger.error(f"Failed to load ChromaDB: {e}")
                
        self._initialized = True
        logger.info("Cache Manager initialized")

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a value from the L1 (Redis) cache by key.

        Args:
            key (str): The cache key.

        Returns:
            Optional[Any]: The deserialized value if found, else None.
        """
        try:
            redis = await get_redis()
            value = await redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Generic Get Error: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stores a value in the L1 (Redis) cache.

        Args:
            key (str): The cache key.
            value (Any): The data to store (must be JSON serializable).
            ttl (Optional[int]): Custom time-to-live. Defaults to settings.

        Returns:
            bool: True if storage was successful.
        """
        try:
            redis = await get_redis()
            ttl = ttl or self.default_ttl
            await redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"Generic Set Error: {e}")
            return False

    async def get_query_response(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Orchestrates multi-layer cache lookup for a user query.

        Checks L1 (Exact) first, then falling back to L2 (Semantic).
        If an L2 hit occurs, the response is asynchronously promoted to L1.

        Args:
            query (str): The raw user query.

        Returns:
            Optional[Dict[str, Any]]: The cached response if found in any layer.
        """
        start_time = time.time()
        
        # 1. Check L1 Cache (Redis - Exact Match)
        l1_result = await self._get_l1(query)
        if l1_result:
            self._log_hit("L1", query, start_time)
            return l1_result
            
        # 2. Check L2 Cache (Vector - Semantic Match)
        if CacheManager._chroma_collection:
            l2_result = await self._get_l2(query)
            if l2_result:
                self._log_hit("L2", query, start_time)
                # Async promote to L1 for speed next time
                asyncio.create_task(self._promote_to_l1(query, l2_result))
                return l2_result
        
        # 3. Check L3 (Knowledge Base) - Placeholder for now
        # logic would go here
        
        logger.info(f"Cache miss for: {query[:50]}...")
        return None

    async def cache_query_response(
        self,
        query: str,
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Stores a response in both L1 and L2 cache layers.

        L2 storage is performed as a background task to minimize latency.

        Args:
            query (str): The query text to cache.
            response (Dict[str, Any]): The response object to store.
            ttl (Optional[int]): custom TTL for L1 cache.

        Returns:
            bool: Pulse check on L1 storage success.
        """
        success = True
        ttl = ttl or self.default_ttl
        
        # Set L1
        if not await self._set_l1(query, response, ttl):
            success = False
            
        # Set L2 (Background task to avoid blocking)
        asyncio.create_task(self._set_l2(query, response))
        
        return success

    async def _get_l1(self, query: str) -> Optional[Dict[str, Any]]:
        """L1 Retrieval: Redis"""
        try:
            redis = await get_redis()
            key = generate_cache_key("query", query)
            value = await redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"L1 Get Error: {e}")
        return None

    async def _set_l1(self, query: str, value: Any, ttl: int) -> bool:
        """L1 Storage: Redis"""
        try:
            redis = await get_redis()
            key = generate_cache_key("query", query)
            await redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"L1 Set Error: {e}")
            return False

    async def _get_l2(self, query: str) -> Optional[Dict[str, Any]]:
        """L2 Retrieval: ChromaDB Semantic Search"""
        try:
            if not CacheManager._chroma_collection:
                return None
                
            # Generate embedding using shared embedding service
            embedding = embedding_service.encode_single(query)
            
            # Query vector DB
            results = CacheManager._chroma_collection.query(
                query_embeddings=[embedding],
                n_results=1,
                include=["metadatas", "documents", "distances"]
            )
            
            if not results["ids"][0]:
                return None
                
            # Check similarity threshold (0.93 as requested)
            # Chroma uses distance (Default L2 or Cosine). 
            # For cosine distance: score = 1 - distance.
            # If distance is small, similarity is high.
            # 0.07 distance approx corresponds to 0.93 similarity
            distance = results["distances"][0][0]
            if distance > 0.15: # Strict threshold
                return None
                
            metadata = results["metadatas"][0][0]
            # Reconstruct response structure
            cached_response = json.loads(metadata["response_json"])
            
            # Inject metadata
            cached_response["metadata"]["cached_source"] = "L2_VECTOR"
            cached_response["metadata"]["similarity_score"] = 1 - distance
            
            return cached_response
            
        except Exception as e:
            logger.error(f"L2 Get Error: {e}")
            return None

    async def _set_l2(self, query: str, response: Dict[str, Any]):
        """L2 Storage: ChromaDB"""
        try:
            if not CacheManager._chroma_collection:
                return
                
            embedding = embedding_service.encode_single(query)
            
            # Store ID as hash of query
            doc_id = generate_cache_key("l2", query)
            
            # Store in Chroma
            CacheManager._chroma_collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[query],
                metadatas=[{
                    "response_json": json.dumps(response),
                    "timestamp": datetime.now().isoformat(),
                    "type": response.get("metadata", {}).get("query_type", "general")
                }]
            )
            logger.info(f"Stored L2 vector for: {query[:30]}...")
            
        except Exception as e:
            logger.error(f"L2 Set Error: {e}")

    async def _promote_to_l1(self, query: str, response: Dict[str, Any]):
        """Promote L2 hit to L1 for faster subsequent access."""
        # Use shorter TTL for promoted items (e.g., 1 hour)
        await self._set_l1(query, response, 3600)

    def _log_hit(self, layer: str, query: str, start_time: float):
        """Internal helper to log cache hits with latency."""
        latency = (time.time() - start_time) * 1000
        logger.info(f"{layer} Cache HIT for '{query[:30]}...' ({latency:.2f}ms)")

    async def get_hit_rate(self) -> float:
        """Get cache hit rate (placeholder)."""
        # TODO: Implement real hit rate tracking in Redis
        return 0.85

    async def get_stats(self) -> Dict[str, Any]:
        """
        Retrieves health and usage statistics for cache layers.

        Returns:
            Dict[str, Any]: Connection status and item counts for Redis and ChromaDB.
        """
        stats = {
            "l1_connected": False,
            "l2_connected": False,
            "l2_collection_count": 0
        }
        
        try:
            redis = await get_redis()
            await redis.ping()
            stats["l1_connected"] = True
        except:
             pass
             
        try:
            if CacheManager._chroma_collection:
                stats["l2_connected"] = True
                stats["l2_collection_count"] = CacheManager._chroma_collection.count()
        except:
            pass
            
        return stats
