"""
Neo4j database connection and utilities.
Manages graph database connections for the GraphRAG system.
"""

from typing import Optional, Dict, Any, List
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable, AuthError

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import CarbonSenseException

logger = get_logger(__name__)

# Neo4j driver instance
neo4j_driver: Optional[AsyncDriver] = None


class Neo4jException(CarbonSenseException):
    """Exception raised for Neo4j errors."""
    pass


async def get_neo4j_driver() -> AsyncDriver:
    """
    Get Neo4j driver instance.
    
    Returns:
        Neo4j async driver
        
    Raises:
        Neo4jException: If driver not initialized
    """
    global neo4j_driver
    if neo4j_driver is None:
        raise Neo4jException("Neo4j driver not initialized")
    return neo4j_driver


async def init_neo4j() -> None:
    """Initialize Neo4j connection."""
    global neo4j_driver
    try:
        neo4j_driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
            max_connection_pool_size=50,
            connection_timeout=30.0,
        )
        
        # Verify connectivity
        await neo4j_driver.verify_connectivity()
        logger.info("Neo4j connection established successfully")
        
        # Create constraints and indexes
        await _create_schema()
        
    except AuthError as e:
        logger.error(f"Neo4j authentication failed: {str(e)}")
        raise Neo4jException(f"Neo4j authentication failed: {str(e)}")
    except ServiceUnavailable as e:
        logger.error(f"Neo4j service unavailable: {str(e)}")
        raise Neo4jException(f"Neo4j service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {str(e)}")
        raise Neo4jException(f"Neo4j initialization failed: {str(e)}")


async def close_neo4j() -> None:
    """Close Neo4j connection."""
    global neo4j_driver
    if neo4j_driver:
        await neo4j_driver.close()
        logger.info("Neo4j connection closed")


async def _create_schema() -> None:
    """Create Neo4j schema constraints and indexes."""
    driver = await get_neo4j_driver()
    
    constraints = [
        # Unique constraints for node names
        "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT technique_name IF NOT EXISTS FOR (t:Technique) REQUIRE t.name IS UNIQUE",
        "CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE",
        "CREATE CONSTRAINT resource_name IF NOT EXISTS FOR (r:Resource) REQUIRE r.name IS UNIQUE",
        "CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE",
    ]
    
    indexes = [
        # Full-text search indexes
        "CREATE FULLTEXT INDEX concept_search IF NOT EXISTS FOR (c:Concept) ON EACH [c.name, c.definition]",
        "CREATE FULLTEXT INDEX technique_search IF NOT EXISTS FOR (t:Technique) ON EACH [t.name, t.definition]",
        "CREATE FULLTEXT INDEX domain_search IF NOT EXISTS FOR (d:Domain) ON EACH [d.name, d.definition]",
        
        # Property indexes for filtering
        "CREATE INDEX concept_domain IF NOT EXISTS FOR (c:Concept) ON (c.domain)",
        "CREATE INDEX concept_confidence IF NOT EXISTS FOR (c:Concept) ON (c.confidence)",
    ]
    
    async with driver.session() as session:
        for constraint in constraints:
            try:
                await session.run(constraint)
                logger.info(f"Created constraint: {constraint.split()[2]}")
            except Exception as e:
                logger.warning(f"Constraint creation skipped (may already exist): {str(e)}")
        
        for index in indexes:
            try:
                await session.run(index)
                logger.info(f"Created index: {index.split()[2]}")
            except Exception as e:
                logger.warning(f"Index creation skipped (may already exist): {str(e)}")


async def execute_query(
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    write: bool = False
) -> List[Dict[str, Any]]:
    """
    Execute a Cypher query.
    
    Args:
        query: Cypher query string
        parameters: Query parameters
        write: Whether this is a write operation
        
    Returns:
        List of result records as dictionaries
    """
    driver = await get_neo4j_driver()
    parameters = parameters or {}
    
    async with driver.session() as session:
        if write:
            result = await session.run(query, parameters)
        else:
            result = await session.run(query, parameters)
        
        records = await result.data()
        return records


async def execute_write_transaction(queries: List[tuple[str, Dict[str, Any]]]) -> None:
    """
    Execute multiple write queries in a transaction.
    
    Args:
        queries: List of (query, parameters) tuples
    """
    driver = await get_neo4j_driver()
    
    async def _transaction_work(tx):
        for query, params in queries:
            await tx.run(query, params)
    
    async with driver.session() as session:
        await session.execute_write(_transaction_work)


async def get_node_by_name(name: str, node_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a node by name.
    
    Args:
        name: Node name
        node_type: Optional node type filter (Concept, Technique, etc.)
        
    Returns:
        Node properties or None if not found
    """
    if node_type:
        query = f"MATCH (n:{node_type} {{name: $name}}) RETURN n"
    else:
        query = "MATCH (n {name: $name}) RETURN n"
    
    results = await execute_query(query, {"name": name})
    
    if results:
        return results[0]["n"]
    return None


async def create_node(
    node_type: str,
    properties: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new node.
    
    Args:
        node_type: Node label (Concept, Technique, etc.)
        properties: Node properties
        
    Returns:
        Created node properties
    """
    query = f"""
    CREATE (n:{node_type} $properties)
    RETURN n
    """
    
    results = await execute_query(query, {"properties": properties}, write=True)
    return results[0]["n"]


async def create_relationship(
    from_name: str,
    to_name: str,
    rel_type: str,
    properties: Optional[Dict[str, Any]] = None
) -> None:
    """
    Create a relationship between two nodes.
    
    Args:
        from_name: Source node name
        to_name: Target node name
        rel_type: Relationship type
        properties: Optional relationship properties
    """
    properties = properties or {}
    
    query = f"""
    MATCH (a {{name: $from_name}})
    MATCH (b {{name: $to_name}})
    MERGE (a)-[r:{rel_type}]->(b)
    SET r += $properties
    """
    
    await execute_query(
        query,
        {"from_name": from_name, "to_name": to_name, "properties": properties},
        write=True
    )


async def get_graph_stats() -> Dict[str, int]:
    """
    Get graph statistics.
    
    Returns:
        Dictionary with node and relationship counts
    """
    stats = {}
    
    # Count nodes by type
    node_types = ["Concept", "Technique", "Domain", "Resource", "Tool"]
    for node_type in node_types:
        query = f"MATCH (n:{node_type}) RETURN count(n) as count"
        result = await execute_query(query)
        stats[f"{node_type.lower()}_count"] = result[0]["count"]
    
    # Count total relationships
    query = "MATCH ()-[r]->() RETURN count(r) as count"
    result = await execute_query(query)
    stats["relationship_count"] = result[0]["count"]
    
    return stats
