"""Tests for utility functions and helpers."""

import time
from pathlib import Path

from homepage.metrics import MetricsCollector
from homepage.utils import (
    SimpleCache,
    load_json_file,
    load_text_file,
    validate_links_config,
    validate_url,
)


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


class TestCacheDecorator:
    """Test cache_with_ttl decorator."""

    def test_cache_with_ttl_decorator(self):
        """Test cache_with_ttl decorator caches function results."""
        from homepage.utils import SimpleCache, cache_with_ttl

        cache = SimpleCache(ttl=5)
        call_count = [0]

        @cache_with_ttl(cache, "test_key")
        def expensive_function():
            call_count[0] += 1
            return "result"

        # First call should execute function
        result1 = expensive_function()
        assert result1 == "result"
        assert call_count[0] == 1

        # Second call should use cache
        result2 = expensive_function()
        assert result2 == "result"
        assert call_count[0] == 1  # Still 1, not incremented


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


class TestValidateUrlAdvanced:
    """Additional URL validation tests."""

    def test_validate_url_with_query_params(self):
        """Test validating URL with query parameters."""
        url = "https://example.com/path?key=value&foo=bar"
        assert validate_url(url) is True

    def test_validate_url_with_fragment(self):
        """Test validating URL with fragment."""
        url = "https://example.com/path#section"
        assert validate_url(url) is True

    def test_validate_url_relative(self):
        """Test validating relative URL."""
        url = "/path/to/page"
        assert validate_url(url) is False

    def test_validate_url_ipv4(self):
        """Test validating IPv4 URL."""
        url = "http://192.168.1.1:8080"
        assert validate_url(url) is True


class TestLoadTomlFile:
    """Test TOML file loading."""

    def test_load_toml_file_success(self, tmp_path):
        """Test loading valid TOML file."""
        from homepage.utils import load_toml_file

        toml_file = tmp_path / "test.toml"
        toml_file.write_text("[section]\nkey = 'value'\n")

        result = load_toml_file(toml_file)
        assert result == {"section": {"key": "value"}}

    def test_load_toml_file_not_found(self, tmp_path):
        """Test loading non-existent TOML file returns default."""
        from homepage.utils import load_toml_file

        result = load_toml_file(tmp_path / "nonexistent.toml", default={})
        assert result == {}

    def test_load_toml_file_invalid(self, tmp_path):
        """Test loading invalid TOML file returns default."""
        from homepage.utils import load_toml_file

        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("invalid: [toml: content")

        result = load_toml_file(toml_file, default={})
        assert result == {}
