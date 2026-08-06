import httpx


async def get_live_weather(city: str) -> str:
    """
    Async tool to get current weather.
    """

    try:
        async with httpx.AsyncClient() as client:

            geo_url = (
                "https://geocoding-api.open-meteo.com/v1/search"
                f"?name={city}&count=1"
            )

            geo_res = await client.get(geo_url)
            geo_data = geo_res.json()

            if not geo_data.get("results"):
                return f"Could not find coordinates for {city}."

            location = geo_data["results"][0]

            lat = location["latitude"]
            lon = location["longitude"]

            name = location["name"]
            country = location.get("country", "")

            weather_url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}"
                f"&longitude={lon}"
                "&current=temperature_2m,weather_code"
            )

            weather_res = await client.get(weather_url)
            weather_data = weather_res.json()

            temp = weather_data["current"]["temperature_2m"]

            return (
                f"The current live temperature in "
                f"{name}, {country} is {temp}°C."
            )

    except Exception as e:
        return f"Error fetching weather data: {str(e)}"



# Ollama tool schema
get_live_weather.tool = {
    "type": "function",
    "function": {
        "name": "get_live_weather",
        "description": "Get the current weather conditions for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name."
                }
            },
            "required": [
                "city"
            ]
        }
    }
}