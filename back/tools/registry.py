from .weather import get_live_weather
from .forecast import get_forecast
from .geocode import geocode_location
from .places import search_places


TOOLS = {
    "get_live_weather": get_live_weather,
    "get_forecast": get_forecast,
    "geocode_location": geocode_location,
    "search_places": search_places,
}