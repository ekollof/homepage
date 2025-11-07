"""Link editing API routes."""

import logging
import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional

from flask import Blueprint, jsonify, request

if TYPE_CHECKING:
    from ..config import Config
    from ..utils import SimpleCache

logger = logging.getLogger(__name__)

editing_bp = Blueprint("editing", __name__)

_config: Optional["Config"] = None
_cache: Optional["SimpleCache"] = None
_load_links: Callable[[], list[dict[str, Any]]] | None = None
_load_toml_file: Callable[[Any, Any], Any] | None = None
_file_watcher_state: dict[str, Any] | None = None


def init_editing_blueprint(config, cache, load_links, load_toml_file, file_watcher_state):
    """Initialize editing blueprint with dependencies."""
    global _config, _cache, _load_links, _load_toml_file, _file_watcher_state
    _config = config
    _cache = cache
    _load_links = load_links
    _load_toml_file = load_toml_file
    _file_watcher_state = file_watcher_state


@editing_bp.route("/api/config")
def get_config_data():
    """Get current links configuration.

    On first access, copies base to override if override doesn't exist.
    This allows editing without modifying the base file.
    """
    assert _config is not None
    assert _load_toml_file is not None
    assert _load_links is not None

    if not _config.ENABLE_EDITING:
        return jsonify({"error": "Editing not enabled"}), 404

    # Copy base to override if override doesn't exist
    if not _config.CONFIG_OVERRIDE_FILE.exists():
        import tomli_w  # pylint: disable=import-outside-toplevel

        base_data = _load_toml_file(_config.CONFIG_FILE, {})
        if base_data:
            try:
                with open(_config.CONFIG_OVERRIDE_FILE, "wb") as f:
                    tomli_w.dump(base_data, f)

                logger.info("Created override file from base configuration")

                # Invalidate cache
                if _cache:
                    _cache.clear()
            except (OSError, ValueError) as e:
                logger.error("Failed to create override file: %s", e)
                return jsonify({"error": "Failed to initialize override file"}), 500

    categories = _load_links()

    # Load widget order from config if exists
    config_data = _load_toml_file(_config.CONFIG_OVERRIDE_FILE, {})
    if not config_data:
        config_data = _load_toml_file(_config.CONFIG_FILE, {})

    widget_order = config_data.get("widget_order", [])

    return jsonify({"category": categories, "widget_order": widget_order})


@editing_bp.route("/api/config", methods=["POST"])
def save_config_data():
    """Save links configuration to override file."""
    assert _config is not None
    assert _file_watcher_state is not None

    if not _config.ENABLE_EDITING:
        return jsonify({"error": "Editing not enabled"}), 404

    try:
        import tomli_w  # pylint: disable=import-outside-toplevel

        data = request.get_json()
        if not data or "category" not in data:
            return jsonify({"error": "Invalid configuration data"}), 400

        # Validate the configuration
        from ..utils import validate_links_config  # pylint: disable=import-outside-toplevel

        valid, errors = validate_links_config(data)
        if not valid:
            return jsonify({"error": "Invalid configuration", "details": errors}), 400

        # Extract widget_order if present (optional field)
        widget_order = data.pop("widget_order", [])

        # Prepare final config with widget_order at top level
        final_config = data.copy()
        if widget_order:
            final_config["widget_order"] = widget_order

        # Write to override file using tomli_w
        with open(_config.CONFIG_OVERRIDE_FILE, "wb") as f:
            tomli_w.dump(final_config, f)
            f.flush()  # Ensure data is written to disk
            os.fsync(f.fileno())  # Force OS to write to disk

        # Invalidate cache
        if _cache:
            _cache.clear()

        # Set reload flag for file watcher
        _file_watcher_state["reload_needed"] = True

        logger.info("Configuration saved to override file")
        return jsonify({"status": "ok"})

    except (ValueError, TypeError, OSError) as e:
        logger.error("Error saving configuration: %s", e)
        return jsonify({"error": "Failed to save configuration"}), 500


@editing_bp.route("/api/config/reset", methods=["POST"])
def reset_config():
    """Reset configuration by removing override file."""
    assert _config is not None

    if not _config.ENABLE_EDITING:
        return jsonify({"error": "Editing not enabled"}), 404

    try:
        if _config.CONFIG_OVERRIDE_FILE.exists():
            _config.CONFIG_OVERRIDE_FILE.unlink()
            logger.info("Override configuration deleted")

        # Invalidate cache
        if _cache:
            _cache.clear()

        return jsonify({"status": "ok"})

    except OSError as e:
        logger.error("Error deleting override file: %s", e)
        return jsonify({"error": "Failed to reset configuration"}), 500


@editing_bp.route("/api/favicon")
def get_favicon_proxy():
    """Proxy favicon requests to avoid CORS issues.

    Attempts to extract favicon directly from the page, falls back to Google's service.
    Caches results to avoid repeated requests.
    """
    from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter required"}), 400

    try:
        # Check cache first
        cache_key = f"favicon:{url}"
        if _cache and (cached_favicon := _cache.get(cache_key)):
            return jsonify({"favicon": cached_favicon, "cached": True})

        # Extract domain for fallback
        parsed = urlparse(url)
        domain = parsed.hostname or parsed.path

        # Import favicon utilities
        from ..utils import (  # pylint: disable=import-outside-toplevel
            extract_favicon_from_page,
            fetch_favicon_google,
        )

        # Try direct extraction first
        favicon_data = extract_favicon_from_page(url, timeout=5)

        # Fallback to Google's favicon service
        if not favicon_data:
            favicon_data = fetch_favicon_google(domain)

        # Cache for 1 hour (3600 seconds)
        if _cache and favicon_data:
            _cache.set(cache_key, favicon_data, ttl=3600)

        return jsonify({"favicon": favicon_data or "", "cached": False})

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Favicon fetch error for %s: %s", url, e)
        return jsonify({"error": "Failed to fetch favicon"}), 500
