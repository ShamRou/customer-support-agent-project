"""Vector store using ChromaDB"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path


class VectorStore:
    """Manages vector storage with ChromaDB"""

    def __init__(self, persist_directory: str = "./data/chroma_db", collection_name: str = "datapulse_docs"):
        """
        Initialize vector store

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Create directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        # Note: We provide our own embeddings (OpenAI), so no embedding_function needed
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "DataPulse documentation embeddings"},
            embedding_function=None  # We provide embeddings explicitly
        )

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str]
    ):
        """
        Add documents to the vector store

        Args:
            documents: List of document texts
            embeddings: List of embeddings
            metadatas: List of metadata dicts
            ids: List of document IDs
        """
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(f"Added {len(documents)} documents to collection '{self.collection_name}'")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store

        Args:
            query_embedding: Embedding of the query
            n_results: Number of results to return
            where: Filter on metadata
            where_document: Filter on document content

        Returns:
            Dict with 'ids', 'documents', 'metadatas', 'distances'
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document
        )

        return results

    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        count = self.collection.count()
        return {
            "name": self.collection_name,
            "count": count,
            "persist_directory": self.persist_directory
        }

    def reset_collection(self):
        """Delete all documents from the collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "DataPulse documentation embeddings"}
        )
        print(f"Reset collection '{self.collection_name}'")

    def delete_by_source(self, source: str):
        """Delete all documents from a specific source file"""
        # Get all IDs for this source
        results = self.collection.get(
            where={"source": source}
        )

        if results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"Deleted {len(results['ids'])} documents from source '{source}'")

    def list_sources(self) -> List[str]:
        """List all unique source files in the collection"""
        # Get all documents
        results = self.collection.get()

        # Extract unique sources
        sources = set()
        for metadata in results['metadatas']:
            if 'source' in metadata:
                sources.add(metadata['source'])

        return sorted(list(sources))


class RAGRetriever:
    """High-level retriever combining vector store and embeddings"""

    def __init__(self, vector_store: VectorStore, embedding_manager):
        """
        Initialize retriever

        Args:
            vector_store: VectorStore instance
            embedding_manager: EmbeddingManager instance
        """
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for relevant documents

        Args:
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of dicts with 'content', 'metadata', 'score'
        """
        # Create query embedding
        query_embedding = self.embedding_manager.create_embedding(query)

        # Search vector store
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
            where=filters
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': results['distances'][0][i],
                'id': results['ids'][0][i]
            })

        return formatted_results

    def search_with_context(
        self,
        query: str,
        n_results: int = 3,
        max_tokens: int = 3000
    ) -> str:
        """
        Search and format results as context for LLM

        Args:
            query: Search query
            n_results: Number of results to retrieve
            max_tokens: Maximum tokens in context

        Returns:
            Formatted context string
        """
        results = self.search(query, n_results=n_results)

        # Build context
        context_parts = []
        total_tokens = 0

        for i, result in enumerate(results, 1):
            # Format result
            source = result['metadata'].get('source', 'Unknown')
            section = result['metadata'].get('section', '')
            content = result['content']

            part = f"--- Source: {source}"
            if section:
                part += f" | Section: {section}"
            part += f" ---\n{content}\n"

            # Check token count
            part_tokens = self.embedding_manager.count_tokens(part)
            if total_tokens + part_tokens > max_tokens:
                break

            context_parts.append(part)
            total_tokens += part_tokens

        context = "\n".join(context_parts)

        print(f"\nRetrieved {len(context_parts)} documents ({total_tokens} tokens)")

        return context
