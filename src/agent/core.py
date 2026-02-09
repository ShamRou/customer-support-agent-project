"""Core agent logic - Simple working version"""
import os
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

def run_agent(user_message: str) -> str:
    """Run the agent with tool support"""
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
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )
        
        # If no tool use, return the response
        if response.stop_reason != "tool_use":
            text_response = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "I couldn't generate a response."
            )
            return text_response
        
        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        
        tool_results = []
        for content_block in response.content:
            if content_block.type == "tool_use":
                result = process_tool_call(content_block.name, content_block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": result
                })
        
        messages.append({"role": "user", "content": tool_results})

def chat_loop():
    """Simple chat interface"""
    print("=" * 60)
    print("DataPulse Support Agent")
    print("=" * 60)
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        print()
        response = run_agent(user_input)
        print(f"🤖 Agent: {response}\n")
        print("-" * 60)

if __name__ == "__main__":
    chat_loop()