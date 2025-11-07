# Features

This document provides a comprehensive overview of all features included in the Homepage application.

## Core Features

### Web Server
- **Flask-based**: Lightweight and reliable Python web framework
- **Localhost only**: Runs on `127.0.0.1:5000` for security
- **Single page application**: Fast loading, no page navigation needed
- **Auto-reload detection**: Monitors configuration files for changes

### Link Management
- **Hierarchical organization**: Support for categories, subcategories, and links
- **TOML configuration**: Easy-to-edit, human-readable format
- **Icon support**: Use emojis or other Unicode characters for visual identification
- **Unlimited nesting**: Categories can contain both direct links and subcategories
- **External link support**: All links open in new tabs with security attributes

### Digital Clock
- **Real-time updates**: Updates every second
- **24-hour format**: Military time display (HH:MM:SS)
- **Zero-padded**: Consistent formatting (e.g., 09:05:03)
- **Date display**: Full date with weekday, month, day, and year
- **Automatic date refresh**: Updates at midnight

### Web Search
- **Integrated search bar**: Quick access below clock and date
- **Multiple providers**: Brave Search, Google, DuckDuckGo, Bing
- **Default provider**: Brave Search (configurable)
- **Dropdown selector**: Easy switching between search engines
- **New tab results**: Searches open in new tab
- **Keyboard friendly**: Press Enter to search
- **Auto-clear**: Input clears after search
- **URL encoding**: Properly handles special characters in queries

### RSS Feed Carousel
- **Auto-rotating carousel**: Displays one RSS item at a time
- **30-second rotation**: Automatically cycles through feed items
- **Manual navigation**: Previous and next buttons (‹ and ›)
- **Item counter**: Shows current position and total count
- **Terminal styling**: Compact, monospace design for clean aesthetics
- **Multiple feeds**: Supports multiple RSS feeds (pipe-separated)
- **Smart caching**: Configurable cache TTL (default 5 minutes)
- **Feed attribution**: Shows source feed name and publication date
- **Description preview**: Displays article summary when available
- **External links**: Opens articles in new tabs
- **Auto-reset timer**: Manual navigation resets the 30-second auto-rotation
- **Configurable items**: Set max items per feed (default 5)
- **Error handling**: Graceful fallback when feeds are unavailable

## Theming & Appearance

### Dynamic Color Scheme
- **Pywal integration**: Automatically reads `~/.cache/wal/colors.json`
- **Gruvbox fallback**: Beautiful dark theme when pywal is unavailable
- **16-color palette**: Full color support from pywal
- **Dynamic foreground/background**: Adapts to your system theme

### Background Management
- **Custom wallpaper**: Reads from `~/.wallpaper` file
- **HTTP serving**: Wallpaper served via `/wallpaper` endpoint (avoids CORS issues)
- **Automatic fallback**: Pure black background if no wallpaper specified
- **Cover mode**: Wallpaper scales to cover entire viewport
- **Fixed attachment**: Background stays in place while scrolling

### Visual Design
- **Semi-transparent overlay**: Dark overlay on wallpaper for readability
- **Rounded corners**: Modern card-based design
- **Hover effects**: Interactive feedback on categories and links
- **Shadow effects**: Depth and visual hierarchy
- **Color-coded elements**: Categories, subcategories, and links use distinct colors
- **Smooth transitions**: Animated hover states and transformations

## Responsive Design

### Desktop Support
- **Grid layout**: Auto-fitting columns based on viewport width
- **Maximum width**: 1400px container for optimal reading
- **Large typography**: Clear, readable text sizes
- **Spacious padding**: Comfortable spacing between elements

### Mobile Support
- **Single column**: Stacks on narrow screens
- **Touch-friendly**: Large tap targets for links
- **Scaled typography**: Appropriate text sizes for mobile
- **Optimized spacing**: Reduced padding on small screens
- **Viewport meta tag**: Proper scaling on mobile devices

### Breakpoints
- **Desktop**: Default grid layout (>768px)
- **Tablet**: Single column with adjusted sizing (480-768px)
- **Mobile**: Compact layout with minimal padding (<480px)

## File Watching

### Auto-Reload System
- **Watchdog integration**: Monitors file system events
- **Colors monitoring**: Detects changes to `~/.cache/wal/colors.json`
- **Wallpaper monitoring**: Detects changes to `~/.wallpaper`
- **Client-side polling**: JavaScript checks for updates every 2 seconds
- **Automatic refresh**: Page reloads when changes detected
- **No manual restart**: Changes apply immediately

## System Integration

### Systemd Service
- **User service**: Runs under your user account
- **Auto-restart**: Automatically recovers from crashes
- **Boot integration**: Optional auto-start on login
- **Journal logging**: Standard systemd logging
- **Easy management**: Standard systemctl commands

### Environment Support
- **Virtual environment**: Isolated Python dependencies
- **Python 3.10+**: Modern Python features and performance
- **Cross-version compatible**: Works with Python 3.10, 3.11, 3.12+
- **TOML library handling**: Automatic selection of tomllib or tomli

## Configuration

### Flexible Link Structure
```toml
[[category]]
name = "Category Name"
icon = "🔗"

  [[category.links]]
  name = "Link Name"
  url = "https://example.com"
  icon = "🌐"

  [[category.subcategory]]
  name = "Subcategory Name"
  icon = "📁"
```

### Color Scheme Support
- **JSON format**: Compatible with pywal output
- **Fallback colors**: Gruvbox dark theme built-in
- **Special colors**: Background and foreground support
- **16-color palette**: Full terminal color compatibility

## Developer Features

### Code Quality
- **Type hints**: Python type annotations throughout
- **Docstrings**: All functions documented
- **PEP 8 compliant**: Standard Python style
- **100% linting score**: Passes all quality checks

### Linting Tools
- **Black**: Code formatting (100 char line length)
- **Ruff**: Fast Python linter
- **Pylint**: Comprehensive code analysis (10/10 score)
- **Pyright**: Static type checking

### Project Structure
- **Modular design**: Clear separation of concerns
- **Configuration files**: Separate config from code
- **Documentation**: Comprehensive README and guides
- **Build system**: Modern pyproject.toml configuration

### Development Tools
- **Makefile**: Common tasks automated
- **Installation script**: One-command setup
- **Requirements files**: Separate prod and dev dependencies
- **Virtual environment**: Isolated dependencies

## Security Features

### Safe Defaults
- **Localhost binding**: Only accessible from your machine
- **New tab links**: All external links open in new tabs
- **rel attributes**: `noopener noreferrer` for security
- **No remote execution**: Static configuration only
- **Input validation**: Safe handling of file paths
- **CORS compliance**: Wallpaper served via HTTP (no file:// URLs)

### Dependency Management
- **Minimal dependencies**: Only 3 production dependencies
- **Well-maintained libraries**: Flask and Watchdog are industry standards
- **Version pinning**: Minimum versions specified
- **Virtual environment**: Isolated from system Python

## Performance

### Optimization
- **Inline assets**: CSS and JavaScript embedded (minimal external requests)
- **Efficient wallpaper serving**: Single HTTP endpoint for background image
- **Minimal JavaScript**: Only clock, reload checking, and search handling
- **Efficient file watching**: Event-based, not polling file system
- **No database**: Configuration in memory
- **Fast templating**: Jinja2 template engine
- **Client-side search**: No server processing for search queries

### Resource Usage
- **Low memory**: Minimal Flask overhead
- **Low CPU**: Efficient file watching
- **No background processes**: Clean systemd integration
- **Fast startup**: Immediate availability

## Accessibility

### Semantic HTML
- **Proper structure**: Header, container, sections
- **Form elements**: Semantic search form with proper labels
- **List elements**: Links organized in semantic lists
- **Language attribute**: Proper HTML lang tag
- **Viewport meta**: Mobile accessibility

### Visual Accessibility
- **High contrast**: Dark overlay on background
- **Large text**: Readable font sizes
- **Clear hierarchy**: Visual distinction between levels
- **Icon support**: Visual and text identification

## Extensibility

### Easy Customization
- **Inline CSS**: All styles in one place
- **Template variables**: Dynamic theming support
- **Configurable icons**: Any Unicode character
- **Flexible structure**: Unlimited categories and links
- **Search providers**: Easy to add or modify search engines
- **Default provider**: Configurable via HTML option order

### Future Enhancement Ready
- **Modular code**: Easy to extend functionality
- **Clear structure**: Well-organized codebase
- **Type hints**: Better IDE support for modifications
- **Documentation**: Comprehensive guides for customization

## Browser Compatibility

### Modern Browser Support
- **Chrome/Chromium**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile browsers**: Responsive design support

### Web Standards
- **HTML5**: Modern semantic markup
- **CSS3**: Grid, transitions, transforms
- **ES6 JavaScript**: Modern JavaScript features
- **Fetch API**: Standard AJAX requests

## Operational Features

### Logging
- **Systemd journal**: Standard logging integration
- **Error tracking**: Flask error handling
- **File watch events**: Debugging information
- **Service status**: systemctl status output

### Maintenance
- **Easy updates**: Pull and restart service
- **Configuration hot-reload**: No restart needed for theme changes
- **Clean uninstall**: Standard systemd service removal
- **Backup friendly**: All config in one directory

## Documentation

### Comprehensive Guides
- **README.md**: Full documentation
- **QUICKSTART.md**: Fast setup guide
- **FEATURES.md**: This feature list
- **Inline comments**: Code documentation

### Installation Options
- **Quick install**: `./install.sh` script
- **Manual install**: Step-by-step instructions
- **Make targets**: Automated common tasks
- **Service setup**: Systemd integration guide