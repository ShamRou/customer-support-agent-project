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

    system_prompt = """You are a helpful customer support agent for DataPulse, a data observability platform.

Your role:
- Answer questions about DataPulse features and capabilities
- Help users troubleshoot issues
- Check plan features when asked
- Create support tickets for complex issues that need human help

Be friendly, concise, and helpful."""

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