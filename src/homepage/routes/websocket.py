"""WebSocket routes for real-time connection management."""

import logging
from typing import TYPE_CHECKING, Any, Optional

from flask import Blueprint, jsonify

if TYPE_CHECKING:
    from ..services.websocket_service import WebSocketService

logger = logging.getLogger(__name__)

websocket_bp = Blueprint("websocket", __name__)

# This will be set when blueprint is registered with app
_websocket_service: Optional["WebSocketService"] = None


def init_websocket_blueprint(websocket_service: "WebSocketService"):
    """Initialize the WebSocket blueprint with dependencies.

    Args:
        websocket_service: WebSocket service instance
    """
    global _websocket_service
    _websocket_service = websocket_service


@websocket_bp.route("/api/websocket/status")
def websocket_status():
    """Get WebSocket connection status and info.

    Returns:
        JSON response with WebSocket status information
    """
    if not _websocket_service or not _websocket_service.is_enabled():
        return jsonify(
            {
                "enabled": False,
                "connected_clients": 0,
                "message": "WebSocket support is disabled",
            }
        )

    return jsonify(
        {
            "enabled": True,
            "connected_clients": _websocket_service.get_connected_clients(),
            "message": "WebSocket service is active",
        }
    )


@websocket_bp.route("/api/websocket/info")
def websocket_info():
    """Get detailed WebSocket configuration info.

    Returns:
        JSON response with WebSocket configuration details
    """
    if not _websocket_service or not _websocket_service.is_enabled():
        return jsonify({"enabled": False})

    config = _websocket_service.config
    return jsonify(
        {
            "enabled": True,
            "async_mode": config.WEBSOCKET_ASYNC_MODE,
            "ping_timeout": config.WEBSOCKET_PING_TIMEOUT,
            "ping_interval": config.WEBSOCKET_PING_INTERVAL,
            "connected_clients": _websocket_service.get_connected_clients(),
        }
    )
