# `requests` is a third-party HTTP library.
# HTTP is the request/response protocol used by web APIs. This app uses it to
# ask OpenWeatherMap for current weather data.
import requests

# The OpenWeatherMap API key comes from `config.py`, which reads `.env` through
# environment variables loaded by `main.py`.
from config import OPENWEATHER_API_KEY, debug_print


# This is the endpoint URL for OpenWeatherMap's "current weather" API.
# An endpoint is the specific web address where an API accepts requests.
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_current_weather(location: str) -> dict:
    """Fetch current weather from OpenWeatherMap for a city or place name.

    Parameter:
    - location: a city or place name from the user, such as "Austin" or
      "New York". The LLM extracts this from the user's message and passes it
      through the tool-calling flow.

    Return value:
    - A Python dictionary. On success it contains clean weather fields the LLM
      can summarize. On failure it contains an `"error"` key with a readable
      explanation.

    How this fits the architecture:
    This is the tool/function the agent can call. The LLM decides *when* to use
    it, but this Python function does the actual live weather API request.
    """
    # Validate the input before calling the external API.
    # `not location` catches None or an empty string.
    # `location.strip()` removes spaces; if only spaces remain, it is invalid.
    if not location or not location.strip():
        debug_print("Weather tool received an empty location")
        return {"error": "Please provide a location."}

    # Check that a real API key is available before making the HTTP request.
    # This produces a clear beginner-friendly error instead of a confusing API
    # authentication failure later.
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "your_openweathermap_api_key_here":
        debug_print("Weather tool cannot run because OPENWEATHER_API_KEY is missing")
        return {
            "error": "OPENWEATHER_API_KEY is missing. Add your OpenWeatherMap API key to .env."
        }

    # Query parameters are values added to the URL by `requests`.
    # For example, requests will turn these into something like:
    # ?q=Austin&appid=...&units=imperial
    #
    # `q` is OpenWeatherMap's parameter for the city/location.
    # `appid` is the API key.
    # `units="imperial"` asks for Fahrenheit and miles-per-hour style units.
    params = {
        "q": location.strip(),
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial",
    }
    debug_print("Weather tool prepared OpenWeatherMap request", {
        "url": OPENWEATHER_URL,
        "params": {
            "q": params["q"],
            "appid": "[hidden]",
            "units": params["units"],
        },
    })

    try:
        # Send an HTTP GET request to OpenWeatherMap.
        #
        # GET is the common HTTP method for "please retrieve data".
        # `params=params` adds the query parameters safely.
        # `timeout=10` means "give up after 10 seconds" so the app does not hang
        # forever if the network or API is unavailable.
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        debug_print("OpenWeatherMap HTTP response received", {
            "status_code": response.status_code,
            "url_without_api_key": response.url.replace(OPENWEATHER_API_KEY, "[hidden]"),
        })

        # OpenWeatherMap returns JSON text. `response.json()` parses that text
        # into Python data structures, usually dictionaries and lists.
        data = response.json()
        debug_print("Parsed OpenWeatherMap JSON response", data)
    except requests.RequestException as exc:
        # Network errors, timeouts, DNS problems, and similar request failures
        # are grouped under `requests.RequestException`.
        return {"error": f"Could not reach OpenWeatherMap: {exc}"}
    except ValueError:
        # If the API response is not valid JSON, `response.json()` raises
        # ValueError. The agent cannot use a response it cannot parse.
        return {"error": "OpenWeatherMap returned a response that was not valid JSON."}

    # HTTP status code 200 means success.
    # Other status codes can mean invalid API key, city not found, rate limit,
    # server error, and so on.
    if response.status_code != 200:
        # `.get("message", "...")` reads the API's error message if it exists;
        # otherwise it uses the fallback string.
        message = data.get("message", "Unknown weather API error.")
        debug_print("OpenWeatherMap returned an error response", {
            "status_code": response.status_code,
            "message": message,
        })
        return {"error": f"OpenWeatherMap error: {message}"}

    try:
        # Pull only the fields we want the LLM to use.
        #
        # OpenWeatherMap returns a large nested JSON object. In Python:
        # - `data["main"]["temp"]` means get the `main` dictionary, then get
        #   its `temp` value.
        # - `data["weather"][0]["description"]` means get the first item from
        #   the `weather` list, then get its `description`.
        #
        # Returning a smaller dictionary keeps the final LLM prompt focused.
        weather_result = {
            "location": f"{data['name']}, {data['sys']['country']}",
            "temperature_f": data["main"]["temp"],
            "feels_like_f": data["main"]["feels_like"],
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed_mph": data["wind"]["speed"],
        }
        debug_print("Weather tool normalized API data for the LLM", weather_result)
        return weather_result
    except (KeyError, IndexError, TypeError):
        # These errors mean the API responded with JSON, but not in the shape
        # the app expected:
        # - KeyError: a dictionary key was missing.
        # - IndexError: a list did not have the expected first item.
        # - TypeError: a value had the wrong type, such as None instead of dict.
        return {"error": "OpenWeatherMap returned an unexpected data format."}
