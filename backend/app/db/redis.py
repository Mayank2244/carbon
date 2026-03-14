"""
Redis connection and cache utilities.
"""

from typing import Optional, Any
import json
import hashlib
from redis import asyncio as aioredis

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import CacheException

logger = get_logger(__name__)

# Redis client instance
redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """
    Get Redis client instance.
    
    Returns:
        Redis client
    """
    global redis_client
    if redis_client is None:
        raise CacheException("Redis client not initialized")
    return redis_client


async def init_redis() -> None:
    """Initialize Redis connection."""
    global redis_client
    try:
        redis_client = await aioredis.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise CacheException(f"Redis initialization failed: {str(e)}")


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


def generate_cache_key(prefix: str, *args: Any) -> str:
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix: Cache key prefix
        *args: Arguments to include in key
        
    Returns:
        Cache key string
    """
    key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
    return hashlib.sha256(key_data.encode()).hexdigest()
