# RAG System Setup Guide

## Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd "/Users/roumilishams/Desktop/Pro 2025/customer-support-agent-project"

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install chromadb openai tiktoken
```

### Step 2: Add OpenAI API Key

Edit your `.env` file and add:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Get your key from: https://platform.openai.com/api-keys

### Step 3: Ingest Documents

Build the vector database (one-time setup):

```bash
python scripts/ingest_documents.py
```

**Expected output:**
```
DATAPULSE KNOWLEDGE BASE INGESTION
======================================================================

STEP 1: PROCESSING DOCUMENTS
Found 15 markdown files
...
Total documents: ~150 chunks

📊 Statistics:
   Estimated cost: $0.000700

⚠️  This will create embeddings using OpenAI API (costs money)
Continue? (yes/no): yes

STEP 2: CREATING EMBEDDINGS
Creating embeddings for 150 documents...
[Progress shown]

EMBEDDING USAGE SUMMARY
Total Tokens: ~35,000
Total Cost: $0.000708

STEP 3: STORING IN VECTOR DATABASE
Added 150 documents to collection 'datapulse_docs'

✅ SUCCESS!
   Total documents: 150
   Source files: 15

INGESTION COMPLETE!
```

### Step 4: Test the RAG System

```bash
python scripts/test_rag.py
```

This will test these queries:
- "How do I connect to Snowflake?"
- "What's included in the Pro plan?"
- "My connection is timing out"
- "Can I set custom alerts?"

### Step 5: Run the Chatbot

```bash
python src/main.py
```

Try asking:
- "How do I connect to BigQuery?"
- "What monitor types are available?"
- "Is ML anomaly detection available on the Free plan?"
- "How do I troubleshoot connection timeouts?"

## Verification

After ingestion, you should see:

```
data/
└── chroma_db/
    ├── chroma.sqlite3
    └── [other ChromaDB files]
```

The chatbot will now use RAG for documentation searches!

## Cost Summary

- **One-time ingestion**: ~$0.0007 (less than 1 cent)
- **Per query**: ~$0.000002 (negligible)
- **1000 queries**: ~$0.002

Total monthly cost is dominated by Claude API ($10-50), not embeddings.

## Troubleshooting

### "OPENAI_API_KEY not set"
Add it to `.env` file.

### "Vector database not found"
Run `python scripts/ingest_documents.py`

### Import errors
Run `pip install -r requirements.txt`

## What Changed

### New Files
- `src/rag/` - RAG system modules
- `scripts/ingest_documents.py` - Ingestion script
- `scripts/test_rag.py` - Test script
- `docs/RAG_SYSTEM.md` - Full documentation

### Modified Files
- `requirements.txt` - Added chromadb, openai, tiktoken
- `src/tools/functions.py` - Updated search_documentation to use RAG

### New Directory
- `data/chroma_db/` - Vector database (created after ingestion)

## Next Steps

1. Run ingestion (Step 3 above)
2. Test with test script
3. Try the chatbot
4. Ask questions about DataPulse features!

The agent will now provide accurate, detailed answers from the 15-document knowledge base.
