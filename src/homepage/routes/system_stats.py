"""System stats API routes."""

import logging
from typing import TYPE_CHECKING, Optional

from flask import Blueprint, jsonify

from ..services.system_stats_service import SystemStatsService

if TYPE_CHECKING:
    from ..config import Config

logger = logging.getLogger(__name__)

system_stats_bp = Blueprint("system_stats", __name__)

_config: Optional["Config"] = None


def init_system_stats_blueprint(config):
    """Initialize system stats blueprint with dependencies."""
    global _config
    _config = config


@system_stats_bp.route("/api/system-stats")
def get_system_stats():
    """Get real-time system statistics."""
    assert _config is not None

    if not _config.ENABLE_SYSTEM_STATS:
        return jsonify({"error": "System stats feature not enabled"}), 404

    try:
        stats = SystemStatsService.get_stats()
        return jsonify(stats)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("System stats error: %s", e)
        return jsonify({"error": "Failed to fetch system stats"}), 500
