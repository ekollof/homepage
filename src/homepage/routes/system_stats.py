"""System stats API routes."""

import logging
from typing import TYPE_CHECKING, Optional

from flask import Blueprint, jsonify, request

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


@system_stats_bp.route("/api/system-stats/cpu-governor", methods=["POST"])
def set_cpu_governor():
    """Set CPU governor for all CPUs (Linux only)."""
    assert _config is not None

    if not _config.ENABLE_SYSTEM_STATS:
        return jsonify({"error": "System stats feature not enabled"}), 404

    try:
        data = request.get_json()
        if not data or "governor" not in data:
            return jsonify({"error": "Missing 'governor' parameter"}), 400

        governor = data["governor"]
        result = SystemStatsService.set_cpu_governor(governor)
        return jsonify(result), 200 if result.get("success") else 500

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to set CPU governor: %s", e)
        return jsonify({"error": str(e)}), 500


@system_stats_bp.route("/api/system-stats/io-scheduler", methods=["POST"])
def set_io_scheduler():
    """Set I/O scheduler for a block device (Linux only)."""
    assert _config is not None

    if not _config.ENABLE_SYSTEM_STATS:
        return jsonify({"error": "System stats feature not enabled"}), 404

    try:
        data = request.get_json()
        if not data or "device" not in data or "scheduler" not in data:
            return jsonify({"error": "Missing 'device' or 'scheduler' parameter"}), 400

        device = data["device"]
        scheduler = data["scheduler"]
        result = SystemStatsService.set_io_scheduler(device, scheduler)
        return jsonify(result), 200 if result.get("success") else 500

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to set I/O scheduler: %s", e)
        return jsonify({"error": str(e)}), 500


@system_stats_bp.route("/api/system-stats/freebsd-cpu-freq", methods=["POST"])
def set_freebsd_cpu_freq():
    """Set CPU frequency on FreeBSD."""
    assert _config is not None

    if not _config.ENABLE_SYSTEM_STATS:
        return jsonify({"error": "System stats feature not enabled"}), 404

    try:
        data = request.get_json()
        if not data or "freq" not in data:
            return jsonify({"error": "Missing 'freq' parameter"}), 400

        freq = int(data["freq"])
        result = SystemStatsService.set_freebsd_cpu_freq(freq)
        return jsonify(result), 200 if result.get("success") else 500

    except ValueError:
        return jsonify({"error": "Invalid frequency value"}), 400
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to set CPU frequency: %s", e)
        return jsonify({"error": str(e)}), 500
