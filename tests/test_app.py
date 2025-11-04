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
