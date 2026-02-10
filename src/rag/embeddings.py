"""Embedding utilities using OpenAI and cost tracking with tiktoken"""
import os
import tiktoken
from typing import List, Dict, Tuple
from openai import OpenAI


class EmbeddingManager:
    """Manages embeddings with cost tracking"""

    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize embedding manager

        Args:
            model: OpenAI embedding model to use
                - text-embedding-3-small: $0.02 per 1M tokens (recommended)
                - text-embedding-3-large: $0.13 per 1M tokens
                - text-embedding-ada-002: $0.10 per 1M tokens (legacy)
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Close enough for counting

        # Cost per 1M tokens (as of 2024)
        self.costs = {
            "text-embedding-3-small": 0.02,
            "text-embedding-3-large": 0.13,
            "text-embedding-ada-002": 0.10
        }

        # Track usage
        self.total_tokens = 0
        self.total_cost = 0.0

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))

    def calculate_cost(self, token_count: int) -> float:
        """Calculate cost for given token count"""
        cost_per_token = self.costs.get(self.model, 0.02) / 1_000_000
        return token_count * cost_per_token

    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for a single text

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        # Count tokens before embedding
        token_count = self.count_tokens(text)

        # Create embedding
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )

        # Track usage
        self.total_tokens += token_count
        cost = self.calculate_cost(token_count)
        self.total_cost += cost

        print(f"   Embedded {token_count} tokens (${cost:.6f})")

        return response.data[0].embedding

    def create_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Create embeddings for multiple texts in batches

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call (max 2048 for OpenAI)

        Returns:
            List of embeddings
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Count tokens in batch
            batch_tokens = sum(self.count_tokens(text) for text in batch)

            # Create embeddings
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )

            # Extract embeddings
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)

            # Track usage
            self.total_tokens += batch_tokens
            cost = self.calculate_cost(batch_tokens)
            self.total_cost += cost

            print(f"   Batch {i//batch_size + 1}: {len(batch)} texts, {batch_tokens} tokens (${cost:.6f})")

        return all_embeddings

    def get_usage_stats(self) -> Dict[str, any]:
        """Get usage statistics"""
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "model": self.model,
            "cost_per_1m_tokens": self.costs.get(self.model, 0.02)
        }

    def print_usage_summary(self):
        """Print usage summary"""
        stats = self.get_usage_stats()
        print("\n" + "=" * 60)
        print("EMBEDDING USAGE SUMMARY")
        print("=" * 60)
        print(f"Model: {stats['model']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"Total Cost: ${stats['total_cost']:.6f}")
        print(f"Cost per 1M tokens: ${stats['cost_per_1m_tokens']}")
        print("=" * 60)


def estimate_embedding_cost(text_length: int, model: str = "text-embedding-3-small") -> Tuple[int, float]:
    """
    Estimate tokens and cost for embedding text

    Args:
        text_length: Character length of text
        model: Embedding model to use

    Returns:
        Tuple of (estimated_tokens, estimated_cost)
    """
    # Rough estimate: 1 token ≈ 4 characters
    estimated_tokens = text_length // 4

    costs = {
        "text-embedding-3-small": 0.02,
        "text-embedding-3-large": 0.13,
        "text-embedding-ada-002": 0.10
    }

    cost_per_token = costs.get(model, 0.02) / 1_000_000
    estimated_cost = estimated_tokens * cost_per_token

    return estimated_tokens, estimated_cost
