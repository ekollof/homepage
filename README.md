# Homepage

A customizable homepage web server that displays links from a TOML configuration file with dynamic theming support from pywal.

## Features

- 🎨 **Dynamic Theming**: Automatically uses colors from `~/.cache/wal/colors.json` with Gruvbox dark as fallback
- 🖼️ **Custom Background**: Displays wallpaper from `~/.wallpaper` file (served via HTTP)
- 🔄 **Auto-Reload**: Page automatically reloads when colors or wallpaper changes
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⏰ **Digital Clock**: 24-hour format clock with current date
- 🔍 **Web Search**: Integrated search bar with multiple providers (Brave, Google, DuckDuckGo, Bing)
- 🔗 **Hierarchical Links**: Organize links in categories and subcategories
- 🎯 **Icon Support**: Use emojis or other icons for visual organization
- ✏️ **In-Browser Editing**: Add, edit, and delete links directly from the web interface
- ⚡ **Lightweight**: Inline CSS and JavaScript for simplicity

## Documentation

📚 **[Full Documentation Index](docs/README.md)** - Complete documentation navigation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Features](docs/FEATURES.md)** - Comprehensive feature documentation
- **[Usage Guide](docs/USAGE.md)** - Complete usage instructions
- **[Technical Notes](docs/TECHNICAL.md)** - Implementation details for developers
- **[Changelog](docs/CHANGELOG.md)** - Version history and updates

## Requirements

- Python 3.10 or higher
- pip

## Installation

### Quick Install (Recommended)

Use the installation script for automated setup:

```bash
cd ~/Code/homepage
./install.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up the systemd service
- Display next steps

### Manual Installation

1. Navigate to the project directory:
```bash
cd ~/Code/homepage
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Install the package:
```bash
./venv/bin/pip install -e .
```

4. Install with development tools (optional):
```bash
./venv/bin/pip install -e ".[dev]"
```

## Configuration

### Links Configuration

Edit `links.toml` to customize your links. The structure supports:

- **Categories**: Top-level groups with name and icon
- **Links**: Direct links within categories
- **Subcategories**: Nested groups within categories

Example:
```toml
[[category]]
name = "Development"
icon = "💻"

  [[category.links]]
  name = "GitHub"
  url = "https://github.com"
  icon = "🔗"

  [[category.subcategory]]
  name = "Documentation"
  icon = "📚"

    [[category.subcategory.links]]
    name = "Python Docs"
    url = "https://docs.python.org"
    icon = "🐍"
```

### Color Scheme

The application automatically reads colors from `~/.cache/wal/colors.json` if available. If not found, it falls back to Gruvbox dark theme.

To use pywal colors, ensure you have pywal installed and configured:
```bash
wal -i /path/to/wallpaper.jpg
```

### Background Image

Create a `~/.wallpaper` file containing the path to your wallpaper:
```bash
echo "/path/to/your/wallpaper.jpg" > ~/.wallpaper
```

The wallpaper is served through Flask at the `/wallpaper` endpoint to avoid browser CORS restrictions with local `file://` URLs.

### In-Browser Link Editing

The application includes a built-in link editor that allows you to manage your links directly from the web interface.

#### Enabling Edit Mode

Edit mode is enabled by default. To disable it, set the environment variable:
```bash
export HOMEPAGE_ENABLE_EDITING=False
```

Or add to your `.env` file:
```
HOMEPAGE_ENABLE_EDITING=False
```

#### Using the Editor

1. **Open Edit Mode**: Click the edit button (pencil icon) in the top-right corner, or press the `e` key
2. **Add Items**: 
   - Click "Add Category" to create a new top-level category
   - Click "Add Link" within a category to add a direct link
   - Click "Add Subcategory" to create a nested group with its own links
3. **Edit Items**: Click the edit icon (✏️) next to any item to modify its properties
4. **Delete Items**: Click the delete icon (🗑️) to remove items (with confirmation)
5. **Reorder Items**: Use the up/down arrows to change the order of items
6. **Save Changes**: Changes are automatically saved to `links.override.toml`

#### Configuration Override System

The editor uses a simple two-file system:
- `links.toml` - Base configuration (tracked in git)
- `links.override.toml` - Your customized version (gitignored, auto-created on first edit)

**Important notes:**
- Once you make your first edit, a `links.override.toml` file is created
- The override file completely replaces the base configuration when it exists
- To reset to the base configuration, simply delete `links.override.toml`
- The base file remains untouched, so you never lose the default configuration

## Usage

### Running Manually

Start the server using the virtual environment:
```bash
./venv/bin/python app.py
```

Then open your browser to: http://localhost:5000

### Running as Systemd Service

If you used `./install.sh`, the service is already installed. Otherwise:

1. Copy the service file to systemd user directory:
```bash
mkdir -p ~/.config/systemd/user
cp homepage.service ~/.config/systemd/user/
```

2. Reload systemd:
```bash
systemctl --user daemon-reload
```

3. Start the service:
```bash
systemctl --user start homepage.service
```

4. Enable auto-start on login:
```bash
systemctl --user enable homepage.service
```

5. Check service status:
```bash
systemctl --user status homepage.service
```

6. View logs:
```bash
journalctl --user -u homepage.service -f
```

### Managing the Service

```bash
# Stop the service
systemctl --user stop homepage.service

# Restart the service
systemctl --user restart homepage.service

# Disable auto-start
systemctl --user disable homepage.service
```

## Development

### Using Make

The project includes a Makefile for common development tasks:

```bash
# Show all available commands
make help

# Install dependencies
make install

# Install with development tools
make install-dev

# Run the application
make run

# Format and check code
make check

# Format code only
make format

# Run linters only
make lint

# Clean up virtual environment
make clean
```

### Systemd Service Management

```bash
# Install service
make service-install

# Start/stop/restart service
make service-start
make service-stop
make service-restart

# Check service status
make service-status

# Enable/disable auto-start
make service-enable
make service-disable

# View logs
make logs
```

### Code Quality Tools

The project uses modern Python development tools for code quality:

```bash
# Format code with black
black app.py

# Lint with ruff
ruff check app.py

# Lint with pylint
pylint app.py

# Type check with pyright
pyright app.py
```

### Run all checks

Using Make (recommended):
```bash
make check
```

Or manually:
```bash
./venv/bin/black app.py && ./venv/bin/ruff check app.py && ./venv/bin/pylint app.py && ./venv/bin/pyright app.py
```

## Project Structure

```
homepage/
├── app.py                  # Main Flask application
├── links.toml              # Links configuration (example included)
├── homepage.service        # Systemd service file
├── install.sh              # Installation script
├── Makefile                # Development task automation
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # Full documentation
└── docs/                   # Documentation
    ├── QUICKSTART.md       # Quick start guide
    ├── FEATURES.md         # Feature documentation
    ├── TECHNICAL.md        # Technical implementation details
    ├── USAGE.md            # Usage guide
    └── CHANGELOG.md        # Version history
```

## Customization

### Changing Port

Edit `app.py` and modify the port in the last line:
```python
app.run(host="127.0.0.1", port=5000, debug=False)
```

### Styling

All CSS is inline in `app.py`. Edit the `<style>` section in the template to customize:
- Colors
- Layout
- Font sizes
- Responsive breakpoints

### Clock Format

The clock uses 24-hour format by default. To change to 12-hour format, modify the JavaScript in the template:
```javascript
const hours = String(now.getHours() % 12 || 12).padStart(2, '0');
// Add AM/PM indicator as needed
```

### Search Providers

The search bar supports multiple search engines. To change the default or add new providers, modify the JavaScript in the template:

```javascript
const searchUrls = {
    'brave': 'https://search.brave.com/search?q=',
    'google': 'https://www.google.com/search?q=',
    'duckduckgo': 'https://duckduckgo.com/?q=',
    'bing': 'https://www.bing.com/search?q='
};
```

To change the default provider, modify the `<option>` order in the HTML, placing your preferred provider first.

## Troubleshooting

### Service Won't Start

Check logs:
```bash
journalctl --user -u homepage.service -n 50
```

Verify the working directory in the service file matches your installation path.

### Colors Not Loading

Ensure `~/.cache/wal/colors.json` exists and is valid JSON. The application will fall back to Gruvbox dark if the file is missing or invalid.

### Wallpaper Not Showing

- Verify `~/.wallpaper` contains a valid path
- Ensure the wallpaper file exists and is readable
- Check that the Flask server is running (wallpaper is served via HTTP at `/wallpaper`)
- View browser console for any loading errors

### Auto-Reload Not Working

The auto-reload feature watches the directories containing:
- `~/.cache/wal/colors.json`
- `~/.wallpaper`
- `links.toml` and `links.override.toml`

Ensure these directories exist and are accessible.

### Edit Mode Not Available

If the edit button doesn't appear:
- Check that `HOMEPAGE_ENABLE_EDITING` is set to `True` (default)
- If running in production mode, ensure the environment variable is set
- Clear your browser cache and reload the page

### Changes Not Saving

If edits don't persist:
- Check that the application has write permissions to the installation directory
- Verify that `links.override.toml` was created in the same directory as `links.toml`
- Check the application logs for any errors: `journalctl --user -u homepage.service -n 50`

## License

This project is provided as-is for personal use.