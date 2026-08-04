import ollama
import requests

def get_live_weather(city: str) -> str:
    """Fetch real-time weather for a given city using the Open-Meteo API."""
    try:
        # 1. Convert city name to latitude and longitude using Open-Meteo Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get("results"):
            return f"Could not find coordinates for {city}."
            
        location = geo_res["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        name = location["name"]
        country = location.get("country", "")

        # 2. Fetch the live weather using those coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        weather_res = requests.get(weather_url).json()
        
        temp = weather_res["current"]["temperature_2m"]
        
        return f"The current live temperature in {name}, {country} is {temp}°C."
        
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

# 3. Ask Qwen a question, passing the live function as a tool
response = ollama.chat(
    model='qwen3:8b',
    messages=[
        {'role': 'user', 'content': 'What is the live weather in Paris right now?'}
    ],
    tools=[get_live_weather],
)

# 4. Handle the tool execution loop
if response.message.tool_calls:
    for tool in response.message.tool_calls:
        if tool.function.name == 'get_live_weather':
            # Execute the function using the arguments Qwen extracted
            api_result = get_live_weather(**tool.function.arguments)
            print(f"🌍 API Result: {api_result}")
else:
    print(response.message.content)