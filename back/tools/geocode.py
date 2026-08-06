import httpx
import json


async def geocode_location(location: str) -> str:
    """
    Find the coordinates and metadata for a location.

    Args:
        location: City, state, country, or address.

    Returns:
        JSON string containing location information.
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )

        response.raise_for_status()
        data = response.json()

    if not data.get("results"):
        return json.dumps({
            "error": f"Could not find '{location}'."
        })

    place = data["results"][0]

    result = {
        "name": place.get("name"),
        "country": place.get("country"),
        "state": place.get("admin1"),
        "latitude": place.get("latitude"),
        "longitude": place.get("longitude"),
        "timezone": place.get("timezone"),
        "population": place.get("population"),
    }

    return json.dumps(result)


geocode_location.tool = {
    "type": "function",
    "function": {
        "name": "geocode_location",
        "description": "Look up the coordinates and metadata for any city, town, address, or location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City, address, landmark, or other location."
                }
            },
            "required": ["location"]
        }
    }
}