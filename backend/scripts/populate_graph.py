"""
Populate Neo4j knowledge graph with initial concepts and relationships.
Supports batch import and Wikipedia expansion.
"""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import wikipediaapi

from app.db.neo4j import (
    init_neo4j,
    close_neo4j,
    create_node,
    create_relationship,
    get_node_by_name,
    get_graph_stats,
    execute_write_transaction
)
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class GraphPopulator:
    """Populates knowledge graph with initial data."""
    
    def __init__(self, data_file: str = "data/initial_concepts.json"):
        """
        Initialize graph populator.
        
        Args:
            data_file: Path to JSON data file
        """
        self.data_file = Path(data_file)
        self.wiki = wikipediaapi.Wikipedia('CarbonSenseAI/1.0', 'en')
    
    async def populate(self, expand_wikipedia: bool = False):
        """
        Populate graph with initial data.
        
        Args:
            expand_wikipedia: Whether to expand concepts using Wikipedia
        """
        logger.info("Starting graph population...")
        
        # Load data
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        
        concepts = data.get('concepts', [])
        relationships = data.get('relationships', [])
        
        logger.info(f"Loaded {len(concepts)} concepts and {len(relationships)} relationships")
        
        # Create nodes in batches
        await self._create_nodes_batch(concepts)
        
        # Create relationships in batches
        await self._create_relationships_batch(relationships)
        
        # Optionally expand with Wikipedia
        if expand_wikipedia:
            await self._expand_from_wikipedia(concepts[:10])  # Expand first 10 concepts
        
        # Print stats
        stats = await get_graph_stats()
        logger.info(f"Graph population complete: {stats}")
    
    async def _create_nodes_batch(self, concepts: List[Dict[str, Any]]):
        """Create nodes in batch transactions."""
        logger.info(f"Creating {len(concepts)} nodes...")
        
        batch_size = 100
        for i in range(0, len(concepts), batch_size):
            batch = concepts[i:i + batch_size]
            queries = []
            
            for concept in batch:
                node_type = concept.get('type', 'Concept')
                properties = {
                    'name': concept['name'],
                    'definition': concept.get('definition', ''),
                    'examples': concept.get('examples', []),
                    'domain': concept.get('domain', ''),
                    'confidence': concept.get('confidence', 1.0),
                    'source': concept.get('source', 'manual')
                }
                
                query = f"""
                MERGE (n:{node_type} {{name: $name}})
                SET n += $properties
                """
                queries.append((query, {'name': concept['name'], 'properties': properties}))
            
            await execute_write_transaction(queries)
            logger.info(f"Created batch {i//batch_size + 1}/{(len(concepts)-1)//batch_size + 1}")
    
    async def _create_relationships_batch(self, relationships: List[Dict[str, Any]]):
        """Create relationships in batch transactions."""
        logger.info(f"Creating {len(relationships)} relationships...")
        
        batch_size = 100
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i + batch_size]
            queries = []
            
            for rel in batch:
                query = f"""
                MATCH (a {{name: $from_name}})
                MATCH (b {{name: $to_name}})
                MERGE (a)-[r:{rel['type']}]->(b)
                SET r.weight = 1.0
                """
                queries.append((query, {
                    'from_name': rel['from'],
                    'to_name': rel['to']
                }))
            
            await execute_write_transaction(queries)
            logger.info(f"Created batch {i//batch_size + 1}/{(len(relationships)-1)//batch_size + 1}")
    
    async def _expand_from_wikipedia(self, concepts: List[Dict[str, Any]]):
        """
        Expand concepts using Wikipedia API.
        
        Args:
            concepts: Concepts to expand
        """
        logger.info(f"Expanding {len(concepts)} concepts from Wikipedia...")
        
        for concept in concepts:
            try:
                page = self.wiki.page(concept['name'])
                
                if not page.exists():
                    logger.warning(f"Wikipedia page not found for: {concept['name']}")
                    continue
                
                # Extract summary as enhanced definition
                summary = page.summary[:500]  # First 500 chars
                
                # Update node with Wikipedia data
                query = """
                MATCH (n {name: $name})
                SET n.wikipedia_summary = $summary,
                    n.wikipedia_url = $url
                """
                await execute_write_transaction([(query, {
                    'name': concept['name'],
                    'summary': summary,
                    'url': page.fullurl
                })])
                
                logger.info(f"Expanded: {concept['name']}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error expanding {concept['name']}: {e}")


async def main():
    """Main execution function."""
    try:
        # Initialize Neo4j
        await init_neo4j()
        
        # Populate graph
        populator = GraphPopulator()
        await populator.populate(expand_wikipedia=False)  # Set to True to enable Wikipedia expansion
        
        logger.info("Graph population completed successfully!")
        
    except Exception as e:
        logger.error(f"Population failed: {e}", exc_info=True)
    finally:
        await close_neo4j()


if __name__ == "__main__":
    asyncio.run(main())
