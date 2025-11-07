"""Tests for WebSocket service."""

import pytest
from flask import Flask

from homepage.config import Config
from homepage.services.websocket_service import WebSocketService, init_websocket_service

try:
    from flask_socketio import SocketIO
except ImportError:
    SocketIO = None  # type: ignore[misc, assignment]


class TestConfig(Config):
    """Test configuration."""

    TESTING: bool = True
    ENABLE_WEBSOCKET: bool = True  # type: ignore[misc]
    WEBSOCKET_ASYNC_MODE: str = "threading"  # type: ignore[misc]
    WEBSOCKET_PING_TIMEOUT: int = 10  # type: ignore[misc]
    WEBSOCKET_PING_INTERVAL: int = 5  # type: ignore[misc]


class TestWebSocketService:
    """Test WebSocketService class."""

    def test_init_without_app(self):
        """Test initializing service without app."""
        config = TestConfig()
        service = WebSocketService(config=config)
        assert service.socketio is None
        assert service.config == config

    def test_init_with_app(self):
        """Test initializing service with app."""
        app = Flask(__name__)
        config = TestConfig()
        service = WebSocketService(app, config)
        assert service.socketio is not None
        if SocketIO is not None:
            assert isinstance(service.socketio, SocketIO)

    def test_init_app_disabled(self):
        """Test init_app when WebSocket is disabled."""
        app = Flask(__name__)

        class DisabledConfig(Config):
            ENABLE_WEBSOCKET: bool = False  # type: ignore[misc]

        config = DisabledConfig()
        service = WebSocketService(config=config)
        service.init_app(app)
        assert service.socketio is None

    def test_is_enabled(self):
        """Test is_enabled method."""
        app = Flask(__name__)
        config = TestConfig()
        service = WebSocketService(app, config)
        assert service.is_enabled() is True

    def test_is_disabled(self):
        """Test is_enabled when disabled."""

        class DisabledConfig(Config):
            ENABLE_WEBSOCKET: bool = False  # type: ignore[misc]

        config = DisabledConfig()
        service = WebSocketService(config=config)
        assert service.is_enabled() is False

    def test_get_connected_clients(self):
        """Test getting connected clients count."""
        app = Flask(__name__)
        config = TestConfig()
        service = WebSocketService(app, config)
        assert service.get_connected_clients() == 0

    def test_emit_without_socketio(self):
        """Test emit methods when socketio is None."""
        config = TestConfig()
        service = WebSocketService(config=config)
        # Should not raise errors
        service.emit_config_change("colors")
        service.emit_system_stats({})
        service.emit_weather_update({})
        service.emit_rss_update({})
        service.emit_links_update([])


class TestWebSocketIntegration:
    """Test WebSocket integration with Flask app."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with WebSocket."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        config = TestConfig()
        service = init_websocket_service(app, config)
        app.websocket_service = service  # type: ignore[attr-defined]
        return app

    @pytest.fixture
    def socketio_client(self, app):
        """Create SocketIO test client."""
        if hasattr(app, "websocket_service"):
            service = app.websocket_service  # type: ignore[attr-defined]
            if service and service.socketio:
                return service.socketio.test_client(app)
        return None

    def test_client_connect(self, socketio_client):
        """Test client connection."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        assert socketio_client.is_connected()

    def test_client_disconnect(self, socketio_client):
        """Test client disconnection."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        socketio_client.disconnect()
        assert not socketio_client.is_connected()

    def test_ping_pong(self, app, socketio_client):
        """Test ping/pong mechanism."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        # Send ping
        socketio_client.emit("ping")

        # Receive pong
        received = socketio_client.get_received()
        assert len(received) > 0
        # First message might be 'connected', look for 'pong'
        pong_found = any(msg["name"] == "pong" for msg in received)
        assert pong_found

    def test_config_change_event(self, app, socketio_client):
        """Test config change event emission."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        service = app.websocket_service  # type: ignore[attr-defined]

        # Clear any previous messages
        socketio_client.get_received()

        # Emit config change
        service.emit_config_change("colors")

        # Check if event was received
        received = socketio_client.get_received()
        assert len(received) > 0

        config_change_msg = next((msg for msg in received if msg["name"] == "config_changed"), None)
        assert config_change_msg is not None
        assert config_change_msg["args"][0]["type"] == "colors"
        assert config_change_msg["args"][0]["action"] == "reload"

    def test_system_stats_event(self, app, socketio_client):
        """Test system stats event emission."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        service = app.websocket_service  # type: ignore[attr-defined]
        socketio_client.get_received()  # Clear

        stats = {
            "cpu_percent": 50.0,
            "memory_percent": 60.0,
            "disk_percent": 70.0,
        }

        service.emit_system_stats(stats)

        received = socketio_client.get_received()
        stats_msg = next((msg for msg in received if msg["name"] == "system_stats_update"), None)
        assert stats_msg is not None
        assert stats_msg["args"][0]["cpu_percent"] == 50.0

    def test_weather_update_event(self, app, socketio_client):
        """Test weather update event emission."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        service = app.websocket_service  # type: ignore[attr-defined]
        socketio_client.get_received()  # Clear

        weather_data = {
            "temperature": 20.0,
            "humidity": 65,
            "description": "Sunny",
        }

        service.emit_weather_update(weather_data)

        received = socketio_client.get_received()
        weather_msg = next((msg for msg in received if msg["name"] == "weather_update"), None)
        assert weather_msg is not None
        assert weather_msg["args"][0]["temperature"] == 20.0

    def test_rss_update_event(self, app, socketio_client):
        """Test RSS update event emission."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        service = app.websocket_service  # type: ignore[attr-defined]
        socketio_client.get_received()  # Clear

        rss_data = {
            "items": [
                {"title": "Test Article", "link": "https://example.com"},
            ]
        }

        service.emit_rss_update(rss_data)

        received = socketio_client.get_received()
        rss_msg = next((msg for msg in received if msg["name"] == "rss_update"), None)
        assert rss_msg is not None
        assert len(rss_msg["args"][0]["items"]) == 1

    def test_links_update_event(self, app, socketio_client):
        """Test links update event emission."""
        if socketio_client is None:
            pytest.skip("SocketIO client not available")

        service = app.websocket_service  # type: ignore[attr-defined]
        socketio_client.get_received()  # Clear

        links_data = [
            {
                "name": "Development",
                "icon": "💻",
                "links": [{"name": "GitHub", "url": "https://github.com", "icon": "🔗"}],
            }
        ]

        service.emit_links_update(links_data)

        received = socketio_client.get_received()
        links_msg = next((msg for msg in received if msg["name"] == "links_update"), None)
        assert links_msg is not None
        assert len(links_msg["args"][0]["categories"]) == 1

    def test_multiple_clients(self, app):
        """Test multiple client connections."""
        if not hasattr(app, "websocket_service"):
            pytest.skip("SocketIO not available")

        service = app.websocket_service  # type: ignore[attr-defined]
        if not service or service.socketio is None:
            pytest.skip("SocketIO not available")

        client1 = service.socketio.test_client(app)
        client2 = service.socketio.test_client(app)

        assert client1.is_connected()
        assert client2.is_connected()

        # Both should receive config change
        client1.get_received()
        client2.get_received()

        service.emit_config_change("wallpaper")

        received1 = client1.get_received()
        received2 = client2.get_received()

        assert any(msg["name"] == "config_changed" for msg in received1)
        assert any(msg["name"] == "config_changed" for msg in received2)

        client1.disconnect()
        client2.disconnect()


def test_init_websocket_service():
    """Test init_websocket_service function."""
    app = Flask(__name__)
    config = TestConfig()
    service = init_websocket_service(app, config)

    assert service is not None
    assert isinstance(service, WebSocketService)
    assert service.socketio is not None
