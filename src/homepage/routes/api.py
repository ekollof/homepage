"""API routes (/api/stats, /api/track)."""

import logging

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

_metrics = None
_config = None


def init_api_blueprint(metrics, config):
    """Initialize API blueprint with dependencies."""
    global _metrics, _config
    _metrics = metrics
    _config = config


@api_bp.route("/api/stats")
def stats():
    """Get metrics statistics."""
    if not _config.ENABLE_METRICS or not _metrics:
        return jsonify({"error": "Metrics not enabled"}), 404

    return jsonify(_metrics.get_stats())


@api_bp.route("/api/track", methods=["POST"])
def track():
    """Track events (searches, link clicks)."""
    if not _config.ENABLE_METRICS or not _metrics:
        return jsonify({"status": "disabled"}), 200

    data = request.get_json()
    if not data or "type" not in data:
        return jsonify({"error": "Invalid request"}), 400

    match data["type"]:
        case "search":
            if "query" in data and "provider" in data:
                _metrics.track_search(data["query"], data["provider"])
        case "link_click":
            if "link" in data:
                _metrics.track_link_click(data["link"])
        case _:
            return jsonify({"error": "Unknown event type"}), 400

    return jsonify({"status": "ok"})
