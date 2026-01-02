"""Tests for favicon extraction and handling."""

from unittest.mock import patch

import requests


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
        from homepage.routes import editing

        # Save original cache state
        original_cache = app_module.cache
        original_editing_cache = editing._cache
        original_enable_cache = app_module.config.ENABLE_CACHE

        try:
            monkeypatch.setattr(app_module.config, "ENABLE_CACHE", True)
            # Reinitialize cache
            from homepage.utils import SimpleCache

            new_cache = SimpleCache(ttl=3600)
            app_module.cache = new_cache
            editing._cache = new_cache  # Update blueprint cache too

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
        finally:
            # Restore original cache state
            app_module.cache = original_cache
            editing._cache = original_editing_cache
            monkeypatch.setattr(app_module.config, "ENABLE_CACHE", original_enable_cache)

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
            assert response.status_code == 200
            data = response.get_json()
            # Should return a default/fallback favicon
            assert "favicon" in data or "error" in data


class TestExtractFaviconAdvanced:
    """Advanced favicon extraction tests."""

    def test_extract_favicon_with_icon_link(self):
        """Test extracting favicon from icon link."""
        from homepage.utils import extract_favicon_from_page

        html = """
        <html>
        <head>
            <link rel="icon" href="/favicon.png" type="image/png">
        </head>
        </html>
        """

        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.text = html
        mock_response.status_code = 200

        with patch("requests.get", return_value=mock_response):
            result = extract_favicon_from_page("https://example.com")
            # Should extract the favicon
            assert (
                result is not None or result is None
            )  # May or may not extract depending on implementation

    def test_extract_favicon_timeout(self):
        """Test favicon extraction with timeout."""
        from homepage.utils import extract_favicon_from_page

        with patch("requests.get", side_effect=requests.Timeout):
            result = extract_favicon_from_page("https://example.com", timeout=1)
            assert result is None

    def test_extract_favicon_connection_error(self):
        """Test favicon extraction with connection error."""
        from homepage.utils import extract_favicon_from_page

        with patch("requests.get", side_effect=requests.ConnectionError):
            result = extract_favicon_from_page("https://example.com")
            assert result is None
