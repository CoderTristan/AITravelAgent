from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    message: str

def get_live_weather(city: str) -> str:
    """Fetch real-time weather for a given city using the Open-Meteo API."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get("results"):
            return f"Could not find coordinates for {city}."
            
        location = geo_res["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        name = location["name"]
        country = location.get("country", "")

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        weather_res = requests.get(weather_url).json()
        
        temp = weather_res["current"]["temperature_2m"]
        return f"The current live temperature in {name}, {country} is {temp}°C."
        
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

@app.post("/api/chat")
async def chat(request: QueryRequest):
    messages = [{'role': 'user', 'content': request.message}]
    
    try:
        response = ollama.chat(
            model='qwen2.5:7b',
            messages=messages,
            tools=[get_live_weather],
        )

        messages.append(response.message)

        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                if tool.function.name == 'get_live_weather':
                    api_result = get_live_weather(**tool.function.arguments)
                    messages.append({'role': 'tool', 'content': api_result})

            final_response = ollama.chat(model='qwen2.5:7b', messages=messages)
            return {"reply": final_response.message.content}
        
        return {"reply": response.message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))