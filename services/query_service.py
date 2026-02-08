"""
Query service that orchestrates the RAG pipeline
"""

from typing import List, Dict, Any, Optional
import logging

from langchain_core.documents import Document

from models.document_processor import DocumentProcessor
from models.llm_handler import LLMHandler
from services.vector_store import VectorStoreManager
from config import settings

logger = logging.getLogger(__name__)


class QueryService:
    """
    Orchestrates the complete RAG pipeline:
    1. Receive query
    2. Retrieve relevant documents from vector store
    3. Generate response using LLM with context
    """

    def __init__(self):
        """Initialize the query service with all required components"""
        self.vector_store = VectorStoreManager()
        self.llm_handler = LLMHandler()
        self.document_processor = DocumentProcessor()
        logger.info("Query service initialized")

    def process_query(
        self,
        query: str,
        top_k: int = settings.TOP_K_RESULTS,
        metadata_filter: Optional[Dict[str, Any]] = None,
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline

        Args:
            query: User's natural language query
            top_k: Number of relevant documents to retrieve
            metadata_filter: Optional filter to narrow document search
            include_sources: Whether to include source documents in response

        Returns:
            Dictionary containing answer, sources, and metadata
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")

            # Step 1: Retrieve relevant documents
            retrieved_docs = self.vector_store.similarity_search_with_score(
                query=query, k=top_k, filter_dict=metadata_filter
            )

            if not retrieved_docs:
                return {
                    "answer": "I couldn't find any relevant documents to answer your question. Please try rephrasing or upload more documents.",
                    "sources": [],
                    "confidence": "none",
                    "documents_searched": 0,
                }

            # Log the scores for debugging
            for doc, score in retrieved_docs:
                logger.info(
                    f"Document score: {score:.4f} - {doc.metadata.get('source_file', 'Unknown')[:50]}"
                )

            # Filter by similarity threshold
            # ChromaDB uses L2 distance where lower is better
            # Typical range is 0-2, so we use threshold directly as max allowed distance
            max_distance = (
                1.0 + settings.SIMILARITY_THRESHOLD
            )  # With 0.3 threshold, max distance = 1.3
            filtered_docs = [
                (doc, score) for doc, score in retrieved_docs if score <= max_distance
            ]

            if not filtered_docs:
                return {
                    "answer": "I found some documents, but none were sufficiently relevant to your question. Please try rephrasing.",
                    "sources": [],
                    "confidence": "low",
                    "documents_searched": len(retrieved_docs),
                }

            # Extract documents without scores for LLM
            context_docs = [doc for doc, score in filtered_docs]

            # Step 2: Generate response using LLM
            llm_response = self.llm_handler.generate_response(
                query=query, context_docs=context_docs
            )

            # Step 3: Compile full response
            response = {
                "answer": llm_response["answer"],
                "sources": llm_response["sources"] if include_sources else [],
                "confidence": self._calculate_confidence(filtered_docs),
                "documents_searched": len(retrieved_docs),
                "relevant_documents": len(filtered_docs),
            }

            logger.info(
                f"Query processed successfully. Found {len(filtered_docs)} relevant documents"
            )
            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "sources": [],
                "confidence": "error",
                "documents_searched": 0,
            }

    def _calculate_confidence(
        self, docs_with_scores: List[tuple[Document, float]]
    ) -> str:
        """
        Calculate confidence level based on similarity scores

        Args:
            docs_with_scores: List of (Document, score) tuples

        Returns:
            Confidence level as string
        """
        if not docs_with_scores:
            return "none"

        # Get best score (lowest distance in ChromaDB)
        best_score = min(score for _, score in docs_with_scores)

        # Convert distance to similarity (approximate)
        similarity = 1.0 - best_score

        if similarity >= 0.85:
            return "high"
        elif similarity >= 0.70:
            return "medium"
        else:
            return "low"

    def get_document_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the document collection

        Returns:
            Dictionary with collection statistics
        """
        return self.vector_store.get_collection_stats()

    def search_documents(
        self,
        query: str,
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for documents without generating an LLM response

        Args:
            query: Search query
            top_k: Number of results to return
            metadata_filter: Optional metadata filter

        Returns:
            List of document dictionaries with metadata
        """
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query, k=top_k, filter_dict=metadata_filter
            )

            documents = []
            for doc, score in results:
                documents.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": 1.0
                        - score,  # Convert distance to similarity
                        "source_file": doc.metadata.get("source_file", "Unknown"),
                        "page": doc.metadata.get("page", "N/A"),
                    }
                )

            return documents

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def find_by_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Find all chunks from a specific file

        Args:
            filename: Name of the source file

        Returns:
            List of document chunks from that file
        """
        try:
            docs = self.vector_store.search_by_metadata(
                metadata_filter={"source_file": filename}
            )

            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "page": doc.metadata.get("page", "N/A"),
                }
                for doc in docs
            ]

        except Exception as e:
            logger.error(f"Error finding documents by file: {e}")
            return []

    def clear_all_documents(self) -> bool:
        """
        Clear all documents from the vector store

        Returns:
            Success status
        """
        return self.vector_store.clear_collection()
