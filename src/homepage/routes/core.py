"""Core routes (/, /health, /check_reload)."""

import logging

from flask import Blueprint, jsonify, make_response, render_template

# Import will be done dynamically to avoid circular imports
# These will be injected when the blueprint is registered

logger = logging.getLogger(__name__)

core_bp = Blueprint("core", __name__)


# These will be set when blueprint is registered with app
_load_colors = None
_load_wallpaper = None
_load_links = None
_file_watcher_state = None
_config = None


def init_core_blueprint(load_colors, load_wallpaper, load_links, file_watcher_state, config):
    """Initialize the core blueprint with dependencies."""
    global _load_colors, _load_wallpaper, _load_links, _file_watcher_state, _config
    _load_colors = load_colors
    _load_wallpaper = load_wallpaper
    _load_links = load_links
    _file_watcher_state = file_watcher_state
    _config = config


@core_bp.route("/")
def index():
    """Render the homepage."""
    colors = _load_colors()
    wallpaper = _load_wallpaper()
    categories = _load_links()

    response = make_response(
        render_template(
            "index.html.j2",
            colors=colors,
            wallpaper=wallpaper,
            categories=categories,
            clock_format=_config.CLOCK_FORMAT,
            reload_interval=_config.RELOAD_CHECK_INTERVAL,
            config=_config,
        )
    )

    # Prevent caching when editing is enabled
    if _config.ENABLE_EDITING:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


@core_bp.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": "homepage",
        }
    )


@core_bp.route("/check_reload")
def check_reload():
    """Check if a reload is needed due to file changes."""
    reload = _file_watcher_state["reload_needed"]
    if reload:
        _file_watcher_state["reload_needed"] = False
    return jsonify({"reload": reload})
