"""High-level RAG retriever for the chatbot"""
import os
from pathlib import Path
from typing import Optional
from .embeddings import EmbeddingManager
from .vector_store import VectorStore, RAGRetriever


class KnowledgeBaseRetriever:
    """Singleton retriever for knowledge base"""

    _instance: Optional['KnowledgeBaseRetriever'] = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize retriever (only once)"""
        if not self._initialized:
            self._setup()
            self._initialized = True

    def _setup(self):
        """Set up retriever components"""
        # Get paths
        base_dir = Path(__file__).parent.parent.parent
        persist_dir = base_dir / "data" / "chroma_db"

        # Check if vector store exists
        if not persist_dir.exists():
            print("\n⚠️  Warning: Vector database not found!")
            print("Please run: python scripts/ingest_documents.py")
            self.ready = False
            return

        # Initialize components
        try:
            self.embedding_manager = EmbeddingManager(model="text-embedding-3-small")
            self.vector_store = VectorStore(
                persist_directory=str(persist_dir),
                collection_name="datapulse_docs"
            )
            self.retriever = RAGRetriever(self.vector_store, self.embedding_manager)
            self.ready = True

            # Get info
            info = self.vector_store.get_collection_info()
            print(f"\n✅ Knowledge base loaded: {info['count']} documents")

        except Exception as e:
            print(f"\n❌ Error initializing RAG system: {e}")
            self.ready = False

    def search(self, query: str, n_results: int = 3) -> str:
        """
        Search knowledge base and return formatted context

        Args:
            query: Search query
            n_results: Number of results to retrieve

        Returns:
            Formatted context string for LLM
        """
        if not self.ready:
            return "Knowledge base not available. Please run ingestion script."

        try:
            # Get context
            context = self.retriever.search_with_context(
                query=query,
                n_results=n_results,
                max_tokens=3000
            )

            return context

        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return f"Error searching knowledge base: {str(e)}"

    def get_relevant_docs(self, query: str, n_results: int = 3):
        """
        Get relevant documents with metadata

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            List of dicts with content, metadata, score
        """
        if not self.ready:
            return []

        try:
            return self.retriever.search(query, n_results=n_results)
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []


# Global instance
_retriever = None


def get_retriever() -> KnowledgeBaseRetriever:
    """Get or create the global retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = KnowledgeBaseRetriever()
    return _retriever
