import requests

from config import OPENWEATHER_API_KEY


OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_current_weather(location: str) -> dict:
    """Fetch current weather from OpenWeatherMap for a city or place name."""
    if not location or not location.strip():
        return {"error": "Please provide a location."}

    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "your_openweathermap_api_key_here":
        return {
            "error": "OPENWEATHER_API_KEY is missing. Add your OpenWeatherMap API key to .env."
        }

    params = {
        "q": location.strip(),
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial",
    }

    try:
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        data = response.json()
    except requests.RequestException as exc:
        return {"error": f"Could not reach OpenWeatherMap: {exc}"}
    except ValueError:
        return {"error": "OpenWeatherMap returned a response that was not valid JSON."}

    if response.status_code != 200:
        message = data.get("message", "Unknown weather API error.")
        return {"error": f"OpenWeatherMap error: {message}"}

    try:
        return {
            "location": f"{data['name']}, {data['sys']['country']}",
            "temperature_f": data["main"]["temp"],
            "feels_like_f": data["main"]["feels_like"],
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed_mph": data["wind"]["speed"],
        }
    except (KeyError, IndexError, TypeError):
        return {"error": "OpenWeatherMap returned an unexpected data format."}
