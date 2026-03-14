"""
Graph traversal and context assembly for GraphRAG.
Implements depth-limited graph traversal with relevance scoring.
"""

from typing import List, Dict, Any, Set, Tuple
from app.core.logging import get_logger
from app.modules.graph_rag.models import (
    Entity,
    GraphPath,
    GraphNode,
    GraphRelationship,
    NodeType,
    RelationType,
)
from app.db.neo4j import execute_query

logger = get_logger(__name__)


class GraphTraversal:
    """Handles graph traversal and path finding."""
    
    def __init__(self, max_depth: int = 3):
        """
        Initialize graph traversal.
        
        Args:
            max_depth: Maximum traversal depth (number of hops)
        """
        self.max_depth = max_depth
    
    async def find_paths(
        self,
        entities: List[Entity],
        max_paths: int = 10
    ) -> List[GraphPath]:
        """
        Find relevant paths connecting extracted entities.
        
        Args:
            entities: Extracted entities from query
            max_paths: Maximum number of paths to return
            
        Returns:
            List of graph paths with relevance scores
        """
        if not entities:
            return []
        
        # Filter to entities that matched graph nodes
        matched_entities = [e for e in entities if e.matched_node]
        
        if not matched_entities:
            logger.warning("No entities matched to graph nodes")
            return []
        
        paths = []
        
        # Strategy 1: Direct paths between entity pairs
        if len(matched_entities) >= 2:
            pair_paths = await self._find_paths_between_pairs(matched_entities)
            paths.extend(pair_paths)
        
        # Strategy 2: Expand from each entity
        for entity in matched_entities[:3]:  # Limit to top 3 entities
            expansion_paths = await self._expand_from_entity(entity)
            paths.extend(expansion_paths)
        
        # Score and rank paths
        scored_paths = self._score_paths(paths, entities)
        scored_paths.sort(key=lambda p: p.relevance_score, reverse=True)
        
        # Deduplicate and limit
        unique_paths = self._deduplicate_paths(scored_paths)
        result = unique_paths[:max_paths]
        
        logger.info(f"Found {len(result)} relevant paths from {len(matched_entities)} entities")
        return result
    
    async def _find_paths_between_pairs(
        self,
        entities: List[Entity]
    ) -> List[GraphPath]:
        """Find paths between pairs of entities."""
        paths = []
        
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity_paths = await self._find_shortest_paths(
                    entities[i].matched_node,
                    entities[j].matched_node
                )
                paths.extend(entity_paths)
        
        return paths
    
    async def _find_shortest_paths(
        self,
        from_node: str,
        to_node: str,
        limit: int = 3
    ) -> List[GraphPath]:
        """
        Find shortest paths between two nodes.
        
        Args:
            from_node: Source node name
            to_node: Target node name
            limit: Maximum number of paths to return
            
        Returns:
            List of paths
        """
        query = f"""
        MATCH path = shortestPath((a {{name: $from_node}})-[*..{self.max_depth}]-(b {{name: $to_node}}))
        RETURN path
        LIMIT {limit}
        """
        
        results = await execute_query(query, {
            "from_node": from_node,
            "to_node": to_node
        })
        
        paths = []
        for result in results:
            path_data = result["path"]
            graph_path = self._convert_neo4j_path(path_data)
            if graph_path:
                paths.append(graph_path)
        
        return paths
    
    async def _expand_from_entity(
        self,
        entity: Entity,
        limit: int = 5
    ) -> List[GraphPath]:
        """
        Expand from a single entity to find relevant context.
        
        Args:
            entity: Entity to expand from
            limit: Maximum paths to return
            
        Returns:
            List of paths
        """
        query = f"""
        MATCH path = (start {{name: $entity_name}})-[*1..{self.max_depth}]-(end)
        WHERE start <> end
        WITH path, length(path) as pathLength
        ORDER BY pathLength ASC
        RETURN path
        LIMIT {limit}
        """
        
        results = await execute_query(query, {"entity_name": entity.matched_node})
        
        paths = []
        for result in results:
            path_data = result["path"]
            graph_path = self._convert_neo4j_path(path_data)
            if graph_path:
                paths.append(graph_path)
        
        return paths
    
    def _convert_neo4j_path(self, neo4j_path: Any) -> GraphPath:
        """
        Convert Neo4j path object to GraphPath model.
        
        Args:
            neo4j_path: Neo4j path object
            
        Returns:
            GraphPath instance
        """
        try:
            nodes = []
            relationships = []
            
            # Extract nodes
            for neo4j_node in neo4j_path.nodes:
                node = GraphNode(
                    name=neo4j_node.get("name", "Unknown"),
                    node_type=NodeType(list(neo4j_node.labels)[0]),
                    definition=neo4j_node.get("definition"),
                    examples=neo4j_node.get("examples", []),
                    domain=neo4j_node.get("domain"),
                    confidence=neo4j_node.get("confidence", 1.0),
                    source=neo4j_node.get("source", "unknown"),
                    properties=dict(neo4j_node)
                )
                nodes.append(node)
            
            # Extract relationships
            for neo4j_rel in neo4j_path.relationships:
                rel = GraphRelationship(
                    from_node=neo4j_rel.start_node.get("name", "Unknown"),
                    to_node=neo4j_rel.end_node.get("name", "Unknown"),
                    rel_type=RelationType(neo4j_rel.type),
                    weight=neo4j_rel.get("weight", 1.0),
                    properties=dict(neo4j_rel)
                )
                relationships.append(rel)
            
            return GraphPath(
                nodes=nodes,
                relationships=relationships,
                relevance_score=0.5,  # Will be scored later
                length=len(relationships)
            )
        except Exception as e:
            logger.error(f"Error converting Neo4j path: {e}")
            return None
    
    def _score_paths(
        self,
        paths: List[GraphPath],
        query_entities: List[Entity]
    ) -> List[GraphPath]:
        """
        Score paths based on relevance to query.
        
        Args:
            paths: Paths to score
            query_entities: Original query entities
            
        Returns:
            Paths with updated relevance scores
        """
        entity_names = {e.matched_node for e in query_entities if e.matched_node}
        
        for path in paths:
            score = 0.0
            
            # Factor 1: Entity coverage (0-0.4)
            node_names = {node.name for node in path.nodes}
            coverage = len(node_names & entity_names) / max(len(entity_names), 1)
            score += coverage * 0.4
            
            # Factor 2: Path length (0-0.3, shorter is better)
            length_score = max(0, 1 - (path.length / self.max_depth))
            score += length_score * 0.3
            
            # Factor 3: Node confidence (0-0.2)
            avg_confidence = sum(n.confidence for n in path.nodes) / len(path.nodes)
            score += avg_confidence * 0.2
            
            # Factor 4: Relationship types (0-0.1)
            # Prefer hierarchical relationships
            hierarchical_rels = sum(
                1 for r in path.relationships
                if r.rel_type in [RelationType.IS_A, RelationType.PART_OF]
            )
            rel_score = hierarchical_rels / max(len(path.relationships), 1)
            score += rel_score * 0.1
            
            path.relevance_score = min(score, 1.0)
        
        return paths
    
    def _deduplicate_paths(self, paths: List[GraphPath]) -> List[GraphPath]:
        """
        Remove duplicate or highly similar paths.
        
        Args:
            paths: Paths to deduplicate
            
        Returns:
            Deduplicated paths
        """
        seen_signatures = set()
        unique_paths = []
        
        for path in paths:
            # Create signature from node names
            signature = tuple(node.name for node in path.nodes)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_paths.append(path)
        
        return unique_paths
