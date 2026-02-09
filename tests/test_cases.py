"""Test cases for evaluation"""

TEST_CASES = [
    {
        "query": "How do I connect to Snowflake?",
        "expected_tool": "search_documentation",
        "expected_contains": ["snowflake", "connect", "integration"]
    },
    {
        "query": "Is API access available on the free plan?",
        "expected_tool": "check_plan_feature",
        "expected_contains": ["api", "pro", "enterprise"]
    },
    {
        "query": "I need help with a critical data quality issue",
        "expected_tool": "create_support_ticket",
        "expected_contains": ["ticket", "support"]
    },
    {
        "query": "What pricing plans do you offer?",
        "expected_tool": "search_documentation",
        "expected_contains": ["free", "pro", "enterprise"]
    },
    {
        "query": "Do you have SSO on the Pro plan?",
        "expected_tool": "check_plan_feature",
        "expected_contains": ["sso", "enterprise"]
    }
]