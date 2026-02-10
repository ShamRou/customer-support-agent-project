# RAG System Documentation

## Overview

This project implements a Retrieval-Augmented Generation (RAG) system to provide accurate, contextual answers from the DataPulse knowledge base.

## Architecture

```
User Query
    ↓
Agent (Claude)
    ↓
search_documentation tool
    ↓
RAG Retriever
    ├─ OpenAI Embedding (query)
    ├─ ChromaDB (vector search)
    └─ Return relevant docs
    ↓
Claude generates answer
    ↓
Response to user
```

## Components

### 1. Document Processing (`src/rag/document_processor.py`)
- Loads markdown files from knowledge base
- Splits documents into chunks (1000 chars, 200 overlap)
- Extracts metadata (source, title, section)
- Cleans text for better embeddings

### 2. Embeddings (`src/rag/embeddings.py`)
- Uses OpenAI `text-embedding-3-small` model
- Tracks token usage with tiktoken
- Calculates costs ($0.02 per 1M tokens)
- Batch processing for efficiency

### 3. Vector Store (`src/rag/vector_store.py`)
- ChromaDB for persistent vector storage
- Stores document embeddings
- Performs similarity search
- Supports metadata filtering

### 4. Retriever (`src/rag/retriever.py`)
- High-level interface for the agent
- Combines embedding + vector search
- Returns formatted context for LLM
- Manages token limits

## Setup

### 1. Install Dependencies

```bash
cd /Users/roumilishams/Desktop/Pro\ 2025/customer-support-agent-project

# Create virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Add to `.env` file:

```bash
# Anthropic API for Claude
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI API for embeddings
OPENAI_API_KEY=sk-...
```

### 3. Ingest Documents

Run the ingestion script to build the vector database:

```bash
python scripts/ingest_documents.py
```

**What it does**:
1. Reads all markdown files from `docs/knowledge_base/`
2. Splits into chunks
3. Creates embeddings using OpenAI
4. Stores in ChromaDB at `data/chroma_db/`

**Cost**: ~$0.01 for 15 documents (~138 KB)

**Output**:
```
DATAPULSE KNOWLEDGE BASE INGESTION
======================================================================

STEP 1: PROCESSING DOCUMENTS
Found 15 markdown files
...
Total documents: 150 chunks

📊 Statistics:
   Total documents/chunks: 150
   Total characters: 140,000
   Estimated tokens: 35,000
   Estimated cost: $0.0007

Continue? (yes/no): yes

STEP 2: CREATING EMBEDDINGS
Creating embeddings for 150 documents...
...

EMBEDDING USAGE SUMMARY
Total Tokens: 35,421
Total Cost: $0.000708

STEP 3: STORING IN VECTOR DATABASE
Added 150 documents to collection 'datapulse_docs'

STEP 4: VERIFICATION
✅ SUCCESS!
   Collection: datapulse_docs
   Total documents: 150
   Source files: 15

INGESTION COMPLETE!
```

## Usage

### In the Chatbot

The RAG system is automatically used when users ask questions:

```python
# User asks: "How do I connect to Snowflake?"
# Agent calls: search_documentation("How do I connect to Snowflake?")
# RAG returns relevant context from docs/knowledge_base/02_snowflake_integration.md
# Agent generates answer based on retrieved context
```

**Run the chatbot**:
```bash
python src/main.py
```

**Example conversation**:
```
You: How do I set up Snowflake integration?

🔧 Using tool: search_documentation
   Input: {'query': 'How do I set up Snowflake integration?'}
   🔍 Searching knowledge base for: 'How do I set up Snowflake integration?'

Retrieved 3 documents (2850 tokens)
   Result: [Retrieved context from Snowflake integration guide]

🤖 Agent: To set up Snowflake integration with DataPulse, follow these steps:

1. Create a DataPulse user in Snowflake:
   - Run SQL to create a read-only user
   - Grant necessary permissions
   ...
```

### Programmatic Usage

```python
from rag.retriever import get_retriever

# Get retriever instance
retriever = get_retriever()

# Search for relevant documents
results = retriever.get_relevant_docs(
    query="How do I connect to BigQuery?",
    n_results=3
)

for result in results:
    print(f"Source: {result['metadata']['source']}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Relevance Score: {result['score']}")
```

### Testing

```bash
python scripts/test_rag.py
```

Tests various queries and shows retrieved documents.

## Cost Management

### Embedding Costs

| Model | Cost per 1M tokens | Recommended Use |
|-------|-------------------|-----------------|
| text-embedding-3-small | $0.02 | ✅ Default (best value) |
| text-embedding-3-large | $0.13 | High accuracy needed |
| text-embedding-ada-002 | $0.10 | Legacy |

### Estimated Costs

**One-time ingestion** (15 docs, ~150 chunks):
- Tokens: ~35,000
- Cost: **~$0.0007** (less than 1 cent!)

**Per query** (search + embed query):
- Tokens: ~50-100
- Cost: **~$0.000002** (negligible)

**Monthly** (1000 queries):
- Cost: **~$0.002** (less than 1 cent!)

### Token Tracking

The system automatically tracks token usage:

```python
from rag.embeddings import EmbeddingManager

manager = EmbeddingManager()
# ... create embeddings ...

# Get usage stats
stats = manager.get_usage_stats()
print(f"Total tokens: {stats['total_tokens']:,}")
print(f"Total cost: ${stats['total_cost']:.6f}")
```

## Configuration

### Chunk Size

Adjust in `document_processor.py`:

```python
processor = DocumentProcessor(
    chunk_size=1000,    # Characters per chunk (default: 1000)
    chunk_overlap=200   # Overlap between chunks (default: 200)
)
```

**Trade-offs**:
- Smaller chunks: More precise, more chunks, higher cost
- Larger chunks: More context, fewer chunks, lower cost

### Retrieval Count

Adjust number of documents retrieved:

```python
retriever.search(query, n_results=3)  # Default: 3
```

**Trade-offs**:
- More results: Better context, more tokens, higher LLM cost
- Fewer results: Faster, cheaper, might miss relevant info

### Embedding Model

Change in `embeddings.py` or when initializing:

```python
EmbeddingManager(model="text-embedding-3-large")  # Higher quality, 6.5x more expensive
```

## Vector Database

### Location

ChromaDB data stored at: `data/chroma_db/`

### Operations

**Reset database**:
```python
from rag.vector_store import VectorStore

store = VectorStore()
store.reset_collection()
```

**List sources**:
```python
sources = store.list_sources()
print(sources)
```

**Delete specific source**:
```python
store.delete_by_source("01_getting_started.md")
```

### Backup

Simply copy the `data/chroma_db/` directory:

```bash
cp -r data/chroma_db/ data/chroma_db_backup/
```

## Updating Documentation

When you add/update knowledge base files:

1. Update markdown files in `docs/knowledge_base/`
2. Re-run ingestion:
   ```bash
   python scripts/ingest_documents.py
   ```
3. Confirm to re-embed documents

**Incremental updates**: Currently, the system re-embeds all documents. For production, implement incremental updates by tracking file hashes.

## Performance

### Search Performance

- **Vector search**: ~10-50ms
- **Embedding query**: ~100-200ms
- **Total**: ~200-300ms per search

### Optimization Tips

1. **Batch embeddings** during ingestion
2. **Cache frequent queries** (if needed)
3. **Use smaller embedding model** for lower latency
4. **Adjust n_results** based on needs

## Troubleshooting

### "Vector database not found"

**Problem**: ChromaDB not initialized

**Solution**:
```bash
python scripts/ingest_documents.py
```

### "OPENAI_API_KEY not set"

**Problem**: Missing OpenAI API key

**Solution**: Add to `.env` file:
```bash
OPENAI_API_KEY=sk-...
```

### "No documents found"

**Problem**: Knowledge base directory empty

**Solution**: Ensure markdown files exist in `docs/knowledge_base/`

### High costs

**Problem**: Too many embeddings being created

**Solution**:
- Use `text-embedding-3-small` (default)
- Increase chunk size (fewer chunks)
- Don't re-ingest unnecessarily

## Architecture Decisions

### Why ChromaDB?

- ✅ Easy to use (no separate server)
- ✅ Persistent storage
- ✅ Python-native
- ✅ Good performance for small-medium datasets
- ✅ Free and open source

### Why OpenAI Embeddings?

- ✅ High quality embeddings
- ✅ Very cheap ($0.02 per 1M tokens)
- ✅ Fast API
- ✅ text-embedding-3-small is excellent value

### Why Tiktoken?

- ✅ Accurate token counting
- ✅ Fast (C implementation)
- ✅ Same tokenizer as OpenAI models
- ✅ Essential for cost management

## Future Enhancements

- [ ] Incremental document updates (track file hashes)
- [ ] Hybrid search (keyword + semantic)
- [ ] Re-ranking results
- [ ] Query caching
- [ ] Multi-language support
- [ ] Document versioning
- [ ] User feedback loop (click tracking)
- [ ] A/B testing different retrieval strategies

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Tiktoken](https://github.com/openai/tiktoken)
- [RAG Best Practices](https://www.anthropic.com/index/retrieval-augmented-generation)
