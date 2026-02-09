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
    Simulate searching documentation.
    In real implementation, this would do RAG/vector search.
    For now, return mock data.
    """
    # Mock responses based on common queries
    mock_docs = {
        "snowflake": "To connect to Snowflake: 1) Go to Integrations, 2) Select Snowflake, 3) Enter your account credentials...",
        "alert": "Custom alerts are available on Pro and Enterprise plans. You can set up alerts based on data quality metrics...",
        "pricing": "We offer three plans: Free ($0), Pro ($99/month), and Enterprise (custom pricing)...",
        "api": "Our API is available on Pro and Enterprise plans. Documentation: docs.datapulse.io/api..."
    }
    
    # Simple keyword matching for demo
    query_lower = query.lower()
    for keyword, response in mock_docs.items():
        if keyword in query_lower:
            return response
    
    return "I found general documentation about DataPulse. Could you be more specific about what you're looking for?"

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