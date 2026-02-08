"""
Pydantic schemas for API request and response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for querying documents"""
    query: str = Field(..., min_length=1, description="The search query or question")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of documents to retrieve")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="Optional metadata filters")
    include_sources: Optional[bool] = Field(True, description="Whether to include source documents")


class SourceDocument(BaseModel):
    """Schema for source document information"""
    file: str = Field(..., description="Source file name")
    page: str = Field(..., description="Page number or location")
    snippet: str = Field(..., description="Relevant text snippet")


class QueryResponse(BaseModel):
    """Response schema for query results"""
    answer: str = Field(..., description="Generated answer to the query")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")
    confidence: str = Field(..., description="Confidence level: high, medium, low, none")
    documents_searched: int = Field(..., description="Total documents searched")
    relevant_documents: Optional[int] = Field(None, description="Number of relevant documents found")


class SearchRequest(BaseModel):
    """Request schema for document search"""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: Optional[int] = Field(10, ge=1, le=50, description="Number of results")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class DocumentResult(BaseModel):
    """Schema for a single document search result"""
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    source_file: str = Field(..., description="Source file name")
    page: str = Field(..., description="Page number")


class SearchResponse(BaseModel):
    """Response schema for document search"""
    results: List[DocumentResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Number of results returned")


class UploadResponse(BaseModel):
    """Response schema for document upload"""
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Status message")
    filename: str = Field(..., description="Name of uploaded file")
    chunks_created: Optional[int] = Field(None, description="Number of chunks created")
    document_ids: Optional[List[str]] = Field(None, description="IDs of created documents")


class StatsResponse(BaseModel):
    """Response schema for collection statistics"""
    collection_name: str = Field(..., description="Name of the collection")
    document_count: int = Field(..., description="Total number of document chunks")
    persist_directory: str = Field(..., description="Storage directory path")


class ErrorResponse(BaseModel):
    """Response schema for errors"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    vectorstore_status: str = Field(..., description="Vector store status")
