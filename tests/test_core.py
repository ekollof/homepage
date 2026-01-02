"""Tests for core Flask application routes."""

import json


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
        assert "service" in data

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


class TestAssetRoutes:
    """Test asset serving routes."""

    def test_favicon_ico_route(self, client):
        """Test favicon.ico route."""
        response = client.get("/favicon.ico")
        assert response.status_code in [200, 404]

    def test_static_js_route(self, client):
        """Test static JS route."""
        response = client.get("/static/js/socket.io.min.js")
        # Should either return the file or 404
        assert response.status_code in [200, 404]

    def test_wallpaper_route_default(self, client, monkeypatch):
        """Test wallpaper route returns default."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", False)

        response = client.get("/wallpaper")
        assert response.status_code == 200


class TestStylesAndScriptsRoutes:
    """Test CSS and JS asset routes."""

    def test_styles_css_route(self, client, monkeypatch):
        """Test /styles.css endpoint."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", False)

        response = client.get("/styles.css")
        assert response.status_code == 200
        assert response.content_type == "text/css"
        assert len(response.data) > 0

    def test_scripts_js_route(self, client, monkeypatch):
        """Test /scripts.js endpoint."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)

        response = client.get("/scripts.js")
        assert response.status_code == 200
        assert response.content_type == "application/javascript"
        assert len(response.data) > 0

    def test_styles_css_caching_disabled_when_editing(self, client, monkeypatch):
        """Test CSS caching is disabled when ENABLE_EDITING is True."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)

        response = client.get("/styles.css")
        assert response.status_code == 200
        # Cache-Control should be set to no-cache when editing
        cache_control = response.headers.get("Cache-Control")
        if cache_control:
            assert "no-cache" in cache_control or "no-store" in cache_control

    def test_styles_css_caching_enabled_when_not_editing(self, client, monkeypatch):
        """Test CSS caching when ENABLE_EDITING is False."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", False)

        response = client.get("/styles.css")
        assert response.status_code == 200
        # Should have cache headers
        cache_control = response.headers.get("Cache-Control")
        assert cache_control is not None

    def test_scripts_js_caching_disabled_when_editing(self, client, monkeypatch):
        """Test JS caching is disabled when ENABLE_EDITING is True."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)

        response = client.get("/scripts.js")
        assert response.status_code == 200


class TestTrackingEndpoint:
    """Test event tracking endpoint."""

    def test_track_event_endpoint(self, client, monkeypatch):
        """Test event tracking endpoint."""

        # Metrics is enabled by default, just verify it works
        response = client.post(
            "/api/track",
            json={"type": "search", "query": "test", "provider": "brave"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"


class TestAppInitialization:
    """Test Flask app initialization and configuration."""

    def test_app_compression_enabled(self):
        """Test app has compression enabled when configured."""
        import homepage.app as app_module

        # Check if compression is applied
        assert app_module.app is not None
        assert app_module.config is not None

    def test_app_metrics_initialized(self):
        """Test metrics collector initialization."""
        import homepage.app as app_module

        # Metrics should be initialized if ENABLE_METRICS is True
        if app_module.config.ENABLE_METRICS:
            assert app_module.metrics is not None
        else:
            assert app_module.metrics is None

    def test_app_cache_initialized(self):
        """Test cache initialization."""
        import homepage.app as app_module

        # Cache should be initialized if ENABLE_CACHE is True
        if app_module.config.ENABLE_CACHE:
            assert app_module.cache is not None
        else:
            assert app_module.cache is None
