"""Tests for RSS feed functionality."""

import json
from unittest.mock import patch


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

        # Mock the RSSService.fetch_feeds method directly
        mock_feeds = [
            {
                "title": "Test Article",
                "link": "https://example.com/article",
                "description": "Test description",
                "published": "2024-01-01",
                "feed_title": "Test Feed",
            }
        ]

        with patch("homepage.services.rss_service.RSSService.fetch_feeds", return_value=mock_feeds):
            response = client.get("/api/rss")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["count"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["title"] == "Test Article"
            assert data["items"][0]["feed_title"] == "Test Feed"


class TestRSSServiceBasic:
    """Basic RSS service tests."""

    def test_fetch_feeds_empty(self):
        """Test fetching feeds with empty list."""
        from homepage.services.rss_service import RSSService

        result = RSSService.fetch_feeds([])
        assert result == []

    def test_fetch_feeds_invalid_url(self):
        """Test fetching with invalid URL."""
        from homepage.services.rss_service import RSSService

        result = RSSService.fetch_feeds(["not a valid url"])
        # Should return empty list
        assert isinstance(result, list)
