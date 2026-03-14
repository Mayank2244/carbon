"""
Domain models for Knowledge Base.

DESIGN RATIONALE:
- Pydantic for runtime validation and serialization
- Explicit field types prevent silent bugs
- Immutable where possible (frozen=True)
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class Document(BaseModel):
    """
    Represents a source document to be ingested.
    
    INVARIANTS:
    - content must be non-empty
    - source must be unique identifier
    """
    content: str = Field(..., min_length=1, description="Raw document text")
    source: str = Field(..., description="Unique identifier (file path, URL, etc)")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional context")


class Chunk(BaseModel):
    """
    Represents a processed text chunk with embedding.
    
    DESIGN NOTE:
    - id is deterministic: hash(source + chunk_index)
    - This prevents duplicate ingestion
    """
    id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = False  # Allow embedding to be set post-creation


class SearchResult(BaseModel):
    """
    Represents a semantic search result.
    
    DESIGN NOTE:
    - distance is cosine distance (lower = more similar)
    - similarity is derived: 1 - distance
    """
    chunk_id: str
    text: str
    similarity: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any]
    source: str


class IngestionStats(BaseModel):
    """Statistics from document ingestion."""
    documents_processed: int
    chunks_created: int
    chunks_stored: int
    duplicates_skipped: int
    duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.now)
