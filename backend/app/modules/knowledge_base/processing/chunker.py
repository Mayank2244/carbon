"""
Text Chunking Strategy.

DESIGN RATIONALE:
- Fixed-size chunks with overlap preserve context across boundaries
- Metadata preservation enables source traceability
- Deterministic IDs prevent duplicate ingestion

CHUNKING STRATEGY TRADE-OFFS:
- Smaller chunks: More precise retrieval, but lose context
- Larger chunks: More context, but less precise matching
- Overlap: Prevents context loss at boundaries, but increases storage

CHOSEN STRATEGY: 512 chars with 64 char overlap
- Balances precision and context for technical documentation
- ~100-150 tokens per chunk (optimal for most embedding models)
"""
import hashlib
from typing import List
from app.modules.knowledge_base.domain import Document, Chunk
from app.modules.knowledge_base.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.core.logging import get_logger

logger = get_logger(__name__)


class TextChunker:
    """
    Splits documents into overlapping chunks.
    
    INVARIANT: All chunks from same document share source metadata.
    """
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        """
        Args:
            chunk_size: Target characters per chunk
            overlap: Characters to overlap between chunks
        
        VALIDATION: overlap must be < chunk_size
        """
        if overlap >= chunk_size:
            raise ValueError(f"Overlap ({overlap}) must be < chunk_size ({chunk_size})")
        
        self.chunk_size = chunk_size
        self.overlap = overlap
        logger.info(f"TextChunker initialized: size={chunk_size}, overlap={overlap}")
    
    def chunk_document(self, document: Document) -> List[Chunk]:
        """
        Split document into chunks with metadata preservation.
        
        ALGORITHM:
        1. Slide window of size `chunk_size` with step `chunk_size - overlap`
        2. Generate deterministic ID: hash(source + chunk_index)
        3. Preserve source metadata in each chunk
        
        Returns:
            List of Chunk objects (embeddings not yet populated)
        """
        text = document.content
        chunks: List[Chunk] = []
        
        if not text or not text.strip():
            logger.warning(f"Document {document.source} has empty content")
            return chunks
        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end].strip()
            
            if not chunk_text:
                break
            
            # Generate deterministic ID
            chunk_id = self._generate_chunk_id(document.source, chunk_index)
            
            # Preserve metadata
            chunk_metadata = {
                **document.metadata,
                "source": document.source,
                "chunk_index": chunk_index,
                "start_char": start,
                "end_char": end
            }
            
            chunk = Chunk(
                id=chunk_id,
                text=chunk_text,
                metadata=chunk_metadata
            )
            chunks.append(chunk)
            
            # Move window
            start += (self.chunk_size - self.overlap)
            chunk_index += 1
        
        logger.info(f"Document '{document.source}' split into {len(chunks)} chunks")
        return chunks
    
    def _generate_chunk_id(self, source: str, index: int) -> str:
        """
        Generate deterministic chunk ID.
        
        RATIONALE: Deterministic IDs enable:
        - Duplicate detection
        - Idempotent ingestion
        - Update-in-place semantics
        """
        content = f"{source}::{index}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
