# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of Homepage web server application
- Flask-based web server running on localhost:5000
- TOML-based link configuration with hierarchical structure
- Support for categories, subcategories, and links
- Icon support using emojis or Unicode characters
- Digital clock with 24-hour format, updating every second
- Current date display below clock in full format
- Integrated web search bar with multiple providers (Brave, Google, DuckDuckGo, Bing)
- Search provider selector with Brave Search as default
- Search results open in new tabs with proper security attributes
- Dynamic theming from pywal colors (~/.cache/wal/colors.json)
- Gruvbox dark theme as fallback when pywal is unavailable
- Custom wallpaper background from ~/.wallpaper file
- Auto-reload functionality when colors.json or wallpaper changes
- File system watching using watchdog library
- Responsive design for desktop, tablet, and mobile devices
- Grid layout with auto-fitting columns
- Inline CSS and JavaScript for simplicity
- Semi-transparent overlay for better readability
- Hover effects and smooth transitions
- systemd user service integration
- Virtual environment support
- Installation script (install.sh)
- Makefile for development tasks
- Comprehensive documentation (README.md, QUICKSTART.md, FEATURES.md)
- HTTP endpoint for serving wallpaper images (avoids browser CORS restrictions)
- Automatic fallback to transparent PNG when wallpaper is unavailable
- Code quality tools configuration (black, ruff, pylint, pyright)
- .gitignore for Python projects
- requirements.txt for production dependencies
- requirements-dev.txt for development dependencies
- pyproject.toml with modern Python packaging configuration
- Example links.toml with sample categories and links
- 10/10 pylint score
- Full type hint coverage with pyright
- Python 3.10+ compatibility with PEP standard compliance

### Security
- Localhost-only binding (127.0.0.1)
- External links open in new tabs with rel="noopener noreferrer"
- Virtual environment for dependency isolation
- No remote code execution capabilities
- CORS-compliant wallpaper serving (no file:// URLs)

### Performance
- Single-page application with minimal HTTP requests
- Inline CSS and JavaScript (no external asset loading)
- Event-based file watching (not polling)
- Efficient template rendering with Jinja2
- Low memory and CPU usage
- Client-side search processing (no server overhead)

### Documentation
- Complete README with installation and usage instructions
- Quick start guide for fast setup
- Comprehensive feature documentation
- Inline code documentation with docstrings
- Makefile help system
- systemd service management guide
- Troubleshooting section
- Customization examples

[0.1.0]: https://github.com/yourusername/homepage/releases/tag/v0.1.0