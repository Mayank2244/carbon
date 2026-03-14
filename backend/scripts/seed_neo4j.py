#!/usr/bin/env python
"""
Seed Neo4j Knowledge Graph
Run this script to populate the graph with initial tech concepts.
"""

import asyncio
import os
import sys

# Add app to path if running directly
sys.path.append(os.getcwd())

from app.modules.graph_rag.neo4j_client import init_neo4j, get_neo4j_driver, close_neo4j
from app.modules.graph_rag.seed_data import SEED_DATA_STATEMENTS
from app.core.logging import get_logger

logger = get_logger(__name__)


async def main():
    """Seed the Neo4j database."""
    try:
        # Initialize connection
        await init_neo4j()
        driver = await get_neo4j_driver()
        
        logger.info("Seeding Neo4j knowledge graph...")
        
        async with driver.session() as session:
            count = 0
            for statement in SEED_DATA_STATEMENTS:
                try:
                    await session.run(statement)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to execute statement: {statement[:50]}... Error: {e}")
            
        logger.info(f"Successfully executed {count} statements in knowledge graph")
        
    except Exception as e:
        logger.error(f"Failed to seed database: {e}", exc_info=True)
        raise
    finally:
        await close_neo4j()


if __name__ == "__main__":
    asyncio.run(main())
