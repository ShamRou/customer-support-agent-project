"""Script to ingest markdown documents into ChromaDB"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag.document_processor import DocumentProcessor, clean_text
from rag.embeddings import EmbeddingManager, estimate_embedding_cost
from rag.vector_store import VectorStore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Main ingestion process"""
    print("=" * 70)
    print("DATAPULSE KNOWLEDGE BASE INGESTION")
    print("=" * 70)

    # Configuration
    docs_dir = Path(__file__).parent.parent / "docs" / "knowledge_base"
    persist_dir = Path(__file__).parent.parent / "data" / "chroma_db"

    print(f"\nDocuments directory: {docs_dir}")
    print(f"Vector DB directory: {persist_dir}")

    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please add it to your .env file:")
        print("OPENAI_API_KEY=sk-...")
        return

    # Step 1: Process documents
    print("\n" + "=" * 70)
    print("STEP 1: PROCESSING DOCUMENTS")
    print("=" * 70)

    processor = DocumentProcessor(
        chunk_size=1000,    # 1000 characters per chunk
        chunk_overlap=200   # 200 character overlap
    )

    documents = processor.process_directory(str(docs_dir), pattern="*.md")

    if not documents:
        print("\n❌ No documents found!")
        return

    # Calculate estimated cost
    total_chars = sum(len(doc.content) for doc in documents)
    est_tokens, est_cost = estimate_embedding_cost(total_chars, model="text-embedding-3-small")

    print(f"\n📊 Statistics:")
    print(f"   Total documents/chunks: {len(documents)}")
    print(f"   Total characters: {total_chars:,}")
    print(f"   Estimated tokens: {est_tokens:,}")
    print(f"   Estimated cost: ${est_cost:.6f}")

    # Ask for confirmation
    print("\n⚠️  This will create embeddings using OpenAI API (costs money)")
    response = input("Continue? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("Aborted.")
        return

    # Step 2: Create embeddings
    print("\n" + "=" * 70)
    print("STEP 2: CREATING EMBEDDINGS")
    print("=" * 70)

    embedding_manager = EmbeddingManager(model="text-embedding-3-small")

    # Clean and prepare texts
    texts = [clean_text(doc.content) for doc in documents]

    # Create embeddings in batches
    print(f"\nCreating embeddings for {len(texts)} documents...")
    embeddings = embedding_manager.create_embeddings_batch(texts, batch_size=100)

    # Print usage
    embedding_manager.print_usage_summary()

    # Step 3: Store in ChromaDB
    print("\n" + "=" * 70)
    print("STEP 3: STORING IN VECTOR DATABASE")
    print("=" * 70)

    vector_store = VectorStore(
        persist_directory=str(persist_dir),
        collection_name="datapulse_docs"
    )

    # Prepare data for storage
    ids = [doc.id for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    # Add to vector store
    vector_store.add_documents(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    # Step 4: Verify
    print("\n" + "=" * 70)
    print("STEP 4: VERIFICATION")
    print("=" * 70)

    info = vector_store.get_collection_info()
    sources = vector_store.list_sources()

    print(f"\n✅ SUCCESS!")
    print(f"   Collection: {info['name']}")
    print(f"   Total documents: {info['count']}")
    print(f"   Source files: {len(sources)}")
    print(f"\nSource files ingested:")
    for source in sources:
        print(f"   - {source}")

    print("\n" + "=" * 70)
    print("INGESTION COMPLETE!")
    print("=" * 70)
    print("\nYou can now use the RAG system in your chatbot.")
    print("Run: python src/main.py")


if __name__ == "__main__":
    main()
