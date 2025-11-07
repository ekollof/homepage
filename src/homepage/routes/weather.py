"""Weather-related API routes."""

import logging
from typing import TYPE_CHECKING, Optional

import requests
from flask import Blueprint, jsonify, request

from ..services.geoip_service import GeoIPService
from ..services.weather_service import WeatherService

if TYPE_CHECKING:
    from ..config import Config

logger = logging.getLogger(__name__)

weather_bp = Blueprint("weather", __name__)

# Config will be injected
_config: Optional["Config"] = None


def init_weather_blueprint(config):
    """Initialize weather blueprint with dependencies."""
    global _config
    _config = config


@weather_bp.route("/api/weather")
def get_weather():  # pylint: disable=too-many-return-statements
    """Get weather data using configured provider."""
    assert _config is not None

    if not _config.ENABLE_WEATHER:
        return jsonify({"error": "Weather feature not enabled"}), 404

    try:
        # Get location
        lat, lon, location_name = _get_location()

        # Get weather data from service
        weather_data = WeatherService.get_current_weather(
            lat,
            lon,
            provider=_config.WEATHER_PROVIDER,
            api_key=_config.WEATHER_API_KEY,
            units=_config.WEATHER_UNITS,
        )

        weather_data["location"] = location_name
        return jsonify(weather_data)

    except requests.ConnectionError:
        logger.warning("Weather: No network connection available")
        return jsonify({"error": "No network connection"}), 503
    except requests.Timeout:
        logger.warning("Weather: Request timed out")
        return jsonify({"error": "Request timed out"}), 504
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error("Error fetching weather: %s", e)
        return jsonify({"error": "Weather service unavailable"}), 503


@weather_bp.route("/api/weather/forecast")
def get_weather_forecast():  # pylint: disable=too-many-return-statements
    """Get hourly weather forecast data."""
    assert _config is not None

    if not _config.ENABLE_WEATHER:
        return jsonify({"error": "Weather feature not enabled"}), 404

    try:
        # Get location
        lat, lon, location_name = _get_location()

        # Get forecast data from service
        forecast_data = WeatherService.get_hourly_forecast(
            lat,
            lon,
            provider=_config.WEATHER_PROVIDER,
            api_key=_config.WEATHER_API_KEY,
            units=_config.WEATHER_UNITS,
        )

        forecast_data["location"] = location_name
        return jsonify(forecast_data)

    except requests.ConnectionError:
        logger.warning("Weather forecast: No network connection available")
        return jsonify({"error": "No network connection"}), 503
    except requests.Timeout:
        logger.warning("Weather forecast: Request timed out")
        return jsonify({"error": "Request timed out"}), 504
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error("Error fetching weather forecast: %s", e)
        return jsonify({"error": "Weather forecast unavailable"}), 503


@weather_bp.route("/api/weather/forecast/daily")
def get_daily_forecast():
    """Get daily weather forecast data."""
    assert _config is not None

    if not _config.ENABLE_WEATHER:
        return jsonify({"error": "Weather feature not enabled"}), 404

    try:
        # Get location
        lat, lon, location_name = _get_location()

        # Get daily forecast data from service
        forecast_data = WeatherService.get_daily_forecast(
            lat,
            lon,
            provider=_config.WEATHER_PROVIDER,
            api_key=_config.WEATHER_API_KEY,
            units=_config.WEATHER_UNITS,
        )

        forecast_data["location"] = location_name
        return jsonify(forecast_data)

    except requests.ConnectionError:
        logger.warning("Daily forecast: No network connection available")
        return jsonify({"error": "No network connection"}), 503
    except requests.Timeout:
        logger.warning("Daily forecast: Request timed out")
        return jsonify({"error": "Request timed out"}), 504
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error("Error fetching daily forecast: %s", e)
        return jsonify({"error": "Daily forecast unavailable"}), 503


def _get_location() -> tuple[float, float, str]:
    """Get location from config or GeoIP."""
    assert _config is not None

    # Check if location is provided in config
    if _config.WEATHER_LOCATION:
        # Parse lat,lon format
        if "," in _config.WEATHER_LOCATION:
            try:
                lat, lon = map(float, _config.WEATHER_LOCATION.split(","))
                return lat, lon, f"{lat:.2f},{lon:.2f}"
            except ValueError:
                pass

    # Use GeoIP to determine location
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if client_ip and client_ip != "127.0.0.1":
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = None

    return GeoIPService.get_location(
        ip_address=client_ip,
        provider=_config.GEOIP_PROVIDER,
        db_path=_config.GEOIP_DB_PATH,
    )
