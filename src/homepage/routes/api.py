"""API routes (/api/stats, /api/track)."""

import logging
from typing import Any

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

_metrics: Any | None = None
_config: Any | None = None


def init_api_blueprint(metrics, config):
    """Initialize API blueprint with dependencies."""
    global _metrics, _config
    _metrics = metrics
    _config = config


@api_bp.route("/api/stats")
def stats():
    """Get metrics statistics."""
    assert _config is not None
    if not _config.ENABLE_METRICS or not _metrics:  # type: ignore[union-attr]
        return jsonify({"error": "Metrics not enabled"}), 404

    return jsonify(_metrics.get_stats())


@api_bp.route("/api/track", methods=["POST"])
def track():
    """Track events (searches, link clicks)."""
    assert _config is not None
    if not _config.ENABLE_METRICS or not _metrics:  # type: ignore[union-attr]
        return jsonify({"status": "disabled"}), 200

    data = request.get_json()
    if not data or "type" not in data:
        return jsonify({"error": "Invalid request"}), 400

    match data["type"]:
        case "search":
            if "query" in data and "provider" in data:
                _metrics.track_search(data["provider"], data["query"])
        case "link_click":
            if "name" in data and "url" in data:
                _metrics.track_link_click(data["name"], data["url"])
        case _:
            return jsonify({"error": "Unknown event type"}), 400

    return jsonify({"status": "ok"})
