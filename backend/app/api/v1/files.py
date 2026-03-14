"""Files management endpoints."""

import io
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/files", tags=["files"])

class FileResponse(BaseModel):
    filename: str
    content_type: str
    size: int
    text_content: str = None
    
@router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a file. 
    Currently supports PDF parsing.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only PDF files are supported currently."
        )
        
    try:
        content = await file.read()
        file_size = len(content)
        
        # Simple PDF text extraction
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        return FileResponse(
            filename=file.filename,
            content_type=file.content_type,
            size=file_size,
            text_content=text[:5000] # Limit response size, usually we'd store this in vector DB
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
