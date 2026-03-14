"""
Confidence scoring for GraphRAG responses.
Calculates confidence based on entity coverage, path quality, and context completeness.
"""

from typing import List
from app.core.logging import get_logger
from app.modules.graph_rag.models import Entity, GraphContext

logger = get_logger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for RAG responses."""
    
    def __init__(self, threshold: float = 0.8):
        """
        Initialize confidence scorer.
        
        Args:
            threshold: Minimum confidence threshold for answering
        """
        self.threshold = threshold
    
    def calculate_confidence(
        self,
        query: str,
        entities: List[Entity],
        context: GraphContext
    ) -> float:
        """
        Calculate overall confidence score for answering the query.
        
        Args:
            query: Original user query
            entities: Extracted entities
            context: Assembled graph context
            
        Returns:
            Confidence score (0-1)
        """
        if not entities or not context.paths:
            return 0.0
        
        # Component scores
        entity_score = self._calculate_entity_score(entities)
        path_score = self._calculate_path_score(context)
        coverage_score = self._calculate_coverage_score(query, context)
        source_score = self._calculate_source_score(context)
        
        # Weighted combination
        confidence = (
            entity_score * 0.3 +
            path_score * 0.3 +
            coverage_score * 0.25 +
            source_score * 0.15
        )
        
        logger.info(
            f"Confidence breakdown - Entity: {entity_score:.2f}, "
            f"Path: {path_score:.2f}, Coverage: {coverage_score:.2f}, "
            f"Source: {source_score:.2f}, Total: {confidence:.2f}"
        )
        
        return min(confidence, 1.0)
    
    def _calculate_entity_score(self, entities: List[Entity]) -> float:
        """
        Score based on entity extraction quality.
        
        Args:
            entities: Extracted entities
            
        Returns:
            Entity quality score (0-1)
        """
        if not entities:
            return 0.0
        
        # Factor 1: Number of entities found (more is better, up to a point)
        count_score = min(len(entities) / 5.0, 1.0)
        
        # Factor 2: Average entity confidence
        avg_confidence = sum(e.confidence for e in entities) / len(entities)
        
        # Factor 3: Percentage matched to graph
        matched_count = sum(1 for e in entities if e.matched_node)
        match_rate = matched_count / len(entities)
        
        # Combine factors
        score = (count_score * 0.3 + avg_confidence * 0.4 + match_rate * 0.3)
        return score
    
    def _calculate_path_score(self, context: GraphContext) -> float:
        """
        Score based on graph path quality.
        
        Args:
            context: Graph context
            
        Returns:
            Path quality score (0-1)
        """
        if not context.paths:
            return 0.0
        
        # Factor 1: Number of paths (more diverse paths = better)
        path_count_score = min(len(context.paths) / 10.0, 1.0)
        
        # Factor 2: Average path relevance
        avg_relevance = sum(p.relevance_score for p in context.paths) / len(context.paths)
        
        # Factor 3: Path diversity (different lengths and structures)
        unique_lengths = len(set(p.length for p in context.paths))
        diversity_score = min(unique_lengths / 3.0, 1.0)
        
        # Combine factors
        score = (path_count_score * 0.3 + avg_relevance * 0.5 + diversity_score * 0.2)
        return score
    
    def _calculate_coverage_score(self, query: str, context: GraphContext) -> float:
        """
        Score based on how well context covers the query.
        
        Args:
            query: Original query
            context: Graph context
            
        Returns:
            Coverage score (0-1)
        """
        query_words = set(query.lower().split())
        
        # Extract all words from context
        context_words = set()
        for path in context.paths:
            for node in path.nodes:
                context_words.update(node.name.lower().split())
                if node.definition:
                    context_words.update(node.definition.lower().split())
        
        # Calculate overlap
        if not query_words:
            return 0.0
        
        overlap = len(query_words & context_words) / len(query_words)
        return overlap
    
    def _calculate_source_score(self, context: GraphContext) -> float:
        """
        Score based on data source quality.
        
        Args:
            context: Graph context
            
        Returns:
            Source quality score (0-1)
        """
        if not context.paths:
            return 0.0
        
        # Collect all nodes
        all_nodes = []
        for path in context.paths:
            all_nodes.extend(path.nodes)
        
        if not all_nodes:
            return 0.0
        
        # Factor 1: Average node confidence
        avg_confidence = sum(n.confidence for n in all_nodes) / len(all_nodes)
        
        # Factor 2: Source diversity (manual > wikipedia > auto)
        source_weights = {"manual": 1.0, "wikipedia": 0.8, "user": 0.7, "auto": 0.5}
        weighted_sources = sum(
            source_weights.get(n.source, 0.5) for n in all_nodes
        ) / len(all_nodes)
        
        # Combine factors
        score = (avg_confidence * 0.6 + weighted_sources * 0.4)
        return score
    
    def should_answer(self, confidence: float) -> bool:
        """
        Determine if confidence is high enough to answer.
        
        Args:
            confidence: Calculated confidence score
            
        Returns:
            True if should answer via RAG, False if should fallback to full LLM
        """
        return confidence >= self.threshold
