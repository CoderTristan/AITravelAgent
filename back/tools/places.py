import httpx
import json


async def search_places(
    city: str,
    category: str = "tourism",
    limit: int = 5,
) -> str:
    """
    Search for interesting places near a city.

    Args:
        city: City or location name.
        category: Type of place (tourism, museum, park, attraction).
        limit: Maximum results.

    Returns:
        JSON string containing places.
    """

    limit = max(1, min(limit, 10))

    async with httpx.AsyncClient() as client:

        # -------------------------
        # Geocode location
        # -------------------------
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
            },
        )

        geo.raise_for_status()

        geo_data = geo.json()

        if not geo_data.get("results"):
            return json.dumps({
                "error": f"Could not find {city}"
            })

        location = geo_data["results"][0]

        lat = location["latitude"]
        lon = location["longitude"]


        # -------------------------
        # Search OpenStreetMap
        # -------------------------
        query = f"""
        [out:json];
        (
          node["tourism"](around:5000,{lat},{lon});
          node["leisure"="park"](around:5000,{lat},{lon});
          node["amenity"="museum"](around:5000,{lat},{lon});
          way["tourism"](around:5000,{lat},{lon});
        );
        out center;
        """

        places_response = await client.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
        )

        places_response.raise_for_status()

        data = places_response.json()


    results = []

    for item in data.get("elements", [])[:limit]:

        tags = item.get("tags", {})

        name = tags.get("name")

        if not name:
            continue

        results.append(
            {
                "name": name,
                "type": (
                    tags.get("tourism")
                    or tags.get("amenity")
                    or tags.get("leisure")
                ),
                "latitude": item.get("lat")
                or item.get("center", {}).get("lat"),
                "longitude": item.get("lon")
                or item.get("center", {}).get("lon"),
            }
        )


    return json.dumps(
        {
            "location": city,
            "places": results,
        }
    )


search_places.tool = {
    "type": "function",
    "function": {
        "name": "search_places",
        "description": "Find tourist attractions, landmarks, museums, parks, and interesting places near a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City or location to search."
                },
                "category": {
                    "type": "string",
                    "description": "Type of place to find."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results."
                }
            },
            "required": [
                "city"
            ]
        }
    }
}