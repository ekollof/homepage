# Project Structure

This document describes the organization of the Homepage project.

## Directory Layout

```
homepage/
├── src/homepage/          # Python source code (package)
│   ├── __init__.py       # Package initialization
│   ├── app.py            # Main Flask application
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── metrics.py        # Metrics collection
│   ├── utils.py          # Utility functions
│   ├── routes/           # Route blueprints (API, assets, etc.)
│   ├── services/         # Service layer (weather, RSS, etc.)
│   ├── templates/        # Jinja2 templates
│   │   ├── *.html.j2    # HTML templates
│   │   ├── *.js.j2      # JavaScript templates (generated)
│   │   ├── *.css.j2     # CSS templates (combined)
│   │   └── css/         # Modular CSS source files
│   └── static/           # Static assets
│       └── js/
│           ├── socket.io.min.js  # Socket.IO library
│           └── modules/  # Modular JavaScript source files
│
├── data/                  # Configuration and data files
│   ├── links.toml        # Link configuration (user-editable)
│   ├── links.override.toml  # Override configuration (gitignored)
│   ├── .env.example      # Environment variable template
│   └── *.mmdb            # GeoIP databases (gitignored)
│
├── docker/                # Docker configuration
│   ├── Dockerfile        # Container build instructions
│   └── docker-compose.yml # Docker Compose configuration
│
├── scripts/               # Installation and utility scripts
│   ├── install.sh        # Installation script
│   ├── setup_geoip.sh    # GeoIP database setup
│   └── homepage.service  # Systemd service template
│
├── docs/                  # Documentation
│   ├── QUICKSTART.md     # Quick start guide
│   ├── API.md            # API documentation
│   ├── DEPLOYMENT.md     # Deployment guide
│   ├── FEATURES.md       # Feature documentation
│   └── ...               # Other documentation
│
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py       # Pytest configuration
│   └── test_app.py       # Application tests
│
├── pyproject.toml         # Project metadata and dependencies
├── Makefile              # Development tasks
├── README.md             # Project README
├── CHANGELOG.md          # Version history
├── CONTRIBUTING.md       # Contribution guidelines
└── .gitignore            # Git ignore rules

## Installation

The project is now a proper Python package. Install from the project root:

### Production Installation
```bash
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

### Using the Install Script
```bash
./scripts/install.sh
```

### Using Make
```bash
make install          # Production
make install-dev      # Development
```

### Using pipx (Isolated Installation)
```bash
pipx install -e .
```

## Running the Application

After installation, you can run the application in several ways:

### Using the Installed Command
```bash
homepage  # Runs the web server
```

### Using Python Module
```bash
python -m homepage.app
```

### Using Make
```bash
make run
```

### Using Systemd Service
```bash
systemctl --user start homepage.service
```

## Configuration

Configuration files are now located in the `data/` directory:

- **data/links.toml** - Your link configuration
- **data/links.override.toml** - Local override (gitignored)
- **data/.env** - Environment variables (create from .env.example)

## Development

All source code is in `src/homepage/`. This follows modern Python packaging conventions:

- Source code is separate from tests and documentation
- Package is importable as `homepage`
- Easy to distribute and install
- Clean project root

### Running Tests
```bash
make test       # Run tests
make test-cov   # Run tests with coverage
```

### Code Quality
```bash
make format     # Format code with black
make lint       # Run linters
make check      # Format and lint
make build-js   # Build JavaScript from modules
```

### JavaScript Development

JavaScript is organized in modular files that get combined into a single template:

```bash
# Edit source modules
vim src/homepage/static/js/modules/04-rss.js.j2

# Build combined JavaScript
make build-js

# This generates src/homepage/templates/scripts.js.j2
```

### CSS Development

CSS is organized in modular files that get included via Jinja2:

```
src/homepage/templates/css/
├── base/         # Reset, typography, variables
├── components/   # Clock, search, weather, etc.
├── features/     # Editing, animations, responsive
└── layout/       # Grid, sidebar

Combined in: styles-modular.css.j2
```

## Docker

Docker files are in the `docker/` directory:

```bash
make docker-build   # Build image
make docker-run     # Run container
make docker-stop    # Stop container
```

Or directly:
```bash
docker build -f docker/Dockerfile -t homepage .
docker-compose -f docker/docker-compose.yml up -d
```

## Benefits of This Structure

1. **Clean Separation** - Code, config, docs, and deployment files are organized
2. **Standard Layout** - Follows Python packaging best practices
3. **Easy Installation** - Works with pip, pipx, and standard tools
4. **Maintainability** - Clear organization makes the project easier to maintain
5. **Distribution** - Can be published to PyPI if desired

## Migration from Old Structure

If you have an existing installation:

1. Configuration files have moved to `data/`
2. Run `./scripts/install.sh` to set up the new structure
3. The installer creates backward-compatible symlinks
4. Update any custom scripts to reference new paths

For detailed migration instructions, see `MIGRATION.md`.
