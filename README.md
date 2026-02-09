# DataPulse Support Agent

A production-ready AI customer support agent built with Claude and tool calling.

## Features

- 🤖 Natural language understanding with Claude Sonnet 4
- 🔧 Tool calling for:
  - Documentation search
  - Plan feature checking
  - Support ticket creation
- 💬 Conversational interface

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "ANTHROPIC_API_KEY=your_key" > .env

# Run the agent
python src/main.py
```

## Architecture
```
User Query
    ↓
Agent (Claude Sonnet 4)
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Final Response
```

## Example Interactions

**User:** "Can I use custom alerts on the free plan?"
**Agent:** Uses `check_plan_feature` → "Custom alerts are available on Pro and Enterprise plans."

## What's Next

- [ ] Add RAG for real documentation
- [ ] Deploy as API
- [ ] Add evaluation framework
- [ ] Implement monitoring