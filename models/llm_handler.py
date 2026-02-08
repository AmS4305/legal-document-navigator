"""
LLM integration module for generating responses using NVIDIA API
"""

from typing import List, Optional
import logging
import requests

from langchain_core.documents import Document

from config import settings

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles interaction with NVIDIA's LLM API"""

    def __init__(self, api_key: Optional[str] = None, model: str = settings.LLM_MODEL):
        """
        Initialize the LLM handler

        Args:
            api_key: NVIDIA API key (falls back to settings if not provided)
            model: Model identifier to use
        """
        self.api_key = api_key or settings.NVIDIA_API_KEY
        self.model = model
        self.base_url = settings.NVIDIA_BASE_URL

        logger.info(f"LLM Handler initialized with model: {self.model}")

        if not self.api_key:
            logger.warning("NVIDIA API key not set. LLM functionality will be limited.")

    def _build_prompt(self, query: str, context_docs: List[Document]) -> str:
        """
        Build a prompt with context from retrieved documents

        Args:
            query: User's query
            context_docs: Retrieved relevant documents

        Returns:
            Formatted prompt string
        """
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            source = doc.metadata.get("source_file", "Unknown")
            page = doc.metadata.get("page", "N/A")
            context_parts.append(
                f"[Document {i} - Source: {source}, Page: {page}]\n{doc.page_content}\n"
            )

        context = "\n".join(context_parts)

        # Create the full prompt
        prompt = f"""You are a legal document assistant. Your task is to answer questions based solely on the provided legal documents.

CONTEXT DOCUMENTS:
{context}

USER QUESTION:
{query}

INSTRUCTIONS:
- Provide a clear, accurate answer based on the context documents above
- If the answer isn't in the documents, say so clearly
- Cite which document and page number you're referencing when possible
- Use legal precision in your language
- If multiple documents have relevant information, synthesize them appropriately

ANSWER:"""

        return prompt

    def generate_response(
        self,
        query: str,
        context_docs: List[Document],
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> dict:
        """
        Generate a response using the NVIDIA API

        Args:
            query: User's query
            context_docs: Retrieved relevant documents for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (lower = more focused)

        Returns:
            Dictionary with 'answer' and 'sources' keys
        """
        if not self.api_key:
            return {
                "answer": "LLM API key not configured. Please set NVIDIA_API_KEY in your environment.",
                "sources": [],
            }

        try:
            # Build the prompt
            prompt = self._build_prompt(query, context_docs)

            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            # Extract answer
            answer = result["choices"][0]["message"]["content"]

            # Compile sources
            sources = [
                {
                    "file": doc.metadata.get("source_file", "Unknown"),
                    "page": doc.metadata.get("page", "N/A"),
                    "snippet": doc.page_content[:200] + "...",
                }
                for doc in context_docs
            ]

            logger.info(f"Generated response for query: {query[:50]}...")

            return {"answer": answer, "sources": sources}

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"answer": f"Error generating response: {str(e)}", "sources": []}
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"answer": f"Error: {str(e)}", "sources": []}

    def generate_simple_response(self, query: str, context_docs: List[Document]) -> str:
        """
        Generate a simple text response (convenience method)

        Args:
            query: User's query
            context_docs: Retrieved relevant documents

        Returns:
            Generated answer as string
        """
        result = self.generate_response(query, context_docs)
        return result["answer"]
