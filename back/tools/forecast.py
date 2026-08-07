import httpx
import json


async def get_forecast(
    city: str,
    days: int = 3,
) -> str:
    """
    Get a multi-day weather forecast for a city.

    Args:
        city: City name (e.g. "Chicago")
        days: Number of forecast days (1-7)

    Returns:
        JSON string containing the forecast.
    """

    # Clamp to Open-Meteo limits
    days = max(1, min(days, 7))

    # -------------------------
    # Geocode city
    # -------------------------
    async with httpx.AsyncClient() as client:
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
            },
        )

        geo.raise_for_status()

        geo_data = geo.json()

        if not geo_data.get("results"):
            return json.dumps(
                {
                    "error": f"Could not find '{city}'."
                }
            )

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        resolved_name = location["name"]
        country = location.get("country", "")

        # -------------------------
        # Forecast
        # -------------------------
        weather = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": [
                    "weathercode",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                ],
                "temperature_unit": "fahrenheit",
                "timezone": "auto",
                "forecast_days": days,
            },
        )

        weather.raise_for_status()

        data = weather.json()

    forecast = []

    for i in range(days):
        forecast.append(
            {
                "date": data["daily"]["time"][i],
                "high_f": data["daily"]["temperature_2m_max"][i],
                "low_f": data["daily"]["temperature_2m_min"][i],
                "precipitation_chance": data["daily"]["precipitation_probability_max"][i],
                "weather_code": data["daily"]["weathercode"][i],
            }
        )

    return json.dumps(
        {
            "location": f"{resolved_name}, {country}",
            "forecast": forecast,
        }
    )


get_forecast.tool = {
    "type": "function",
    "function": {
        "name": "get_forecast",
        "description": "Get a weather forecast for the next 1-7 days for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City or area for weather forecast."
                },
                "days": {
                    "type": "integer",
                    "description": "Number of forecast days (1-7)",
                    "default": 3,
                },
            },
            "required": ["city"],
        },
    },
}