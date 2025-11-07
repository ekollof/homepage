"""Static asset routes (CSS, JS, wallpaper, favicon)."""

import base64
import logging
from io import BytesIO

from flask import Blueprint, make_response, send_file

logger = logging.getLogger(__name__)

assets_bp = Blueprint("assets", __name__)

_config = None
_load_colors = None
_load_wallpaper = None
_render_template = None


def init_assets_blueprint(config, load_colors, load_wallpaper, render_template):
    """Initialize assets blueprint with dependencies."""
    global _config, _load_colors, _load_wallpaper, _render_template
    _config = config
    _load_colors = load_colors
    _load_wallpaper = load_wallpaper
    _render_template = render_template


@assets_bp.route("/styles.css")
def styles():
    """Generate and serve the CSS stylesheet."""
    colors = _load_colors()
    # Use modular CSS template that includes all CSS modules
    css_content = _render_template("styles-modular.css.j2", colors=colors)

    response = make_response(css_content)
    response.headers["Content-Type"] = "text/css"

    # Cache for 1 hour if not in edit mode
    if not _config.ENABLE_EDITING:
        response.headers["Cache-Control"] = "public, max-age=3600"
    else:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response


@assets_bp.route("/scripts.js")
def scripts():
    """Generate and serve the JavaScript file."""
    js_content = _render_template(
        "scripts.js.j2",
        enable_metrics=_config.ENABLE_METRICS,
        enable_weather=_config.ENABLE_WEATHER,
        enable_rss=_config.ENABLE_RSS,
        enable_system_stats=_config.ENABLE_SYSTEM_STATS,
        enable_editing=_config.ENABLE_EDITING,
        weather_cache_ttl=_config.WEATHER_CACHE_TTL,
        rss_cache_ttl=_config.RSS_CACHE_TTL,
        system_stats_update_interval=_config.SYSTEM_STATS_UPDATE_INTERVAL,
    )

    response = make_response(js_content)
    response.headers["Content-Type"] = "application/javascript"

    # Cache for 1 hour if not in edit mode
    if not _config.ENABLE_EDITING:
        response.headers["Cache-Control"] = "public, max-age=3600"
    else:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response


@assets_bp.route("/wallpaper")
def serve_wallpaper():
    """Serve the wallpaper image."""
    wallpaper_path = _load_wallpaper()
    if wallpaper_path:
        try:
            return send_file(wallpaper_path)
        except (OSError, FileNotFoundError):
            logger.warning("Wallpaper file not found: %s", wallpaper_path)
    # Return a 1x1 transparent PNG if no wallpaper
    transparent_png = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
        b"AAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    return send_file(BytesIO(transparent_png), mimetype="image/png")


@assets_bp.route("/favicon")
def favicon():
    """Serve favicon."""
    # Generate a simple favicon based on first color
    colors = _load_colors()
    color4 = colors.get("color4", "#458588")
    fg_color = colors.get("foreground", "#ebdbb2")
    # Create a 16x16 colored square as favicon
    favicon_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
        <rect width="16" height="16" fill="{color4}"/>
        <text x="8" y="12" font-size="10" text-anchor="middle" fill="{fg_color}">H</text>
    </svg>"""
    return favicon_svg, 200, {"Content-Type": "image/svg+xml"}
