"""Tests for weather API functionality."""

import json
from unittest.mock import Mock, patch

import pytest
import requests


class TestWeatherAPI:
    """Test weather API functionality."""

    def test_weather_connection_error(self, client, monkeypatch):
        """Test weather endpoint handles connection errors."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        with patch(
            "homepage.services.weather_service.requests.get",
            side_effect=requests.ConnectionError("No network"),
        ):
            response = client.get("/api/weather")
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data["error"] == "No network connection"

    def test_weather_timeout_error(self, client, monkeypatch):
        """Test weather endpoint handles timeout errors."""
        import requests

        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        with patch(
            "homepage.services.weather_service.requests.get",
            side_effect=requests.Timeout("Timeout"),
        ):
            response = client.get("/api/weather")
            assert response.status_code == 504
            data = json.loads(response.data)
            assert data["error"] == "Request timed out"

    def test_weather_with_manual_location(self, client, monkeypatch, weather_mock_builder):
        """Test weather endpoint with manual location."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        # Mock the requests to Open-Meteo
        mock_response = Mock()
        mock_response.json.return_value = weather_mock_builder.openmeteo_current()

        with patch("homepage.services.weather_service.requests.get", return_value=mock_response):
            response = client.get("/api/weather")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "temperature" in data
            assert data["temperature"] == 15.0
            assert "location" in data
            assert data["location"] == "52.00,5.00"

    def test_geoip_database_not_found(self, monkeypatch):
        """Test MaxMind GeoIP raises error when database missing."""
        pytest.importorskip("geoip2")  # Skip if geoip2 not installed

        import tempfile
        from pathlib import Path

        from homepage.services.geoip_service import _geoip_maxmind

        with tempfile.TemporaryDirectory() as tmpdir:
            missing_db = Path(tmpdir) / "missing.mmdb"

            import homepage.app as app_module

            monkeypatch.setattr(app_module.config, "GEOIP_DB_PATH", str(missing_db))

            with pytest.raises(FileNotFoundError, match="MaxMind database not found"):
                _geoip_maxmind("8.8.8.8", str(missing_db))

    def test_openmeteo_weather_codes(self, monkeypatch):
        """Test Open-Meteo weather code mapping."""
        from unittest.mock import Mock, patch

        import homepage.app as app_module
        from homepage.services.weather_service import _fetch_openmeteo_weather

        monkeypatch.setattr(app_module.config, "WEATHER_UNITS", "metric")

        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 20.0,
                "relative_humidity_2m": 65,
                "weather_code": 61,  # Light rain
                "wind_speed_10m": 15.0,
            }
        }

        with patch("homepage.services.weather_service.requests.get", return_value=mock_response):
            result = _fetch_openmeteo_weather(52.0, 5.0)
            assert result["temperature"] == 20.0
            assert result["description"] == "Light rain"
            assert result["units"] == "metric"

    def test_forecast_endpoint_disabled(self, client, monkeypatch):
        """Test forecast endpoint returns 404 when weather disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", False)

        response = client.get("/api/weather/forecast")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_forecast_with_openmeteo(self, client, monkeypatch, weather_mock_builder):
        """Test forecast endpoint with Open-Meteo provider."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        mock_response = Mock()
        mock_response.json.return_value = weather_mock_builder.openmeteo_hourly()

        with patch("homepage.services.weather_service.requests.get", return_value=mock_response):
            response = client.get("/api/weather/forecast")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "hourly" in data
            assert len(data["hourly"]) >= 1  # At least one forecast item
            assert "hour" in data["hourly"][0]
            assert "temperature" in data["hourly"][0]
            assert "weather_emoji" in data["hourly"][0]
            assert data["units"] == "metric"

    def test_forecast_connection_error(self, client, monkeypatch):
        """Test forecast endpoint handles connection errors."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        with patch(
            "homepage.services.weather_service.requests.get",
            side_effect=requests.ConnectionError("No network"),
        ):
            response = client.get("/api/weather/forecast")
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data["error"] == "No network connection"


class TestDailyWeatherForecast:
    """Test daily weather forecast endpoint."""

    def test_daily_forecast_enabled(self, client, monkeypatch, weather_mock_builder):
        """Test daily forecast endpoint when enabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        mock_response = Mock()
        mock_response.json.return_value = weather_mock_builder.openmeteo_daily()

        with patch("homepage.services.weather_service.requests.get", return_value=mock_response):
            response = client.get("/api/weather/forecast/daily")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "daily" in data
            assert len(data["daily"]) >= 1
            assert "date" in data["daily"][0]
            assert "temperature_max" in data["daily"][0]
            assert "temperature_min" in data["daily"][0]
            assert data["units"] == "metric"

    def test_daily_forecast_disabled(self, client, monkeypatch):
        """Test daily forecast returns 404 when disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", False)

        response = client.get("/api/weather/forecast/daily")
        assert response.status_code == 404

    def test_daily_forecast_connection_error(self, client, monkeypatch):
        """Test daily forecast with connection error."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")

        with patch(
            "homepage.services.weather_service.requests.get", side_effect=requests.ConnectionError
        ):
            response = client.get("/api/weather/forecast/daily")
            assert response.status_code == 503
            data = response.get_json()
            assert "error" in data

    def test_daily_forecast_timeout(self, client, monkeypatch):
        """Test daily forecast with timeout."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")

        with patch("homepage.services.weather_service.requests.get", side_effect=requests.Timeout):
            response = client.get("/api/weather/forecast/daily")
            assert response.status_code == 504
            data = response.get_json()
            assert "error" in data


class TestWeatherServiceAdvanced:
    """Advanced weather service tests."""

    def test_get_current_weather_with_invalid_provider(self):
        """Test current weather with invalid provider."""
        from homepage.services.weather_service import WeatherService

        with pytest.raises(ValueError, match="Invalid weather provider"):
            WeatherService.get_current_weather(52.0, 5.0, provider="invalid")

    def test_get_hourly_forecast_with_invalid_provider(self):
        """Test hourly forecast with invalid provider."""
        from homepage.services.weather_service import WeatherService

        with pytest.raises(ValueError, match="Invalid weather provider"):
            WeatherService.get_hourly_forecast(52.0, 5.0, provider="invalid")

    def test_get_daily_forecast_with_invalid_provider(self):
        """Test daily forecast with invalid provider."""
        from homepage.services.weather_service import WeatherService

        with pytest.raises(ValueError, match="Invalid weather provider"):
            WeatherService.get_daily_forecast(52.0, 5.0, provider="invalid")

    def test_get_current_weather_openweathermap_no_api_key(self):
        """Test OpenWeatherMap without API key."""
        from homepage.services.weather_service import WeatherService

        with pytest.raises(ValueError, match="API key required"):
            WeatherService.get_current_weather(52.0, 5.0, provider="openweathermap")

    def test_get_hourly_forecast_openweathermap_no_api_key(self):
        """Test hourly forecast OpenWeatherMap without API key."""
        from homepage.services.weather_service import WeatherService

        with pytest.raises(ValueError, match="API key required"):
            WeatherService.get_hourly_forecast(52.0, 5.0, provider="openweathermap")
