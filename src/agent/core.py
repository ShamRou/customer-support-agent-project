"""Core agent logic - Simple working version"""
import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv
from tools.functions import TOOLS, TOOL_FUNCTIONS

load_dotenv()

def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result"""
    print(f"🔧 Using tool: {tool_name}")
    print(f"   Input: {tool_input}")

    tool_function = TOOL_FUNCTIONS[tool_name]
    result = tool_function(**tool_input)

    print(f"   Result: {result}\n")
    return result

def run_agent_streaming(user_message: str):
    """Run the agent with streaming support"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    messages = [{"role": "user", "content": user_message}]

    system_prompt = """You are an expert customer support agent for DataPulse, a leading data observability platform that helps teams monitor, validate, and ensure the quality of their data pipelines.

## Your Role & Capabilities

You have access to a comprehensive knowledge base with detailed documentation about:
- Platform features and integrations (Snowflake, BigQuery, Redshift, dbt)
- Monitor types (freshness, volume, schema, custom SQL, ML-based)
- Alerts and notifications (Slack, PagerDuty, email)
- Pricing plans (Free, Pro, Enterprise)
- Security and compliance (SOC 2, GDPR, HIPAA)
- API documentation and best practices
- Troubleshooting guides

## Available Tools

1. **search_documentation**: Search the knowledge base for detailed information
   - Use this FIRST for ANY product questions
   - The knowledge base contains comprehensive, accurate information
   - Always search before giving general answers

2. **check_plan_feature**: Check if a feature is available on a specific plan
   - Use when users ask about plan capabilities
   - Helps users understand upgrade benefits

3. **create_support_ticket**: Create tickets for complex issues
   - Use when issues require account-specific help
   - Use when problems need engineering investigation
   - Use for bugs, outages, or data-specific troubleshooting

## How to Respond

**For Product Questions**:
- ALWAYS use search_documentation first
- Provide specific, detailed answers based on retrieved documentation
- Include step-by-step instructions when relevant
- Reference specific documentation sections
- Don't make up or guess information

**For Troubleshooting**:
- Search documentation for common issues first
- Provide specific solutions from troubleshooting guides
- Escalate to support ticket if issue is complex or account-specific

**For Plan/Feature Questions**:
- Use check_plan_feature for specific features
- Search documentation for plan comparisons
- Be clear about what's available on each tier

**For Complex/Urgent Issues**:
- Create support tickets with appropriate priority
- High priority: Production issues, outages, data loss
- Medium priority: Non-critical bugs, feature questions
- Low priority: General inquiries, feature requests

## Communication Style

- **Professional yet approachable**: Friendly but knowledgeable
- **Concise**: Get to the point quickly, but be thorough
- **Empathetic**: Understand user frustration with data issues
- **Solution-oriented**: Focus on solving problems, not just explaining them
- **Proactive**: Anticipate follow-up questions and provide relevant links

## Important Guidelines

- **Accuracy First**: Use the knowledge base - don't guess or make assumptions
- **Search Before Answering**: For any product question, search documentation first
- **Be Specific**: Provide exact steps, commands, and configuration examples
- **Acknowledge Limitations**: If you don't know, say so and create a support ticket
- **Stay in Scope**: Focus on DataPulse - don't provide general data engineering advice
- **No Hallucinations**: Only provide information from the knowledge base or tools

## Example Interactions

❌ **Bad**: "DataPulse has monitoring features that help track your data."
✅ **Good**: [searches documentation first] "DataPulse offers 9 types of monitors. For your use case, I recommend Freshness monitors to track data recency and Volume monitors to detect missing data. Let me show you how to set these up..."

❌ **Bad**: "You might need to check the documentation for that."
✅ **Good**: [searches documentation] "According to our Snowflake integration guide, you need to create a read-only user with these specific permissions: [provides exact SQL commands from docs]"

Remember: Your knowledge base is comprehensive and accurate. Use it extensively to provide the best support possible!"""

    # Tool use loop
    while True:
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        ) as stream:
            # Collect the full response
            full_content = []

            # Stream text in real-time
            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "text":
                        # Start of text block
                        pass
                elif event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        # Print text as it arrives
                        print(event.delta.text, end="", flush=True)
                elif event.type == "content_block_stop":
                    # End of a content block
                    pass

            # Get the final message
            final_message = stream.get_final_message()

            # If no tool use, we're done
            if final_message.stop_reason != "tool_use":
                print()  # New line after streaming
                return

            # Process tool calls
            messages.append({"role": "assistant", "content": final_message.content})

            tool_results = []
            for content_block in final_message.content:
                if content_block.type == "tool_use":
                    result = process_tool_call(content_block.name, content_block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

def chat_loop():
    """Simple chat interface with streaming"""
    print("=" * 60)
    print("DataPulse Support Agent (Streaming Enabled)")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\n🤖 Agent: ", end="", flush=True)
        run_agent_streaming(user_input)
        print("-" * 60)

if __name__ == "__main__":
    chat_loop()