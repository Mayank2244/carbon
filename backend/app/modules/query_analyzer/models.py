"""
Query Analyzer Models
Defines data structures and enums for query classification.
"""

from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class QueryComplexity(str, Enum):
    """Query complexity levels."""
    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    COMPLEX = "COMPLEX"


class QueryIntent(str, Enum):
    """Query intent categories."""
    FACTUAL = "factual"          # Seeking specific information
    CREATIVE = "creative"        # content generation
    TRANSACTIONAL = "transactional"  # Action-oriented
    ANALYTICAL = "analytical"    # Analysis or reasoning
    UNKNOWN = "unknown"


class QueryUrgency(str, Enum):
    """Query urgency levels."""
    URGENT = "urgent"            # Immediate response needed
    TIME_SENSITIVE = "time-sensitive"  # Relevant to current time
    FLEXIBLE = "flexible"        # No rush


class QueryDomain(str, Enum):
    """Query domain categories."""
    TECH = "tech"
    MEDICAL = "medical"
    FINANCE = "finance"
    GENERAL = "general"


class QueryAnalysisResult(BaseModel):
    """Structured result of query analysis."""
    
    query_text: str
    complexity: QueryComplexity
    intent: QueryIntent
    urgency: QueryUrgency
    domain: QueryDomain
    estimated_tokens: int
    requires_context: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}
