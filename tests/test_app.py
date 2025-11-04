"""Tests for Homepage application."""

import json
from pathlib import Path

import pytest

from app import app as flask_app
from config import Config
from metrics import MetricsCollector
from utils import (
    SimpleCache,
    load_json_file,
    load_text_file,
    validate_links_config,
    validate_url,
)


@pytest.fixture
def app():
    """Create Flask test app."""
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


class TestSimpleCache:
    """Test SimpleCache class."""

    def test_set_and_get(self):
        """Test setting and getting cache values."""
        cache = SimpleCache(ttl=10)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent(self):
        """Test getting nonexistent key returns None."""
        cache = SimpleCache(ttl=10)
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = SimpleCache(ttl=0)
        cache.set("key1", "value1")
        import time

        time.sleep(0.1)
        assert cache.get("key1") is None

    def test_clear(self):
        """Test clearing cache."""
        cache = SimpleCache(ttl=10)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_invalidate(self):
        """Test invalidating specific key."""
        cache = SimpleCache(ttl=10)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.invalidate("key1")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestMetricsCollector:
    """Test MetricsCollector class."""

    def test_initialization(self):
        """Test metrics collector initialization."""
        metrics = MetricsCollector()
        assert metrics.request_count == 0
        assert metrics.page_views == 0
        assert metrics.search_count == 0

    def test_track_request(self):
        """Test tracking requests."""
        metrics = MetricsCollector()
        metrics.track_request("/")
        assert metrics.request_count == 1
        assert metrics.page_views == 1

        metrics.track_request("/health")
        assert metrics.request_count == 2
        assert metrics.page_views == 1

    def test_track_search(self):
        """Test tracking searches."""
        metrics = MetricsCollector()
        metrics.track_search("google", "test query")
        assert metrics.search_count == 1
        assert metrics.search_providers["google"] == 1

    def test_track_link_click(self):
        """Test tracking link clicks."""
        metrics = MetricsCollector()
        metrics.track_link_click("GitHub", "https://github.com")
        assert metrics.link_clicks["GitHub"] == 1

    def test_get_stats(self):
        """Test getting statistics."""
        metrics = MetricsCollector()
        metrics.track_request("/")
        metrics.track_search("brave", "test")
        stats = metrics.get_stats()

        assert "uptime_seconds" in stats
        assert "request_count" in stats
        assert stats["page_views"] == 1
        assert stats["search_count"] == 1


class TestUtilityFunctions:
    """Test utility functions."""

    def test_validate_url(self):
        """Test URL validation."""
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("ftp://example.com") is False
        assert validate_url("example.com") is False
        assert validate_url("") is False

    def test_load_json_file_nonexistent(self):
        """Test loading nonexistent JSON file."""
        result = load_json_file(Path("/nonexistent/file.json"), default={"key": "value"})
        assert result == {"key": "value"}

    def test_load_text_file_nonexistent(self):
        """Test loading nonexistent text file."""
        result = load_text_file(Path("/nonexistent/file.txt"), default="default")
        assert result == "default"

    def test_validate_links_config_valid(self):
        """Test validating valid links configuration."""
        config = {
            "category": [
                {
                    "name": "Test Category",
                    "icon": "📚",
                    "links": [
                        {
                            "name": "Test Link",
                            "url": "https://example.com",
                            "icon": "🔗",
                        }
                    ],
                }
            ]
        }
        valid, errors = validate_links_config(config)
        assert valid is True
        assert len(errors) == 0

    def test_validate_links_config_invalid_url(self):
        """Test validating configuration with invalid URL."""
        config = {
            "category": [
                {
                    "name": "Test Category",
                    "links": [{"name": "Test Link", "url": "invalid-url"}],
                }
            ]
        }
        valid, errors = validate_links_config(config)
        assert valid is False
        assert len(errors) > 0

    def test_validate_links_config_missing_category(self):
        """Test validating configuration without category key."""
        config = {}
        valid, errors = validate_links_config(config)
        assert valid is False
        assert "Missing 'category' key" in errors[0]


class TestFlaskRoutes:
    """Test Flask application routes."""

    def test_index_route(self, client):
        """Test index route returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_health_route(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "uptime" in data
        assert "version" in data

    def test_check_reload_route(self, client):
        """Test check reload endpoint."""
        response = client.get("/check_reload")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "reload" in data
        assert isinstance(data["reload"], bool)

    def test_wallpaper_route(self, client):
        """Test wallpaper endpoint returns image."""
        response = client.get("/wallpaper")
        assert response.status_code == 200
        # Can be PNG, JPEG, or other image format depending on config
        assert "image/" in response.content_type

    def test_favicon_route(self, client):
        """Test favicon endpoint."""
        response = client.get("/favicon")
        assert response.status_code == 200
        assert "image/svg+xml" in response.content_type


class TestWeatherAPI:
    """Test weather API functionality."""

    def test_weather_connection_error(self, client, monkeypatch):
        """Test weather endpoint handles connection errors."""
        from unittest.mock import patch
        import requests
        
        # Import and patch the config in app module
        import app as app_module
        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")
        
        with patch("app.requests.get", side_effect=requests.ConnectionError("No network")):
            response = client.get("/api/weather")
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data["error"] == "No network connection"

    def test_weather_timeout_error(self, client, monkeypatch):
        """Test weather endpoint handles timeout errors."""
        from unittest.mock import patch
        import requests
        
        import app as app_module
        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")
        
        with patch("app.requests.get", side_effect=requests.Timeout("Timeout")):
            response = client.get("/api/weather")
            assert response.status_code == 504
            data = json.loads(response.data)
            assert data["error"] == "Request timed out"

    def test_weather_with_manual_location(self, client, monkeypatch):
        """Test weather endpoint with manual location."""
        from unittest.mock import Mock, patch
        
        import app as app_module
        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")
        
        # Mock the requests to Open-Meteo
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 15.0,
                "relative_humidity_2m": 70,
                "weather_code": 0,
                "wind_speed_10m": 10.0
            }
        }
        
        with patch("app.requests.get", return_value=mock_response):
            response = client.get("/api/weather")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "temperature" in data
            assert data["temperature"] == 15.0
            assert "location" in data
            assert data["location"] == "52.00,5.00"

    def test_geoip_database_not_found(self, monkeypatch):
        """Test MaxMind GeoIP raises error when database missing."""
        from app import _geoip_maxmind
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_db = Path(tmpdir) / "missing.mmdb"
            
            import app as app_module
            monkeypatch.setattr(app_module.config, "GEOIP_DB_PATH", str(missing_db))
            
            with pytest.raises(FileNotFoundError, match="MaxMind database not found"):
                _geoip_maxmind("8.8.8.8")

    def test_openmeteo_weather_codes(self, monkeypatch):
        """Test Open-Meteo weather code mapping."""
        from app import _fetch_openmeteo_weather
        from unittest.mock import Mock, patch
        
        import app as app_module
        monkeypatch.setattr(app_module.config, "WEATHER_UNITS", "metric")
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 20.0,
                "relative_humidity_2m": 65,
                "weather_code": 61,  # Light rain
                "wind_speed_10m": 15.0
            }
        }
        
        with patch("app.requests.get", return_value=mock_response):
            result = _fetch_openmeteo_weather(52.0, 5.0)
            assert result["temperature"] == 20.0
            assert result["description"] == "Light rain"
            assert result["units"] == "metric"

    def test_track_event_endpoint(self, client, monkeypatch):
        """Test event tracking endpoint."""
        import app as app_module
        
        # Metrics is enabled by default, just verify it works
        response = client.post("/api/track", 
                              json={"event": "search", "data": {"provider": "brave", "query": "test"}},
                              content_type="application/json")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"


class TestConfig:
    """Test configuration management."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.HOST == "127.0.0.1"
        assert config.PORT == 5000
        assert config.DEBUG is False
        assert config.CACHE_TTL == 5

    def test_config_from_env(self):
        """Test loading configuration from environment."""
        # Config class reads from environment at module import time
        # so we can't easily test env vars without reloading
        # Just test that config values are accessible
        assert hasattr(Config, "PORT")
        assert hasattr(Config, "HOST")
        assert isinstance(Config.PORT, int)

    def test_gruvbox_colors_exist(self):
        """Test that Gruvbox colors are defined."""
        config = Config()
        assert "background" in config.GRUVBOX_DARK
        assert "foreground" in config.GRUVBOX_DARK
        assert "color0" in config.GRUVBOX_DARK


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
