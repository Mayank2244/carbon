"""Knowledge Base Processing Layer."""
from app.modules.knowledge_base.processing.embedder import embedding_service
from app.modules.knowledge_base.processing.chunker import TextChunker

__all__ = ["embedding_service", "TextChunker"]
