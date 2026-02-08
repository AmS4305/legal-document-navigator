"""
FastAPI routes for the Legal Document Navigator
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
import shutil

from api.schemas import (
    QueryRequest, QueryResponse,
    SearchRequest, SearchResponse,
    UploadResponse, StatsResponse,
    ErrorResponse, HealthResponse
)
from services.query_service import QueryService
from services.vector_store import VectorStoreManager
from models.document_processor import DocumentProcessor
from config import settings

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize services
query_service = QueryService()
document_processor = DocumentProcessor()
vector_store = VectorStoreManager()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        stats = query_service.get_document_stats()
        vectorstore_status = "healthy" if stats.get("document_count", 0) >= 0 else "error"
        
        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            vectorstore_status=vectorstore_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            vectorstore_status="error"
        )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a legal document (PDF, DOCX, or TXT)
    The document will be processed, chunked, and added to the vector store
    """
    try:
        # Validate file extension
        file_path = Path(file.filename)
        if file_path.suffix.lower() not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Save uploaded file
        upload_path = settings.UPLOAD_DIR / file.filename
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate file
        is_valid, error_msg = document_processor.validate_file(upload_path)
        if not is_valid:
            upload_path.unlink()  # Delete invalid file
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Process the document
        logger.info(f"Processing uploaded file: {file.filename}")
        chunks = document_processor.process_file(upload_path)
        
        # Add to vector store
        document_ids = vector_store.add_documents(chunks)
        
        logger.info(f"Successfully processed {file.filename}: {len(chunks)} chunks created")
        
        return UploadResponse(
            success=True,
            message=f"Document processed successfully",
            filename=file.filename,
            chunks_created=len(chunks),
            document_ids=document_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the legal document collection
    Performs semantic search and generates an answer using LLM
    """
    try:
        logger.info(f"Received query: {request.query[:100]}...")
        
        response = query_service.process_query(
            query=request.query,
            top_k=request.top_k or 5,
            metadata_filter=request.metadata_filter,
            include_sources=request.include_sources if request.include_sources is not None else True
        )
        
        return QueryResponse(**response)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for documents without LLM generation
    Returns raw document chunks ranked by relevance
    """
    try:
        results = query_service.search_documents(
            query=request.query,
            top_k=request.top_k or 10,
            metadata_filter=request.metadata_filter
        )
        
        return SearchResponse(
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about the document collection"""
    try:
        stats = query_service.get_document_stats()
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.get("/documents/{filename}")
async def get_document_chunks(filename: str):
    """
    Get all chunks from a specific document
    """
    try:
        chunks = query_service.find_by_file(filename)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No documents found with filename: {filename}"
            )
        
        return {
            "filename": filename,
            "total_chunks": len(chunks),
            "chunks": chunks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )


@router.delete("/documents")
async def clear_documents():
    """
    Clear all documents from the vector store
    WARNING: This will delete all uploaded documents
    """
    try:
        success = query_service.clear_all_documents()
        
        if success:
            return {
                "success": True,
                "message": "All documents cleared successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear documents"
            )
            
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing documents: {str(e)}"
        )


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Intelligent Legal Document Navigator - RAG System",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "query": "/query",
            "search": "/search",
            "stats": "/stats",
            "docs": "/docs"
        }
    }
