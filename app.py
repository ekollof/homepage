"""Flask application for customizable homepage with dynamic theming."""

import base64
import json
import sys
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, render_template_string, send_file
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

app = Flask(__name__)

# Configuration
CONFIG_FILE = Path("links.toml")
COLORS_FILE = Path.home() / ".cache" / "wal" / "colors.json"
WALLPAPER_FILE = Path.home() / ".wallpaper"

# Gruvbox dark theme fallback colors
GRUVBOX_DARK = {
    "background": "#282828",
    "foreground": "#ebdbb2",
    "color0": "#282828",
    "color1": "#cc241d",
    "color2": "#98971a",
    "color3": "#d79921",
    "color4": "#458588",
    "color5": "#b16286",
    "color6": "#689d6a",
    "color7": "#a89984",
    "color8": "#928374",
    "color9": "#fb4934",
    "color10": "#b8bb26",
    "color11": "#fabd2f",
    "color12": "#83a598",
    "color13": "#d3869b",
    "color14": "#8ec07c",
    "color15": "#ebdbb2",
}

# Global state for file modification tracking
file_watcher_state = {"reload_needed": False}


class ConfigFileHandler(FileSystemEventHandler):
    """Handler for file system events on config files."""

    def on_modified(self, event):
        """Mark that a reload is needed when files are modified."""
        if not event.is_directory:
            file_path = Path(str(event.src_path))
            if file_path.name in ("colors.json", ".wallpaper"):
                file_watcher_state["reload_needed"] = True


def load_colors():
    """Load colors from pywal cache or use gruvbox dark fallback."""
    if COLORS_FILE.exists():
        try:
            with open(COLORS_FILE, encoding="utf-8") as f:
                data = json.load(f)
                colors = data.get("colors", {})
                colors["background"] = data.get("special", {}).get(
                    "background", colors.get("color0", GRUVBOX_DARK["background"])
                )
                colors["foreground"] = data.get("special", {}).get(
                    "foreground", colors.get("color7", GRUVBOX_DARK["foreground"])
                )
                return colors
        except (json.JSONDecodeError, KeyError):
            pass
    return GRUVBOX_DARK


def load_wallpaper():
    """Load wallpaper path or return None."""
    if WALLPAPER_FILE.exists():
        try:
            with open(WALLPAPER_FILE, encoding="utf-8") as f:
                wallpaper_path = f.read().strip()
                if wallpaper_path and Path(wallpaper_path).exists():
                    return wallpaper_path
        except OSError:
            pass
    return None


def load_links():
    """Load links from TOML configuration file."""
    if not CONFIG_FILE.exists():
        return []

    try:
        with open(CONFIG_FILE, "rb") as f:
            data = tomllib.load(f)
            return data.get("category", [])
    except (tomllib.TOMLDecodeError, OSError):
        return []


@app.route("/")
def index():
    """Render the homepage."""
    colors = load_colors()
    wallpaper = load_wallpaper()
    categories = load_links()

    # HTML template with inline CSS and JavaScript
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homepage</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: {{ colors.foreground }};
            background-color: {{ colors.background }};
            {% if wallpaper %}
            background-image: url('/wallpaper');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            {% else %}
            background-color: #000000;
            {% endif %}
            min-height: 100vh;
            overflow-y: auto;
        }

        .overlay {
            background-color: rgba(0, 0, 0, 0.7);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .clock {
            font-size: 3rem;
            font-weight: bold;
            color: {{ colors.color12 }};
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }

        .date {
            font-size: 1.2rem;
            color: {{ colors.color14 }};
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            margin-bottom: 20px;
        }

        .search-container {
            max-width: 600px;
            margin: 0 auto;
        }

        .search-form {
            display: flex;
            gap: 10px;
            align-items: stretch;
        }

        .search-provider {
            background-color: rgba(40, 40, 40, 0.9);
            color: {{ colors.foreground }};
            border: 2px solid {{ colors.color8 }};
            border-radius: 5px;
            padding: 12px 15px;
            font-size: 1rem;
            cursor: pointer;
            transition: border-color 0.2s, background-color 0.2s;
            min-width: 140px;
        }

        .search-provider:hover {
            border-color: {{ colors.color12 }};
            background-color: rgba(60, 60, 60, 0.9);
        }

        .search-provider:focus {
            outline: none;
            border-color: {{ colors.color11 }};
        }

        .search-input {
            flex: 1;
            background-color: rgba(40, 40, 40, 0.9);
            color: {{ colors.foreground }};
            border: 2px solid {{ colors.color8 }};
            border-radius: 5px;
            padding: 12px 15px;
            font-size: 1rem;
            transition: border-color 0.2s, background-color 0.2s;
        }

        .search-input:hover {
            border-color: {{ colors.color12 }};
            background-color: rgba(60, 60, 60, 0.9);
        }

        .search-input:focus {
            outline: none;
            border-color: {{ colors.color11 }};
            background-color: rgba(50, 50, 50, 0.9);
        }

        .search-input::placeholder {
            color: {{ colors.color8 }};
        }

        .links-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            width: 90%;
            margin: 0 auto;
        }

        .category {
            background-color: rgba(40, 40, 40, 0.9);
            border: 2px solid {{ colors.color8 }};
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .category:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
            border-color: {{ colors.color12 }};
        }

        .category-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: {{ colors.color11 }};
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .category-icon {
            font-size: 1.8rem;
        }

        .links-list {
            list-style: none;
            margin-bottom: 15px;
        }

        .link-item {
            margin-bottom: 8px;
        }

        .link-item a {
            color: {{ colors.color14 }};
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 5px;
            transition: background-color 0.2s, color 0.2s;
        }

        .link-item a:hover {
            background-color: {{ colors.color8 }};
            color: {{ colors.color10 }};
        }

        .link-icon {
            font-size: 1.1rem;
        }

        .subcategory {
            margin-top: 15px;
            margin-left: 10px;
            padding-left: 15px;
            border-left: 2px solid {{ colors.color8 }};
        }

        .subcategory-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: {{ colors.color9 }};
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .subcategory-icon {
            font-size: 1.3rem;
        }

        @media (max-width: 768px) {
            .clock {
                font-size: 2rem;
            }

            .date {
                font-size: 1rem;
            }

            .search-container {
                max-width: 90%;
            }

            .search-form {
                flex-direction: column;
            }

            .search-provider {
                min-width: unset;
            }

            .links-container {
                grid-template-columns: 1fr;
                width: 95%;
            }

            .category-title {
                font-size: 1.3rem;
            }

            .subcategory-title {
                font-size: 1.1rem;
            }
        }

        @media (max-width: 480px) {
            .clock {
                font-size: 1.5rem;
            }

            .container {
                padding: 10px;
            }

            .category {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="overlay">
        <div class="container">
            <div class="header">
                <div class="clock" id="clock">00:00:00</div>
                <div class="date" id="date">Loading...</div>

                <div class="search-container">
                    <form class="search-form" onsubmit="handleSearch(event)">
                        <select class="search-provider" id="searchProvider">
                            <option value="brave">Brave Search</option>
                            <option value="google">Google</option>
                            <option value="duckduckgo">DuckDuckGo</option>
                            <option value="bing">Bing</option>
                        </select>
                        <input
                            type="text"
                            class="search-input"
                            id="searchInput"
                            placeholder="Search the web..."
                            autocomplete="off"
                        />
                    </form>
                </div>
            </div>

            <div class="links-container">
                {% for category in categories %}
                <div class="category">
                    <div class="category-title">
                        <span class="category-icon">{{ category.icon }}</span>
                        <span>{{ category.name }}</span>
                    </div>

                    {% if category.links %}
                    <ul class="links-list">
                        {% for link in category.links %}
                        <li class="link-item">
                            <a href="{{ link.url }}" target="_blank" rel="noopener noreferrer">
                                <span class="link-icon">{{ link.icon }}</span>
                                <span>{{ link.name }}</span>
                            </a>
                        </li>
                        {% endfor %}
                    </ul>
                    {% endif %}

                    {% if category.subcategory %}
                    {% for subcategory in category.subcategory %}
                    <div class="subcategory">
                        <div class="subcategory-title">
                            <span class="subcategory-icon">{{ subcategory.icon }}</span>
                            <span>{{ subcategory.name }}</span>
                        </div>
                        {% if subcategory.links %}
                        <ul class="links-list">
                            {% for link in subcategory.links %}
                            <li class="link-item">
                                <a href="{{ link.url }}" target="_blank" rel="noopener noreferrer">
                                    <span class="link-icon">{{ link.icon }}</span>
                                    <span>{{ link.name }}</span>
                                </a>
                            </li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                    {% endfor %}
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;
        }

        function updateDate() {
            const now = new Date();
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const dateString = now.toLocaleDateString('en-US', options);
            document.getElementById('date').textContent = dateString;
        }

        function checkForReload() {
            fetch('/check_reload')
                .then(response => response.json())
                .then(data => {
                    if (data.reload) {
                        window.location.reload();
                    }
                })
                .catch(error => console.error('Error checking for reload:', error));
        }

        function handleSearch(event) {
            event.preventDefault();

            const searchInput = document.getElementById('searchInput');
            const searchProvider = document.getElementById('searchProvider');
            const query = searchInput.value.trim();

            if (!query) {
                return;
            }

            const searchUrls = {
                'brave': 'https://search.brave.com/search?q=',
                'google': 'https://www.google.com/search?q=',
                'duckduckgo': 'https://duckduckgo.com/?q=',
                'bing': 'https://www.bing.com/search?q='
            };

            const baseUrl = searchUrls[searchProvider.value] || searchUrls['brave'];
            const searchUrl = baseUrl + encodeURIComponent(query);

            window.open(searchUrl, '_blank', 'noopener,noreferrer');
            searchInput.value = '';
        }

        // Update clock every second
        updateClock();
        updateDate();
        setInterval(updateClock, 1000);

        // Update date at midnight
        setInterval(updateDate, 60000);

        // Check for file changes every 2 seconds
        setInterval(checkForReload, 2000);
    </script>
</body>
</html>
"""

    return render_template_string(
        template, colors=colors, wallpaper=wallpaper, categories=categories
    )


@app.route("/check_reload")
def check_reload():
    """Check if a reload is needed due to file changes."""
    reload = file_watcher_state["reload_needed"]
    if reload:
        file_watcher_state["reload_needed"] = False
    return jsonify({"reload": reload})


@app.route("/wallpaper")
def serve_wallpaper():
    """Serve the wallpaper image."""
    wallpaper_path = load_wallpaper()
    if wallpaper_path:
        try:
            return send_file(wallpaper_path)
        except (OSError, FileNotFoundError):
            pass
    # Return a 1x1 transparent PNG if no wallpaper
    transparent_png = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
        b"AAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    return send_file(BytesIO(transparent_png), mimetype="image/png")


def start_file_watcher():
    """Start watching configuration files for changes."""
    file_observer = Observer()
    handler = ConfigFileHandler()

    # Watch colors.json directory
    colors_dir = COLORS_FILE.parent
    if colors_dir.exists():
        file_observer.schedule(handler, str(colors_dir), recursive=False)

    # Watch wallpaper file directory
    wallpaper_dir = WALLPAPER_FILE.parent
    if wallpaper_dir.exists():
        file_observer.schedule(handler, str(wallpaper_dir), recursive=False)

    file_observer.start()
    return file_observer


if __name__ == "__main__":
    observer = start_file_watcher()
    try:
        app.run(host="127.0.0.1", port=5000, debug=False)
    finally:
        observer.stop()
        observer.join()
