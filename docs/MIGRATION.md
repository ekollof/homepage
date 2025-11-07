# Migration Guide: pyproject.toml

This project has been migrated from using `requirements.txt` to a modern `pyproject.toml` configuration. This provides better dependency management and follows current Python packaging standards.

## What Changed

- **Dependencies**: Now managed in `pyproject.toml` instead of `requirements.txt`
- **Installation**: Use `pip install -e .` instead of `pip install -r requirements.txt`
- **Development tools**: Use `pip install -e ".[dev]"` instead of `pip install -r requirements-dev.txt`

## Migration Steps

If you already have the project installed, you can upgrade to the new system:

### Option 1: Reinstall (Recommended)

```bash
# Stop the service if running
systemctl --user stop homepage.service

# Remove old virtual environment
rm -rf venv

# Create new virtual environment
python3 -m venv venv

# Install using new system
./venv/bin/pip install -e .

# Or with dev dependencies
./venv/bin/pip install -e ".[dev]"

# Restart the service
systemctl --user start homepage.service
```

### Option 2: Upgrade Existing venv

```bash
# Stop the service if running
systemctl --user stop homepage.service

# Install in editable mode (will upgrade existing installation)
./venv/bin/pip install -e .

# Optionally install dev dependencies
./venv/bin/pip install -e ".[dev]"

# Restart the service
systemctl --user start homepage.service
```

## Benefits

- **Standardized**: Uses modern Python packaging standards (PEP 621)
- **Consolidated**: All project configuration in one file
- **Editable Mode**: Changes to code are immediately reflected without reinstall
- **Better Tooling**: Better integration with modern Python tools
- **Metadata**: Includes project metadata, classifiers, and entry points

## What Still Works

- All Make commands continue to work
- The install.sh script has been updated
- The systemd service file is unchanged
- Your existing configuration files (links.toml, etc.) are unchanged

## Old Files

The `requirements.txt` and `requirements-dev.txt` files have been removed. All dependencies are now managed exclusively in `pyproject.toml`.

## New Dependencies

When the project needs new dependencies:
- Add to `dependencies` in `pyproject.toml` for production
- Add to `[project.optional-dependencies].dev` for development tools
- Run `pip install -e .` or `pip install -e ".[dev]"` to install

## Questions or Issues?

If you encounter any issues during migration, please:
1. Check that you're using Python 3.10 or higher
2. Ensure pip is up to date: `./venv/bin/pip install --upgrade pip`
3. Try the "Reinstall" option above
