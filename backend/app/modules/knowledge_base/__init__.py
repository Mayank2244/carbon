"""
Knowledge Base Module - Production RAG System.

PUBLIC API:
- knowledge_base_service: Main entry point
- Document, SearchResult: Domain models
"""
from app.modules.knowledge_base.service import knowledge_base_service
from app.modules.knowledge_base.domain import Document, SearchResult, IngestionStats

__all__ = [
    "knowledge_base_service",
    "Document",
    "SearchResult",
    "IngestionStats"
]
