import requests
from flask import current_app
from app import cache

@cache.memoize(timeout=300)
def get_weather_by_district(district):
    api_key = current_app.config.get("WEATHER_API_KEY")
    if not api_key or not district:
        return None

    params = {
        "q": f"{district},UG",
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(
            current_app.config["WEATHER_BASE_URL"],
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        return {
            "district": district,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"].title(),
            "wind_speed": data["wind"]["speed"],
            "icon": data["weather"][0]["icon"]
        }
    except Exception:
        return None