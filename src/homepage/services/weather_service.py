"""Weather service for fetching weather data from multiple providers."""

import logging
from datetime import datetime
from typing import Any

import requests

logger = logging.getLogger(__name__)


# Map WMO weather codes to descriptions (Open-Meteo)
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Light snow showers",
    86: "Snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail",
}


# Map WMO weather codes to emojis (Open-Meteo)
WMO_WEATHER_EMOJIS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌦️",
    53: "🌦️",
    55: "🌧️",
    61: "🌧️",
    63: "🌧️",
    65: "🌧️",
    71: "🌨️",
    73: "🌨️",
    75: "🌨️",
    77: "🌨️",
    80: "🌦️",
    81: "🌧️",
    82: "🌧️",
    85: "🌨️",
    86: "🌨️",
    95: "⛈️",
    96: "⛈️",
    99: "⛈️",
}


# Map OpenWeatherMap icons to emojis
OPENWEATHERMAP_ICON_EMOJIS = {
    "01d": "☀️",
    "01n": "🌙",
    "02d": "🌤️",
    "02n": "☁️",
    "03d": "☁️",
    "03n": "☁️",
    "04d": "☁️",
    "04n": "☁️",
    "09d": "🌧️",
    "09n": "🌧️",
    "10d": "🌦️",
    "10n": "🌧️",
    "11d": "⛈️",
    "11n": "⛈️",
    "13d": "🌨️",
    "13n": "🌨️",
    "50d": "🌫️",
    "50n": "🌫️",
}


class WeatherService:
    """Service for fetching weather data from multiple providers."""

    @staticmethod
    def get_current_weather(
        lat: float,
        lon: float,
        provider: str = "openmeteo",
        api_key: str | None = None,
        units: str = "metric",
    ) -> dict[str, Any]:
        """Get current weather data.

        Args:
            lat: Latitude
            lon: Longitude
            provider: Weather provider ('openmeteo' or 'openweathermap')
            api_key: API key for provider (required for OpenWeatherMap)
            units: Unit system ('metric' or 'imperial')

        Returns:
            Dictionary with weather data including temperature, humidity, description, wind_speed

        Raises:
            ValueError: If provider is invalid or API key is missing
            requests.RequestException: If API request fails
        """
        match provider:
            case "openmeteo":
                return _fetch_openmeteo_weather(lat, lon, units)
            case "openweathermap":
                if not api_key:
                    raise ValueError("OpenWeatherMap API key required")
                return _fetch_openweathermap_weather(lat, lon, api_key, units)
            case _:
                raise ValueError(f"Invalid weather provider: {provider}")

    @staticmethod
    def get_hourly_forecast(
        lat: float,
        lon: float,
        provider: str = "openmeteo",
        api_key: str | None = None,
        units: str = "metric",
    ) -> dict[str, Any]:
        """Get hourly weather forecast.

        Args:
            lat: Latitude
            lon: Longitude
            provider: Weather provider ('openmeteo' or 'openweathermap')
            api_key: API key for provider (required for OpenWeatherMap)
            units: Unit system ('metric' or 'imperial')

        Returns:
            Dictionary with hourly forecast data

        Raises:
            ValueError: If provider is invalid or API key is missing
            requests.RequestException: If API request fails
        """
        match provider:
            case "openmeteo":
                return _fetch_openmeteo_forecast(lat, lon, units)
            case "openweathermap":
                if not api_key:
                    raise ValueError("OpenWeatherMap API key required")
                return _fetch_openweathermap_forecast(lat, lon, api_key, units)
            case _:
                raise ValueError(f"Invalid weather provider: {provider}")

    @staticmethod
    def get_daily_forecast(
        lat: float,
        lon: float,
        provider: str = "openmeteo",
        api_key: str | None = None,
        units: str = "metric",
    ) -> dict[str, Any]:
        """Get daily weather forecast.

        Args:
            lat: Latitude
            lon: Longitude
            provider: Weather provider ('openmeteo' or 'openweathermap')
            api_key: API key for provider (required for OpenWeatherMap)
            units: Unit system ('metric' or 'imperial')

        Returns:
            Dictionary with daily forecast data

        Raises:
            ValueError: If provider is invalid or API key is missing
            requests.RequestException: If API request fails
        """
        match provider:
            case "openmeteo":
                return _fetch_openmeteo_daily_forecast(lat, lon, units)
            case "openweathermap":
                if not api_key:
                    raise ValueError("OpenWeatherMap API key required")
                return _fetch_openweathermap_daily_forecast(lat, lon, api_key, units)
            case _:
                raise ValueError(f"Invalid weather provider: {provider}")


def _fetch_openmeteo_weather(lat: float, lon: float, units: str = "metric") -> dict[str, Any]:
    """Fetch weather from Open-Meteo (no API key needed)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params: dict[str, str | float] = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "temperature_unit": "celsius" if units == "metric" else "fahrenheit",
        "wind_speed_unit": "kmh" if units == "metric" else "mph",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data["current"]

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "description": WMO_WEATHER_CODES.get(current["weather_code"], "Unknown"),
        "wind_speed": current["wind_speed_10m"],
        "units": units,
    }


def _fetch_openmeteo_forecast(lat: float, lon: float, units: str = "metric") -> dict[str, Any]:
    """Fetch hourly weather forecast from Open-Meteo (no API key needed)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params: dict[str, str | float] = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,weather_code,precipitation_probability",
        "temperature_unit": "celsius" if units == "metric" else "fahrenheit",
        "forecast_days": 1,  # Today only
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    hourly = data["hourly"]
    times = hourly["time"]
    temps = hourly["temperature_2m"]
    codes = hourly["weather_code"]
    precip_probs = hourly["precipitation_probability"]

    # Get current hour
    now = datetime.now()
    current_hour = now.hour

    # Build hourly forecast for next 12 hours
    forecast = []
    for time_str, temp, code, precip in zip(times, temps, codes, precip_probs, strict=True):
        hour = int(time_str.split("T")[1].split(":")[0])
        # Start from current hour, get next 12 hours
        if hour >= current_hour and len(forecast) < 12:
            forecast.append(
                {
                    "hour": f"{hour:02d}:00",
                    "temperature": round(temp, 1),
                    "weather_code": code,
                    "weather_emoji": WMO_WEATHER_EMOJIS.get(code, "❓"),
                    "precipitation_probability": precip if precip else 0,
                }
            )

    return {"hourly": forecast, "units": units}


def _fetch_openmeteo_daily_forecast(lat: float, lon: float, units: str = "metric") -> dict[str, Any]:
    """Fetch 7-day daily forecast from Open-Meteo (no API key needed)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params: dict[str, str | float] = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "temperature_unit": "celsius" if units == "metric" else "fahrenheit",
        "forecast_days": 7,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    daily = data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    codes = daily["weather_code"]
    precip_probs = daily["precipitation_probability_max"]

    # Build daily forecast for 7 days
    forecast = []
    for date_str, max_temp, min_temp, code, precip in zip(
        dates, max_temps, min_temps, codes, precip_probs, strict=True
    ):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%a")

        forecast.append(
            {
                "day": day_name,
                "date": date_str,
                "temperature_max": round(max_temp, 1),
                "temperature_min": round(min_temp, 1),
                "weather_code": code,
                "weather_emoji": WMO_WEATHER_EMOJIS.get(code, "❓"),
                "precipitation_probability": precip if precip else 0,
            }
        )

    return {"daily": forecast, "units": units}


def _fetch_openweathermap_weather(
    lat: float, lon: float, api_key: str, units: str = "metric"
) -> dict[str, Any]:
    """Fetch weather from OpenWeatherMap (requires API key)."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params: dict[str, str | float] = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"].title(),
        "wind_speed": data["wind"]["speed"],
        "units": units,
    }


def _fetch_openweathermap_forecast(
    lat: float, lon: float, api_key: str, units: str = "metric"
) -> dict[str, Any]:
    """Fetch hourly forecast from OpenWeatherMap (requires API key)."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params: dict[str, str | float] = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "cnt": 12,  # Next 12 periods (3-hour intervals)
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    forecast = []
    for item in data["list"][:12]:  # Take first 12 items
        dt = datetime.fromtimestamp(item["dt"])
        icon = item["weather"][0]["icon"]

        forecast.append(
            {
                "hour": dt.strftime("%H:%M"),
                "temperature": round(item["main"]["temp"], 1),
                "weather_code": item["weather"][0]["id"],
                "weather_emoji": OPENWEATHERMAP_ICON_EMOJIS.get(icon, "❓"),
                "precipitation_probability": int(item.get("pop", 0) * 100),
            }
        )

    return {"hourly": forecast, "units": units}


def _fetch_openweathermap_daily_forecast(
    lat: float, lon: float, api_key: str, units: str = "metric"
) -> dict[str, Any]:
    """Fetch 7-day daily forecast from OpenWeatherMap (requires API key)."""
    # Note: OpenWeatherMap deprecated the daily forecast endpoint in their free tier
    # We'll use the 5-day forecast and group by day
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params: dict[str, str | float] = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Group forecast by day
    daily_data = {}
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        date_str = dt.strftime("%Y-%m-%d")
        day_name = dt.strftime("%a")

        if date_str not in daily_data:
            daily_data[date_str] = {
                "day": day_name,
                "date": date_str,
                "temps": [],
                "icons": [],
                "precip": [],
                "codes": [],
            }

        daily_data[date_str]["temps"].append(item["main"]["temp"])
        daily_data[date_str]["icons"].append(item["weather"][0]["icon"])
        daily_data[date_str]["precip"].append(item.get("pop", 0))
        daily_data[date_str]["codes"].append(item["weather"][0]["id"])

    # Build daily forecast
    forecast = []
    for date_str in sorted(daily_data.keys())[:7]:  # Take first 7 days
        day_info = daily_data[date_str]
        max_temp = max(day_info["temps"])
        min_temp = min(day_info["temps"])
        # Use most common icon
        most_common_icon = max(set(day_info["icons"]), key=day_info["icons"].count)
        most_common_code = max(set(day_info["codes"]), key=day_info["codes"].count)
        max_precip = max(day_info["precip"]) if day_info["precip"] else 0

        forecast.append(
            {
                "day": day_info["day"],
                "date": date_str,
                "temperature_max": round(max_temp, 1),
                "temperature_min": round(min_temp, 1),
                "weather_code": most_common_code,
                "weather_emoji": OPENWEATHERMAP_ICON_EMOJIS.get(most_common_icon, "❓"),
                "precipitation_probability": int(max_precip * 100),
            }
        )

    return {"daily": forecast, "units": units}
