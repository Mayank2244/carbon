"""
Pydantic models for GraphRAG system.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class NodeType(str, Enum):
    """Graph node types."""
    CONCEPT = "Concept"
    TECHNIQUE = "Technique"
    DOMAIN = "Domain"
    RESOURCE = "Resource"
    TOOL = "Tool"


class RelationType(str, Enum):
    """Graph relationship types."""
    IS_A = "IS_A"
    USES = "USES"
    APPLIED_IN = "APPLIED_IN"
    REQUIRES = "REQUIRES"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"


class GraphNode(BaseModel):
    """Represents a node in the knowledge graph."""
    
    name: str = Field(..., description="Node name/identifier")
    node_type: NodeType = Field(..., description="Type of node")
    definition: Optional[str] = Field(None, description="Node definition/description")
    examples: List[str] = Field(default_factory=list, description="Usage examples")
    domain: Optional[str] = Field(None, description="Primary domain")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Data quality score")
    source: str = Field(default="manual", description="Data source")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        use_enum_values = True


class GraphRelationship(BaseModel):
    """Represents a relationship between nodes."""
    
    from_node: str = Field(..., description="Source node name")
    to_node: str = Field(..., description="Target node name")
    rel_type: RelationType = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, ge=0.0, description="Relationship strength")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        use_enum_values = True


class GraphPath(BaseModel):
    """Represents a path through the knowledge graph."""
    
    nodes: List[GraphNode] = Field(..., description="Nodes in the path")
    relationships: List[GraphRelationship] = Field(..., description="Relationships in the path")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Path relevance to query")
    length: int = Field(..., ge=1, description="Path length (number of hops)")
    
    def __str__(self) -> str:
        """String representation of path."""
        path_str = self.nodes[0].name
        for i, rel in enumerate(self.relationships):
            path_str += f" -[{rel.rel_type}]-> {self.nodes[i+1].name}"
        return path_str


class Entity(BaseModel):
    """Extracted entity from query."""
    
    text: str = Field(..., description="Entity text as appears in query")
    normalized: str = Field(..., description="Normalized entity name")
    node_type: Optional[NodeType] = Field(None, description="Matched node type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    matched_node: Optional[str] = Field(None, description="Matched graph node name")
    
    class Config:
        use_enum_values = True


class GraphContext(BaseModel):
    """Assembled context from graph traversal."""
    
    query: str = Field(..., description="Original query")
    entities: List[Entity] = Field(..., description="Extracted entities")
    paths: List[GraphPath] = Field(..., description="Relevant graph paths")
    total_nodes: int = Field(..., description="Total unique nodes in context")
    total_relationships: int = Field(..., description="Total relationships in context")
    traversal_depth: int = Field(..., description="Maximum traversal depth used")
    
    def get_context_text(self) -> str:
        """
        Generate text representation of graph context.
        
        Returns:
            Formatted context string
        """
        lines = [f"Query: {self.query}\n"]
        lines.append(f"Entities found: {', '.join([e.normalized for e in self.entities])}\n")
        lines.append(f"\nKnowledge Graph Context ({len(self.paths)} paths):\n")
        
        for i, path in enumerate(self.paths, 1):
            lines.append(f"\nPath {i} (relevance: {path.relevance_score:.2f}):")
            
            # Add node definitions
            for node in path.nodes:
                if node.definition:
                    lines.append(f"  - {node.name} ({node.node_type}): {node.definition}")
                else:
                    lines.append(f"  - {node.name} ({node.node_type})")
            
            # Add path structure
            lines.append(f"  Path: {str(path)}")
        
        return "\n".join(lines)


class RAGResponse(BaseModel):
    """Final RAG response with citations."""
    
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Answer confidence")
    used_graph_rag: bool = Field(..., description="Whether GraphRAG was used")
    used_small_llm: bool = Field(default=False, description="Whether small LLM was used")
    fallback_to_full_llm: bool = Field(default=False, description="Whether full LLM was needed")
    
    # Context and citations
    graph_context: Optional[GraphContext] = Field(None, description="Graph context used")
    citations: List[str] = Field(default_factory=list, description="Source citations")
    
    # Metrics
    entities_found: int = Field(default=0, description="Number of entities extracted")
    paths_explored: int = Field(default=0, description="Number of graph paths explored")
    nodes_traversed: int = Field(default=0, description="Total nodes in context")
    query_time_ms: float = Field(..., description="Total query time in milliseconds")
    
    # Carbon tracking
    estimated_carbon_g: float = Field(..., description="Estimated carbon footprint in grams")
    carbon_saved_g: Optional[float] = Field(None, description="Carbon saved vs full LLM")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is machine learning?",
                "answer": "Machine learning is a subset of artificial intelligence...",
                "confidence": 0.92,
                "used_graph_rag": True,
                "used_small_llm": True,
                "fallback_to_full_llm": False,
                "citations": ["Machine Learning (Concept)", "Artificial Intelligence (Concept)"],
                "entities_found": 2,
                "paths_explored": 5,
                "nodes_traversed": 8,
                "query_time_ms": 45.2,
                "estimated_carbon_g": 0.5,
                "carbon_saved_g": 4.5
            }
        }
