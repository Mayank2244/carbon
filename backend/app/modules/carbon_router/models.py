"""
Carbon Router Models
Data structures for routing decisions.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel

class Region(BaseModel):
    """Data center region configuration."""
    id: str
    name: str
    coordinates: Tuple[float, float]
    endpoints: List[str]
    timezone: str

class RouteResult(BaseModel):
    """Result of a routing calculation."""
    selected_region: str
    selected_endpoint: str
    carbon_intensity: float
    latency_ms: float
    score: float
    reasoning: str
