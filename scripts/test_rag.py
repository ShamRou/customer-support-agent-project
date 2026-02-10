"""Test script for RAG system"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag.retriever import get_retriever
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_search(query: str):
    """Test a single search query"""
    print("\n" + "=" * 70)
    print(f"Query: {query}")
    print("=" * 70)

    retriever = get_retriever()

    if not retriever.ready:
        print("❌ Retriever not ready. Run: python scripts/ingest_documents.py")
        return

    # Get results
    results = retriever.get_relevant_docs(query, n_results=3)

    print(f"\nFound {len(results)} relevant documents:\n")

    for i, result in enumerate(results, 1):
        source = result['metadata'].get('source', 'Unknown')
        section = result['metadata'].get('section', '')
        score = result['score']
        content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']

        print(f"{i}. {source}")
        if section:
            print(f"   Section: {section}")
        print(f"   Score: {score:.4f}")
        print(f"   Preview: {content_preview}\n")


def main():
    """Run test queries"""
    print("=" * 70)
    print("RAG SYSTEM TEST")
    print("=" * 70)

    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please add it to your .env file")
        return

    # Test queries
    test_queries = [
        "How do I connect to Snowflake?",
        "What's included in the Pro plan?",
        "My connection is timing out",
        "Can I set custom alerts?"
    ]

    for query in test_queries:
        test_search(query)
        input("\nPress Enter to continue to next query...")

    # Test full context retrieval
    print("\n" + "=" * 70)
    print("TESTING CONTEXT RETRIEVAL (for LLM)")
    print("=" * 70)

    retriever = get_retriever()
    if retriever.ready:
        query = "How do I connect to BigQuery?"
        print(f"\nQuery: {query}")
        print("\nRetrieved Context:\n")
        context = retriever.search(query, n_results=2)
        print(context)

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
