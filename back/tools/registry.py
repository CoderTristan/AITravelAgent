from .weather import get_live_weather
from .forecast import get_forecast
from .geocode import geocode_location
from .places import search_places


TOOLS = {
    tool.__name__: tool
    for tool in [
        get_live_weather,
        get_forecast,
        geocode_location,
        search_places,
    ]
}


def get_tool_schemas():
    return [
        tool.tool
        for tool in TOOLS.values()
    ]


def get_tool_function(name: str):
    return TOOLS.get(name)