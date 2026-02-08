"""
Document processing module for loading and chunking legal documents
"""

from pathlib import Path
from typing import List, Optional
import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document

from config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document loading, parsing, and chunking"""

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )

    def load_document(self, file_path: Path) -> List[Document]:
        """
        Load a document based on its file extension

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects containing the loaded content
        """
        file_extension = file_path.suffix.lower()

        try:
            if file_extension == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif file_extension == ".docx":
                loader = Docx2txtLoader(str(file_path))
            elif file_extension == ".txt":
                loader = TextLoader(str(file_path))
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path.name}")
            return documents

        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunked Document objects
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            return chunks

        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            raise

    def process_file(
        self, file_path: Path, metadata: Optional[dict] = None
    ) -> List[Document]:
        """
        Complete processing pipeline: load and chunk a document

        Args:
            file_path: Path to the document file
            metadata: Optional additional metadata to attach to chunks

        Returns:
            List of processed and chunked Document objects
        """
        # Load the document
        documents = self.load_document(file_path)

        # Add custom metadata if provided
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)

        # Add file-specific metadata
        for doc in documents:
            doc.metadata.update(
                {"source_file": file_path.name, "file_type": file_path.suffix.lower()}
            )

        # Chunk the documents
        chunks = self.chunk_documents(documents)

        return chunks

    def validate_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Validate if a file can be processed

        Args:
            file_path: Path to the file to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file_path.exists():
            return False, "File does not exist"

        # Check file extension
        if file_path.suffix.lower() not in settings.ALLOWED_EXTENSIONS:
            return (
                False,
                f"Unsupported file type. Allowed: {settings.ALLOWED_EXTENSIONS}",
            )

        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            return False, f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"

        return True, ""
