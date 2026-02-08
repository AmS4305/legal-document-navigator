"""
Vector store management using ChromaDB
"""

from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import settings
from models.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages ChromaDB vector store for document embeddings"""

    def __init__(
        self,
        collection_name: str = "legal_documents",
        persist_directory: Optional[Path] = None,
    ):
        """
        Initialize the vector store manager

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the vector store
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.CHROMA_DIR
        self.embedding_generator = EmbeddingGenerator()

        # Initialize ChromaDB
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize or load the ChromaDB vector store"""
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_generator,
                persist_directory=str(self.persist_directory),
            )
            logger.info(f"Vector store initialized: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store

        Args:
            documents: List of Document objects to add

        Returns:
            List of document IDs
        """
        try:
            ids = self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = settings.TOP_K_RESULTS,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Search query text
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of most similar Document objects
        """
        try:
            results = self.vectorstore.similarity_search(
                query=query, k=k, filter=filter_dict
            )
            logger.info(f"Found {len(results)} similar documents for query")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = settings.TOP_K_RESULTS,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """
        Search for similar documents with relevance scores

        Args:
            query: Search query text
            k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of tuples (Document, similarity_score)
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query, k=k, filter=filter_dict
            )
            logger.info(f"Found {len(results)} similar documents with scores")
            return results
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {e}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()

            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": str(self.persist_directory),
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by ID

        Args:
            ids: List of document IDs to delete

        Returns:
            Success status
        """
        try:
            self.vectorstore._collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False

    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection

        Returns:
            Success status
        """
        try:
            # Delete the collection and recreate it
            self.vectorstore._client.delete_collection(self.collection_name)
            self._initialize_vectorstore()
            logger.info("Collection cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

    def search_by_metadata(
        self, metadata_filter: Dict[str, Any], k: Optional[int] = None
    ) -> List[Document]:
        """
        Search documents by metadata only

        Args:
            metadata_filter: Metadata filter dictionary
            k: Optional limit on results

        Returns:
            List of matching Document objects
        """
        try:
            # Use a dummy query for metadata-only search
            results = self.vectorstore.get(where=metadata_filter, limit=k)

            # Convert to Document objects
            documents = []
            if results and results.get("documents"):
                for i, doc_text in enumerate(results["documents"]):
                    metadata = (
                        results["metadatas"][i] if results.get("metadatas") else {}
                    )
                    documents.append(Document(page_content=doc_text, metadata=metadata))

            logger.info(f"Found {len(documents)} documents matching metadata filter")
            return documents
        except Exception as e:
            logger.error(f"Error in metadata search: {e}")
            raise
