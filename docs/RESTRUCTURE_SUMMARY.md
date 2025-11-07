# Project Restructure Summary

## What Changed

The Homepage project has been reorganized to follow modern Python packaging best practices with a clean, professional directory structure.

### New Directory Structure

```
homepage/
├── src/homepage/          # Python package source code
│   ├── app.py            # Main Flask application
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── metrics.py        # Metrics collection
│   ├── utils.py          # Utility functions
│   ├── templates/        # Jinja2 templates
│   └── static/           # Static assets
│
├── data/                  # Configuration and data files
│   ├── links.toml        # Link configuration
│   ├── *.mmdb            # GeoIP databases
│   └── .env.example      # Environment template
│
├── docker/                # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── scripts/               # Installation scripts
│   ├── install.sh
│   ├── setup_geoip.sh
│   └── homepage.service  # Systemd template
│
├── docs/                  # Documentation (already existed)
├── tests/                 # Test suite (already existed)
└── pyproject.toml        # Project configuration

```

### Key Changes

1. **Source code** moved to `src/homepage/` (proper Python package)
2. **Configuration files** moved to `data/`
3. **Docker files** moved to `docker/`
4. **Scripts** moved to `scripts/`
5. **Documentation** already in `docs/` (no change)
6. **Tests** remain in `tests/` (no change)

## Installation & Usage

### Fresh Installation

```bash
# Using the install script (recommended)
./scripts/install.sh

# Using Make
make install          # Production
make install-dev      # Development

# Using pip directly
pip install -e .           # Production
pip install -e ".[dev]"    # Development

# Using pipx (isolated environment)
pipx install -e .
```

### Running the Application

```bash
# Using the installed command
homepage

# Using Python module
python -m homepage.app

# Using Make
make run

# Using systemd
systemctl --user start homepage.service
```

### Development Commands

```bash
make test         # Run tests (47 tests, all passing)
make test-cov     # Run tests with coverage
make format       # Format code with Black
make lint         # Run linters (ruff, pylint, pyright)
make check        # Format + lint
```

### Docker Usage

```bash
make docker-build   # Build image
make docker-run     # Run container
make docker-stop    # Stop container

# Or directly
docker build -f docker/Dockerfile -t homepage .
docker-compose -f docker/docker-compose.yml up -d
```

## Migration from Old Structure

### Backward Compatibility

Symlinks have been created for backward compatibility:
- `links.toml` → `data/links.toml`
- `.env.example` → `data/.env.example`

### Configuration Files

Your configuration files have moved:
- **Old:** `links.toml` in project root
- **New:** `data/links.toml`
- **Override:** `data/links.override.toml` (gitignored)

The install script automatically handles this migration.

### Service Files

If you have an existing systemd service:
1. Run `./scripts/install.sh` or `make service-install`
2. The service will be updated to use `python -m homepage.app`
3. Restart the service: `systemctl --user restart homepage.service`

## Benefits of New Structure

1. **Professional Layout** - Follows Python packaging standards (PEP 517/518)
2. **Clean Project Root** - Less clutter, easier to navigate
3. **Better Organization** - Clear separation of code, config, docs, deployment
4. **Distribution Ready** - Can be published to PyPI
5. **Tool Compatibility** - Works with modern Python tools (pipx, poetry, etc.)
6. **Maintainability** - Easier to understand and maintain
7. **Standard Imports** - Package is importable as `homepage`

## Verification

All systems verified working:
- ✅ Installation via pip/pipx
- ✅ Installation via install.sh
- ✅ All 47 tests passing
- ✅ Make commands working
- ✅ Application runs successfully
- ✅ Module imports work correctly
- ✅ Docker build succeeds
- ✅ Code quality checks pass

## Files Updated

### Core Files
- `pyproject.toml` - Updated package structure and paths
- `Makefile` - Updated all paths and commands
- `.gitignore` - Updated for new structure

### Source Code
- All Python files use relative imports (`.config`, `.utils`, etc.)
- Paths updated to reference `data/` directory
- Module structure properly defined

### Scripts
- `scripts/install.sh` - Updated for new structure
- `scripts/homepage.service` - Uses `python -m homepage.app`
- `scripts/setup_geoip.sh` - No changes needed

### Docker
- `docker/Dockerfile` - Updated to copy from new locations
- `docker/docker-compose.yml` - Updated build context and volume mounts

### CI/CD
- `.github/workflows/ci.yml` - Updated test and lint paths

### Tests
- `tests/test_app.py` - Updated all imports to use `homepage.*`

## Next Steps

1. **Test your setup:** Run `./scripts/install.sh`
2. **Verify it works:** `make test`
3. **Start the service:** `systemctl --user restart homepage.service`
4. **Check it's running:** `curl http://localhost:5000/health`

## Documentation

- `PROJECT_STRUCTURE.md` - Detailed structure explanation
- `MIGRATION.md` - Migration guide from requirements.txt
- `docs/DEPLOYMENT.md` - Deployment guide (updated)
- `docs/QUICKSTART.md` - Quick start guide

## Support

If you encounter issues:
1. Check `PROJECT_STRUCTURE.md` for detailed information
2. Run `make clean && make install-dev` for a fresh install
3. Verify paths in the service file
4. Check logs: `journalctl --user -u homepage.service -f`

---

**Date:** November 7, 2025
**Change Type:** Project restructuring (non-breaking, backward compatible)
**Status:** Complete ✅
