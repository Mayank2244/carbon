"""
Neo4j Database Client
Manages connection to Neo4j knowledge graph.
"""

from typing import Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global driver instance
_neo4j_driver: Optional[AsyncDriver] = None


async def get_neo4j_driver() -> AsyncDriver:
    """Get Neo4j driver instance."""
    global _neo4j_driver
    if _neo4j_driver is None:
        raise Exception("Neo4j driver not initialized")
    return _neo4j_driver


async def init_neo4j() -> None:
    """Initialize Neo4j connection."""
    global _neo4j_driver
    try:
        _neo4j_driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        # Verify connection
        async with _neo4j_driver.session() as session:
            result = await session.run("RETURN 1 as test")
            await result.single()
        logger.info("Neo4j connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {str(e)}")
        raise


async def close_neo4j() -> None:
    """Close Neo4j connection."""
    global _neo4j_driver
    if _neo4j_driver:
        await _neo4j_driver.close()
        logger.info("Neo4j connection closed")
