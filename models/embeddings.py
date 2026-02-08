"""
Embedding generation module using Sentence Transformers
"""

from typing import List
import logging

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from config import settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator(Embeddings):
    """
    Custom embedding generator using Sentence Transformers
    Compatible with LangChain's embedding interface
    """

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        """
        Initialize the embedding model

        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents

        Args:
            texts: List of text documents to embed

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            embeddings = self.model.encode(
                texts, convert_to_numpy=True, show_progress_bar=False
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text

        Args:
            text: Query text to embed

        Returns:
            Embedding as a list of floats
        """
        try:
            embedding = self.model.encode(
                [text], convert_to_numpy=True, show_progress_bar=False
            )[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors

        Returns:
            Dimension of embeddings
        """
        return self.model.get_sentence_embedding_dimension()
