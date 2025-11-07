"""WebSocket service for real-time updates."""

import logging
from typing import TYPE_CHECKING, Any

from flask_socketio import SocketIO, emit

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)


class WebSocketService:
    """Service for managing WebSocket connections and real-time updates."""

    __slots__ = ("socketio", "config", "_connected_clients")

    def __init__(self, app: "Flask | None" = None, config: Any = None):
        """Initialize WebSocket service.

        Args:
            app: Flask application instance
            config: Configuration object
        """
        self.socketio: SocketIO | None = None
        self.config = config
        self._connected_clients = 0

        if app is not None:
            self.init_app(app)

    def init_app(self, app: "Flask"):
        """Initialize SocketIO with Flask app.

        Args:
            app: Flask application instance
        """
        if not self.config or not self.config.ENABLE_WEBSOCKET:
            logger.info("WebSocket support is disabled")
            return

        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode=self.config.WEBSOCKET_ASYNC_MODE,
            ping_timeout=self.config.WEBSOCKET_PING_TIMEOUT,
            ping_interval=self.config.WEBSOCKET_PING_INTERVAL,
            logger=False,
            engineio_logger=False,
        )

        self._register_handlers()
        logger.info(
            "WebSocket service initialized (async_mode=%s)", self.config.WEBSOCKET_ASYNC_MODE
        )

    def _register_handlers(self):
        """Register WebSocket event handlers."""
        if not self.socketio:
            return

        @self.socketio.on("connect")
        def handle_connect():
            """Handle client connection."""
            self._connected_clients += 1
            logger.info("Client connected (total: %d)", self._connected_clients)
            emit("connected", {"status": "ok", "message": "Connected to homepage server"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle client disconnection."""
            self._connected_clients = max(0, self._connected_clients - 1)
            logger.info("Client disconnected (remaining: %d)", self._connected_clients)

        @self.socketio.on("ping")
        def handle_ping():
            """Handle ping from client."""
            emit("pong", {"timestamp": self._get_timestamp()})

    def emit_config_change(self, change_type: str):
        """Emit configuration change event to all connected clients.

        Args:
            change_type: Type of change (colors, wallpaper, links)
        """
        if not self.socketio:
            return

        logger.info("Emitting config change: %s", change_type)
        self.socketio.emit(
            "config_changed",
            {
                "type": change_type,
                "timestamp": self._get_timestamp(),
                "action": "reload",
            },
        )

    def emit_system_stats(self, stats: dict[str, Any]):
        """Emit system stats update to all connected clients.

        Args:
            stats: System statistics dictionary
        """
        if not self.socketio:
            return

        self.socketio.emit("system_stats_update", stats)

    def emit_weather_update(self, weather_data: dict[str, Any]):
        """Emit weather update to all connected clients.

        Args:
            weather_data: Weather data dictionary
        """
        if not self.socketio:
            return

        self.socketio.emit("weather_update", weather_data)

    def emit_rss_update(self, rss_data: dict[str, Any]):
        """Emit RSS feed update to all connected clients.

        Args:
            rss_data: RSS feed data dictionary
        """
        if not self.socketio:
            return

        self.socketio.emit("rss_update", rss_data)

    def emit_links_update(self, links_data: list[dict[str, Any]]):
        """Emit links update to all connected clients.

        Args:
            links_data: Updated links configuration
        """
        if not self.socketio:
            return

        logger.info("Emitting links update")
        self.socketio.emit("links_update", {"categories": links_data})

    def get_connected_clients(self) -> int:
        """Get number of connected clients.

        Returns:
            Number of connected WebSocket clients
        """
        return self._connected_clients

    def is_enabled(self) -> bool:
        """Check if WebSocket is enabled.

        Returns:
            True if WebSocket is enabled, False otherwise
        """
        return self.socketio is not None

    @staticmethod
    def _get_timestamp() -> int:
        """Get current timestamp in milliseconds.

        Returns:
            Current timestamp
        """
        from time import time

        return int(time() * 1000)


# Global instance to be initialized by app
websocket_service: WebSocketService | None = None


def get_websocket_service() -> WebSocketService | None:
    """Get the global WebSocket service instance.

    Returns:
        WebSocket service instance or None if not initialized
    """
    return websocket_service


def init_websocket_service(app: "Flask", config: Any) -> WebSocketService:
    """Initialize the global WebSocket service.

    Args:
        app: Flask application instance
        config: Configuration object

    Returns:
        Initialized WebSocket service instance
    """
    global websocket_service
    websocket_service = WebSocketService(app, config)
    return websocket_service
