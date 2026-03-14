"""
Entity extraction pipeline for GraphRAG (Lightweight).
Uses custom pattern matching to extract technical entities from queries.
"""

import re
from typing import List, Optional, Set

from app.core.logging import get_logger
from app.modules.graph_rag.models import Entity, NodeType

logger = get_logger(__name__)


class EntityExtractor:
    """Extracts technical entities from user queries (Lightweight version)."""
    
    def __init__(self):
        self._known_entities_cache: Set[str] = set()
        
    async def extract_entities(self, query: str) -> List[Entity]:
        """
        Extract entities from query using pattern matching.
        """
        
        entities = []
        seen_texts = set()
        
        # Strategy 1: Technical term patterns
        tech_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Title case (e.g., "Machine Learning")
            r'\b[A-Z]{2,}\b',  # Acronyms (e.g., "API", "ML")
            r'\b\w+(?:\.js|\.py|SQL|DB)\b',  # Tech suffixes
        ]
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, query)
            for match in matches:
                text = match.group()
                normalized = self._normalize_text(text)
                if normalized not in seen_texts and len(normalized) > 2:
                    entities.append(Entity(
                        text=text,
                        normalized=normalized,
                        confidence=0.6,
                    ))
                    seen_texts.add(normalized)
        
        # Sort by confidence
        entities.sort(key=lambda x: x.confidence, reverse=True)
        return entities
    
    def _normalize_text(self, text: str) -> str:
        """Normalize entity text."""
        # Remove special characters, convert to title case
        text = re.sub(r'[^\w\s-]', '', text)
        text = text.strip()
        return ' '.join(word.capitalize() for word in text.split())

    async def link_entities_to_graph(self, entities: List[Entity]) -> List[Entity]:
        """
        Link extracted entities to actual graph nodes (Stub).
        """
        return entities
