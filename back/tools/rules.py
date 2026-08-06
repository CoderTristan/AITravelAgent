TOOL_RULES = {

    "weather": {

        "keywords": [
            "weather",
            "temperature",
            "forecast",
            "rain",
            "snow",
            "storm",
            "hot",
            "cold",
            "climate",
        ],

        "required_tools": [
            "get_live_weather",
            "get_forecast",
        ],
    },


    "places": {

        "keywords": [
            "things to do",
            "activities",
            "attractions",
            "places",
            "landmarks",
            "visit",
            "explore",
        ],

        "required_tools": [
            "search_places",
        ],
    },


    "restaurants": {

        "keywords": [
            "restaurant",
            "food",
            "eat",
            "dinner",
            "lunch",
            "breakfast",
            "cafe",
        ],

        "required_tools": [
            "search_restaurants",
        ],
    },


    "distance": {

        "keywords": [
            "distance",
            "how far",
            "drive",
            "walk",
            "miles",
            "kilometers",
        ],

        "required_tools": [
            "calculate_distance",
        ],
    },


    "currency": {

        "keywords": [
            "currency",
            "exchange",
            "dollars",
            "euros",
            "convert",
            "price",
        ],

        "required_tools": [
            "convert_currency",
        ],
    },


    "events": {

        "keywords": [
            "events",
            "concert",
            "festival",
            "happening",
            "today",
            "this weekend",
        ],

        "required_tools": [
            "search_events",
        ],
    },

}

def detect_required_tools(message: str):
    """
    Detect likely tool categories from user input.
    Returns tool names that should be considered.
    """

    message = message.lower()

    required = []

    for category, rule in TOOL_RULES.items():

        for keyword in rule["keywords"]:

            if keyword in message:
                required.extend(
                    rule["required_tools"]
                )

                break

    return list(set(required))