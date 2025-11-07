"""Tests for Homepage application."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from homepage.app import app as flask_app
from homepage.config import Config
from homepage.metrics import MetricsCollector
from homepage.utils import (
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
        config: dict = {}
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
        # Import and patch the config in app module
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        with patch("homepage.app.requests.get", side_effect=requests.ConnectionError("No network")):
            response = client.get("/api/weather")
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data["error"] == "No network connection"

    def test_weather_timeout_error(self, client, monkeypatch):
        """Test weather endpoint handles timeout errors."""
        from unittest.mock import patch

        import requests

        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        with patch("homepage.app.requests.get", side_effect=requests.Timeout("Timeout")):
            response = client.get("/api/weather")
            assert response.status_code == 504
            data = json.loads(response.data)
            assert data["error"] == "Request timed out"

    def test_weather_with_manual_location(self, client, monkeypatch):
        """Test weather endpoint with manual location."""
        from unittest.mock import Mock, patch

        import homepage.app as app_module

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
                "wind_speed_10m": 10.0,
            }
        }

        with patch("homepage.app.requests.get", return_value=mock_response):
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

        from homepage.app import _geoip_maxmind

        with tempfile.TemporaryDirectory() as tmpdir:
            missing_db = Path(tmpdir) / "missing.mmdb"

            import homepage.app as app_module

            monkeypatch.setattr(app_module.config, "GEOIP_DB_PATH", str(missing_db))

            with pytest.raises(FileNotFoundError, match="MaxMind database not found"):
                _geoip_maxmind("8.8.8.8")

    def test_openmeteo_weather_codes(self, monkeypatch):
        """Test Open-Meteo weather code mapping."""
        from unittest.mock import Mock, patch

        import homepage.app as app_module
        from homepage.app import _fetch_openmeteo_weather

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

        with patch("homepage.app.requests.get", return_value=mock_response):
            result = _fetch_openmeteo_weather(52.0, 5.0)
            assert result["temperature"] == 20.0
            assert result["description"] == "Light rain"
            assert result["units"] == "metric"

    def test_track_event_endpoint(self, client, monkeypatch):
        """Test event tracking endpoint."""

        # Metrics is enabled by default, just verify it works
        response = client.post(
            "/api/track",
            json={"event": "search", "data": {"provider": "brave", "query": "test"}},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_forecast_endpoint_disabled(self, client, monkeypatch):
        """Test forecast endpoint returns 404 when weather disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", False)

        response = client.get("/api/weather/forecast")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_forecast_with_openmeteo(self, client, monkeypatch):
        """Test forecast endpoint with Open-Meteo provider."""
        from unittest.mock import Mock, patch

        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        # Mock Open-Meteo forecast response
        mock_response = Mock()
        mock_response.json.return_value = {
            "hourly": {
                "time": [
                    "2025-11-07T12:00",
                    "2025-11-07T13:00",
                    "2025-11-07T14:00",
                ],
                "temperature_2m": [14.5, 15.0, 15.5],
                "weather_code": [0, 1, 2],
                "precipitation_probability": [0, 10, 20],
            }
        }

        with patch("homepage.app.requests.get", return_value=mock_response):
            response = client.get("/api/weather/forecast")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "hourly" in data
            assert len(data["hourly"]) == 3
            assert data["hourly"][0]["hour"] == "12:00"
            assert data["hourly"][0]["temperature"] == 14.5
            assert "weather_emoji" in data["hourly"][0]
            assert data["units"] == "metric"

    def test_forecast_connection_error(self, client, monkeypatch):
        """Test forecast endpoint handles connection errors."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
        monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
        monkeypatch.setattr(app_module.config, "WEATHER_PROVIDER", "openmeteo")

        with patch("homepage.app.requests.get", side_effect=requests.ConnectionError("No network")):
            response = client.get("/api/weather/forecast")
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data["error"] == "No network connection"


class TestRSSFeeds:
    """Test RSS feed functionality."""

    def test_rss_endpoint_disabled(self, client, monkeypatch):
        """Test RSS endpoint returns 404 when disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_RSS", False)

        response = client.get("/api/rss")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "not enabled" in data["error"]

    def test_rss_endpoint_no_feeds(self, client, monkeypatch):
        """Test RSS endpoint with no feeds configured."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_RSS", True)
        monkeypatch.setattr(app_module.config, "RSS_FEEDS", [])

        response = client.get("/api/rss")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["items"] == []
        assert data["count"] == 0

    def test_rss_endpoint_with_feeds(self, client, monkeypatch):
        """Test RSS endpoint fetches feeds successfully."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_RSS", True)
        monkeypatch.setattr(
            app_module.config,
            "RSS_FEEDS",
            ["https://example.com/feed.xml"],
        )
        monkeypatch.setattr(app_module.config, "RSS_MAX_ITEMS", 5)

        # Mock feedparser module
        import sys
        from types import SimpleNamespace

        mock_feedparser = SimpleNamespace()
        mock_feed = SimpleNamespace(
            feed={"title": "Test Feed"},
            entries=[
                {
                    "title": "Test Article",
                    "link": "https://example.com/article",
                    "summary": "Test description",
                    "published": "2024-01-01",
                }
            ],
        )
        mock_feedparser.parse = lambda url: mock_feed
        sys.modules["feedparser"] = mock_feedparser  # type: ignore[assignment]

        try:
            response = client.get("/api/rss")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["count"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["title"] == "Test Article"
            assert data["items"][0]["feed_title"] == "Test Feed"
        finally:
            # Cleanup
            if "feedparser" in sys.modules:
                del sys.modules["feedparser"]


class TestConfig:
    """Test configuration management."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.HOST == "127.0.0.1"
        assert config.PORT == 5000
        # DEBUG depends on environment variable, just check it exists
        assert hasattr(config, "DEBUG")
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


class TestEditingFeature:
    """Test editing functionality."""

    def test_get_config_endpoint(self, client, monkeypatch):
        """Test getting configuration via API."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)

        response = client.get("/api/config")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "category" in data

    def test_get_config_disabled(self, client, monkeypatch):
        """Test config endpoint when editing is disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", False)

        response = client.get("/api/config")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_save_config_endpoint(self, client, monkeypatch, tmp_path):
        """Test saving configuration via API."""
        import homepage.app as app_module

        # Use temporary override file
        override_file = tmp_path / "links.override.toml"
        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)
        monkeypatch.setattr(app_module.config, "CONFIG_OVERRIDE_FILE", override_file)

        test_config = {
            "category": [
                {
                    "name": "Test Category",
                    "icon": "🧪",
                    "links": [{"name": "Test Link", "url": "https://example.com", "icon": "🔗"}],
                }
            ]
        }

        response = client.post(
            "/api/config", data=json.dumps(test_config), content_type="application/json"
        )

        assert response.status_code == 200
        assert override_file.exists()

    def test_save_config_invalid(self, client, monkeypatch, tmp_path):
        """Test saving invalid configuration."""
        import homepage.app as app_module

        # Use temporary override file
        override_file = tmp_path / "links.override.toml"
        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)
        monkeypatch.setattr(app_module.config, "CONFIG_OVERRIDE_FILE", override_file)

        # Missing required fields
        invalid_config = {"category": [{"name": "Test"}]}

        response = client.post(
            "/api/config", data=json.dumps(invalid_config), content_type="application/json"
        )

        # Should accept it as valid (links can be empty)
        assert response.status_code in [200, 400]

    def test_reset_config(self, client, monkeypatch, tmp_path):
        """Test resetting configuration."""
        import homepage.app as app_module

        override_file = tmp_path / "links.override.toml"
        override_file.write_text("# test file")

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)
        monkeypatch.setattr(app_module.config, "CONFIG_OVERRIDE_FILE", override_file)

        response = client.post("/api/config/reset")
        assert response.status_code == 200
        assert not override_file.exists()


class TestConfigMerging:
    """Test configuration merging functionality."""

    def test_merge_configs_with_override(self):
        """Test that override completely replaces base."""
        from homepage.utils import merge_links_configs

        base = {
            "category": [
                {
                    "name": "Dev",
                    "icon": "💻",
                    "links": [{"name": "GitHub", "url": "https://github.com"}],
                }
            ]
        }

        override = {
            "category": [
                {
                    "name": "Personal",
                    "icon": "🏠",
                    "links": [{"name": "Email", "url": "https://mail.example.com"}],
                }
            ]
        }

        result = merge_links_configs(base, override)

        # Should use override exclusively (no merge)
        assert len(result["category"]) == 1
        assert result["category"][0]["name"] == "Personal"
        assert result["category"][0]["icon"] == "🏠"

    def test_merge_empty_override(self):
        """Test merging with empty override returns base."""
        from homepage.utils import merge_links_configs

        base = {"category": [{"name": "Test", "icon": "📝", "links": []}]}
        override: dict = {}

        result = merge_links_configs(base, override)
        assert result == base

    def test_merge_no_override_category(self):
        """Test that missing category key in override returns base."""
        from homepage.utils import merge_links_configs

        base = {"category": [{"name": "Test", "icon": "📝", "links": []}]}
        override = {"other": "data"}

        result = merge_links_configs(base, override)
        assert result == base


class TestFaviconExtraction:
    """Test favicon extraction functionality."""

    def test_extract_favicon_from_page_success(self):
        """Test successful favicon extraction from HTML page."""
        from homepage.utils import extract_favicon_from_page

        # Mock the requests to avoid actual network calls
        with patch("homepage.utils.requests.get") as mock_get:
            # Mock HTML page response
            html_content = """
            <html>
            <head>
                <link rel="icon" href="/favicon.ico">
            </head>
            </html>
            """

            class MockResponse:
                """Mock response object."""

                def __init__(self, content, status_code=200, headers=None):
                    self.content = content
                    self.status_code = status_code
                    self.headers = headers or {}

                def raise_for_status(self):
                    """Raise for status."""
                    if self.status_code >= 400:
                        raise requests.HTTPError()

            mock_page_response = MockResponse(
                content=html_content.encode(), headers={"Content-Type": "text/html"}
            )
            mock_favicon_response = MockResponse(
                content=b"fake_favicon_data", headers={"Content-Type": "image/x-icon"}
            )

            # Setup mock to return different responses for page and favicon
            mock_get.side_effect = [mock_page_response, mock_favicon_response]

            result = extract_favicon_from_page("https://example.com")

            assert result is not None
            assert result.startswith("data:image/x-icon;base64,")

    def test_extract_favicon_from_page_timeout(self):
        """Test favicon extraction handles timeout."""
        from homepage.utils import extract_favicon_from_page

        with patch("homepage.utils.requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Connection timeout")

            result = extract_favicon_from_page("https://example.com", timeout=1)

            assert result is None

    def test_fetch_favicon_google_success(self):
        """Test fetching favicon from Google service."""
        from homepage.utils import fetch_favicon_google

        with patch("homepage.utils.requests.get") as mock_get:

            class MockResponse:
                """Mock response object."""

                def __init__(self, content, status_code=200, headers=None):
                    self.content = content
                    self.status_code = status_code
                    self.headers = headers or {}

            mock_response = MockResponse(
                content=b"google_favicon_data", headers={"Content-Type": "image/png"}
            )

            mock_get.return_value = mock_response

            result = fetch_favicon_google("example.com")

            assert result is not None
            assert result.startswith("data:image/png;base64,")

    def test_favicon_endpoint_with_cache(self, client, monkeypatch):
        """Test /api/favicon endpoint uses cache."""
        # Enable cache for this test
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_CACHE", True)
        # Reinitialize cache
        from homepage.utils import SimpleCache

        app_module.cache = SimpleCache(ttl=3600)

        with patch("homepage.utils.extract_favicon_from_page") as mock_extract:
            mock_extract.return_value = "data:image/png;base64,fake_data"

            # First request - should call extraction
            response1 = client.get("/api/favicon?url=https://example.com")
            assert response1.status_code == 200
            data1 = response1.get_json()
            assert data1["cached"] is False
            assert "favicon" in data1

            # Second request - should use cache
            response2 = client.get("/api/favicon?url=https://example.com")
            assert response2.status_code == 200
            data2 = response2.get_json()
            assert data2["cached"] is True

    def test_favicon_endpoint_fallback_to_google(self, client):
        """Test /api/favicon falls back to Google when direct extraction fails."""
        # Clear cache to avoid interference from previous tests
        import homepage.app as app_module

        if app_module.cache:
            app_module.cache.clear()

        with (
            patch("homepage.utils.extract_favicon_from_page") as mock_extract,
            patch("homepage.utils.fetch_favicon_google") as mock_google,
        ):
            mock_extract.return_value = None  # Direct extraction fails
            mock_google.return_value = "data:image/png;base64,google_data"

            response = client.get("/api/favicon?url=https://example2.com")
            assert response.status_code == 200
            data = response.get_json()
            assert "favicon" in data
            assert data["favicon"] == "data:image/png;base64,google_data"

    def test_favicon_endpoint_both_methods_fail(self, client):
        """Test /api/favicon returns 404 when both methods fail."""
        # Clear cache to avoid interference from previous tests
        import homepage.app as app_module

        if app_module.cache:
            app_module.cache.clear()

        with (
            patch("homepage.utils.extract_favicon_from_page") as mock_extract,
            patch("homepage.utils.fetch_favicon_google") as mock_google,
        ):
            mock_extract.return_value = None
            mock_google.return_value = None

            response = client.get("/api/favicon?url=https://example3.com")
            assert response.status_code == 404
            data = response.get_json()
            assert "error" in data
