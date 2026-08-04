import ollama

# 1. Define a normal Python function you want your agent to use
def get_current_weather(city: str) -> str:
    """Get the current weather for a specific city."""
    # (In a real project, you would call a real weather API here)
    return f"The weather in {city} is 22°C and sunny."

# 2. Ask the model a question and pass the function into the 'tools' list
response = ollama.chat(
    model='qwen3:8b',
    messages=[
        {'role': 'user', 'content': 'What is the weather like in Tokyo right now?'}
    ],
    tools=[get_current_weather], # Ollama automatically generates the schema for this function!
)

# 3. Check if the model decided to call the function
if response.message.tool_calls:
    for tool in response.message.tool_calls:
        print(f"🤖 Agent decided to call function: {tool.function.name}")
        print(f"📦 With arguments: {tool.function.arguments}")
        
        # Execute your local Python function with the arguments Qwen chose
        if tool.function.name == 'get_current_weather':
            result = get_current_weather(**tool.function.arguments)
            print(f"⚙️ Function Output: {result}")
else:
    print(response.message.content)