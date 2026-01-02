"""Core routes (/, /health, /check_reload)."""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from flask import Blueprint, jsonify, make_response, render_template, send_from_directory

if TYPE_CHECKING:
    from ..config import Config

# Import will be done dynamically to avoid circular imports
# These will be injected when the blueprint is registered

logger = logging.getLogger(__name__)

core_bp = Blueprint("core", __name__)


# These will be set when blueprint is registered with app
_load_colors: Callable[[], dict[str, str]] | None = None
_load_wallpaper: Callable[[], str] | None = None
_load_links: Callable[[], list[dict[str, Any]]] | None = None
_file_watcher_state: dict[str, Any] | None = None
_config: Optional["Config"] = None


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
    assert _load_colors is not None
    assert _load_wallpaper is not None
    assert _load_links is not None
    assert _config is not None

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
    assert _file_watcher_state is not None

    reload = _file_watcher_state["reload_needed"]
    if reload:
        _file_watcher_state["reload_needed"] = False
    return jsonify({"reload": reload})


@core_bp.route("/docs")
@core_bp.route("/docs/")
def docs_redirect():
    """Redirect to documentation."""
    # Check if docs are built
    docs_path = Path(__file__).parent.parent.parent.parent / "site"
    if docs_path.exists():
        # Read the index.html and inject base href
        index_file = docs_path / "index.html"
        if index_file.exists():
            with open(index_file) as f:
                html = f.read()
            # Inject base href if not already present
            if "<base href=" not in html:
                html = html.replace("<head>", '<head>\n    <base href="/docs/">')
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return send_from_directory(docs_path, "index.html")
    # Fallback to basic docs page
    return jsonify({"error": "Documentation not built. Run 'mkdocs build' to generate."}), 404


@core_bp.route("/docs/<path:filename>")
def serve_docs(filename: str):
    """Serve documentation files."""
    docs_path = Path(__file__).parent.parent.parent.parent / "site"
    if not docs_path.exists():
        return jsonify({"error": "Documentation not built"}), 404

    # For HTML files, inject base href
    if filename.endswith(".html"):
        file_path = docs_path / filename
        if file_path.exists() and file_path.is_file():
            with open(file_path) as f:
                html = f.read()
            # Inject base href if not already present
            if "<base href=" not in html:
                html = html.replace("<head>", '<head>\n    <base href="/docs/">')
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}

    return send_from_directory(docs_path, filename)
