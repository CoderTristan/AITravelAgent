import httpx
import json


async def search_places(
    city: str,
    category: str = "tourism",
    limit: int = 5,
) -> str:
    """
    Find interesting places near a city.

    Returns only concise verified place information
    for the travel agent.
    """

    limit = max(1, min(limit, 5))

    async with httpx.AsyncClient(timeout=15) as client:

        # -------------------------
        # Geocode city
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
                "success": False,
                "error": f"Could not locate {city}"
            })


        location = geo_data["results"][0]

        lat = location["latitude"]
        lon = location["longitude"]


        # -------------------------
        # OpenStreetMap search
        # -------------------------
        query = f"""
        [out:json];
        (
          node["tourism"](around:5000,{lat},{lon});
          node["amenity"="museum"](around:5000,{lat},{lon});
          node["leisure"="park"](around:5000,{lat},{lon});
          way["tourism"](around:5000,{lat},{lon});
        );
        out center;
        """


        response = await client.post(
            "https://overpass-api.de/api/interpreter",
            data=query,
        )

        response.raise_for_status()

        data = response.json()


    places = []

    seen = set()


    for item in data.get("elements", []):

        tags = item.get("tags", {})

        name = tags.get("name")


        if not name:
            continue


        # avoid duplicates
        if name in seen:
            continue

        seen.add(name)


        place_type = (
            tags.get("tourism")
            or tags.get("amenity")
            or tags.get("leisure")
            or "place"
        )


        places.append(
            {
                "name": name,
                "type": place_type
            }
        )


        if len(places) >= limit:
            break



    return json.dumps(
        {
            "success": True,
            "city": city,
            "count": len(places),
            "places": places
        }
    )

search_places.tool = {
    "type": "function",
    "function": {
        "name": "search_places",
        "description": (
            "Find verified nearby attractions, museums, "
            "parks, landmarks, and interesting places. "
            "Use this when the user asks what to do, "
            "things to see, or activities."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City, region, state, or travel area."
                },
                "category": {
                    "type": "string",
                    "description": "Optional place category."
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of places to return, maximum 5."
                }
            },
            "required": [
                "city"
            ]
        }
    }
}