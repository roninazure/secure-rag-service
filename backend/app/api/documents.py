from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.rag_service import rag_service
import datetime

router = APIRouter()

class DocumentIngestionRequest(BaseModel):
    documents: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None

class DocumentIngestionResponse(BaseModel):
    success: bool
    message: str
    document_count: int
    chunk_count: int
    doc_ids: List[str]
    timestamp: datetime.datetime

class SystemStatusResponse(BaseModel):
    status: str
    vector_database: Dict[str, Any]
    embedding_model: str
    text_generation_model: str
    configuration: Dict[str, Any]
    timestamp: datetime.datetime

@router.post("/ingest", response_model=DocumentIngestionResponse)
async def ingest_documents(request: DocumentIngestionRequest):
    """Ingest documents into the RAG system"""
    try:
        result = await rag_service.ingest_documents(
            documents=request.documents,
            metadata=request.metadata
        )
        
        if result["success"]:
            return DocumentIngestionResponse(
                success=True,
                message=result["message"],
                document_count=result["document_count"],
                chunk_count=result.get("chunk_count", result["document_count"]),
                doc_ids=result["doc_ids"],
                timestamp=datetime.datetime.now()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Document ingestion failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        print(f"Document ingestion endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest documents: {str(e)}"
        )

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get RAG system status and statistics"""
    try:
        status = await rag_service.get_system_status()
        
        return SystemStatusResponse(
            status=status["status"],
            vector_database=status.get("vector_database", {}),
            embedding_model=status.get("embedding_model", "unknown"),
            text_generation_model=status.get("text_generation_model", "unknown"),
            configuration=status.get("configuration", {}),
            timestamp=datetime.datetime.now()
        )
        
    except Exception as e:
        print(f"System status endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system status: {str(e)}"
        )
