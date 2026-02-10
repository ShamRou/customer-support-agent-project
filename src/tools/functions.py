"""Tool definitions and implementations for the agent"""

# Tool schemas (what Claude sees)
TOOLS = [
    {
        "name": "search_documentation",
        "description": "Search the product documentation for information. Use this when the user asks about features, how-tos, or product capabilities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documentation"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "check_plan_feature",
        "description": "Check if a specific feature is available on a given pricing plan (free, pro, or enterprise).",
        "input_schema": {
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "description": "The feature to check (e.g., 'custom_alerts', 'api_access', 'sso')"
                },
                "plan": {
                    "type": "string",
                    "enum": ["free", "pro", "enterprise"],
                    "description": "The pricing plan to check"
                }
            },
            "required": ["feature", "plan"]
        }
    },
    {
        "name": "create_support_ticket",
        "description": "Create a support ticket for issues that require human assistance. Use when the query is complex or requires account-specific help.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_description": {
                    "type": "string",
                    "description": "Description of the user's issue"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Priority level of the ticket"
                }
            },
            "required": ["issue_description", "priority"]
        }
    }
]

# Tool implementations (actual functions)
def search_documentation(query: str) -> str:
    """
    Search the DataPulse documentation using RAG (Retrieval-Augmented Generation).
    Uses ChromaDB + OpenAI embeddings to find relevant documentation.
    """
    try:
        # Import here to avoid circular dependencies
        from rag.retriever import get_retriever

        # Get retriever instance
        retriever = get_retriever()

        if not retriever.ready:
            # Fallback to mock data if RAG not ready
            return _search_documentation_fallback(query)

        # Search knowledge base
        print(f"   🔍 Searching knowledge base for: '{query}'")
        context = retriever.search(query, n_results=3)

        # Return the context
        return context

    except ImportError:
        # If RAG dependencies not installed, use fallback
        return _search_documentation_fallback(query)
    except Exception as e:
        print(f"   ⚠️  RAG search error: {e}")
        return _search_documentation_fallback(query)


def _search_documentation_fallback(query: str) -> str:
    """
    Fallback search when RAG is not available.
    Returns mock data based on keywords.
    """
    # Mock responses based on common queries
    mock_docs = {
        "snowflake": "To connect to Snowflake: 1) Go to Integrations, 2) Select Snowflake, 3) Enter your account credentials...",
        "bigquery": "To connect to BigQuery: 1) Create a service account in GCP, 2) Download JSON key, 3) Upload to DataPulse...",
        "redshift": "To connect to Redshift: 1) Configure security group, 2) Create read-only user, 3) Enter connection details...",
        "alert": "Custom alerts are available on Pro and Enterprise plans. You can set up alerts based on data quality metrics...",
        "pricing": "We offer three plans: Free ($0), Pro ($99/month), and Enterprise (custom pricing)...",
        "api": "Our API is available on Pro and Enterprise plans. Documentation: docs.datapulse.io/api...",
        "monitor": "DataPulse supports multiple monitor types: Freshness (data recency), Volume (row counts), Schema (structure changes), and Custom SQL...",
        "slack": "Slack integration is available on Pro and Enterprise plans. Setup: Go to Settings > Integrations > Slack > Connect...",
        "freshness": "Freshness monitors check when data was last updated. Configure by selecting a timestamp column and setting your threshold...",
        "dbt": "dbt integration: Connect via dbt Cloud API or upload manifest.json. DataPulse auto-creates monitors from dbt tests...",
    }

    # Simple keyword matching
    query_lower = query.lower()
    for keyword, response in mock_docs.items():
        if keyword in query_lower:
            return response

    return "I found general documentation about DataPulse. Could you be more specific about what you're looking for? Try asking about: Snowflake, BigQuery, alerts, pricing, monitors, or API."

def check_plan_feature(feature: str, plan: str) -> str:
    """
    Check if a feature is available on a plan.
    In real implementation, this would query a database.
    """
    # Mock feature matrix
    features = {
        "custom_alerts": ["pro", "enterprise"],
        "api_access": ["pro", "enterprise"],
        "sso": ["enterprise"],
        "basic_monitoring": ["free", "pro", "enterprise"],
        "slack_integration": ["pro", "enterprise"],
        "premium_support": ["enterprise"]
    }
    
    if feature not in features:
        return f"I don't recognize the feature '{feature}'. Available features: {', '.join(features.keys())}"
    
    if plan in features[feature]:
        return f"✅ Yes, '{feature}' is available on the {plan.upper()} plan."
    else:
        available_plans = ", ".join([p.upper() for p in features[feature]])
        return f"❌ No, '{feature}' is not available on the {plan.upper()} plan. It's available on: {available_plans}"

def create_support_ticket(issue_description: str, priority: str) -> str:
    """
    Create a support ticket.
    In real implementation, this would integrate with ticketing system.
    """
    ticket_id = f"TICKET-{hash(issue_description) % 10000:04d}"
    return f"✅ Support ticket created: {ticket_id}\nPriority: {priority.upper()}\nOur team will respond within 24 hours."

# Map tool names to functions
TOOL_FUNCTIONS = {
    "search_documentation": search_documentation,
    "check_plan_feature": check_plan_feature,
    "create_support_ticket": create_support_ticket
}