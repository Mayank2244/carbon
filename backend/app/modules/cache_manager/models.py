"""
Cache Manager Models
Defines data structures for intelligent caching.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CachedResponse(BaseModel):
    """Structured cached response."""
    
    query: str
    response: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)
    ttl: int
    
    # Layer tracking
    source_layer: str = "L1"  # L1, L2, L3
    similarity_score: float = 1.0  # 1.0 for exact match


class CacheStats(BaseModel):
    """Cache statistics."""
    
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    total_keys: int = 0
    vector_keys: int = 0
    avg_latency_ms: float = 0.0
