#!/bin/sh

set -e

echo "=========================================="
echo "Homepage Installation Script (BSD)"
echo "=========================================="
echo ""

# Get the directory where the script is located (scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get project root (parent of scripts/)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Installation directory: $PROJECT_ROOT"
echo ""

# Detect OS
OS_TYPE=$(uname -s)
echo "Detected OS: $OS_TYPE"
echo ""

# Create virtual environment
echo "[1/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Install dependencies
echo "[2/5] Installing package..."
./venv/bin/pip install --upgrade pip > /dev/null 2>&1
./venv/bin/pip install -e .
echo "✓ Package installed"
echo ""

# Create data directory and example config if it doesn't exist
echo "[3/5] Checking configuration..."
mkdir -p data
if [ ! -f "data/links.toml" ]; then
    echo "⚠ data/links.toml not found - please copy your configuration"
    if [ -f "links.toml" ]; then
        cp links.toml data/links.toml
        echo "✓ Copied links.toml to data/"
    fi
else
    echo "✓ data/links.toml exists"
fi
echo ""

# Create symlinks for backward compatibility
echo "[4/5] Creating compatibility symlinks..."
if [ ! -L "links.toml" ]; then
    ln -sf data/links.toml links.toml 2>/dev/null || true
fi
if [ ! -L ".env.example" ]; then
    ln -sf data/.env.example .env.example 2>/dev/null || true
fi
echo "✓ Symlinks created"
echo ""

# Install XDG autostart
echo "[5/5] Setting up XDG autostart..."
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

# Create desktop file with actual paths
sed "s|INSTALL_DIR_PLACEHOLDER|$PROJECT_ROOT|g" scripts/homepage.desktop > "$AUTOSTART_DIR/homepage.desktop"
chmod +x "$AUTOSTART_DIR/homepage.desktop"

echo "✓ Desktop file installed to $AUTOSTART_DIR/homepage.desktop"
echo "  Working directory: $PROJECT_ROOT"
echo ""

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Read the documentation:"
echo "   cat docs/QUICKSTART.md"
echo ""
echo "2. Edit data/links.toml to customize your links"
echo ""
echo "3. Start the server manually:"
echo "   make run"
echo "   # OR:"
echo "   ./venv/bin/python -m homepage.app"
echo ""
echo "4. The server will auto-start on next login via XDG autostart"
echo ""
echo "5. To start it now without rebooting:"
echo "   nohup ./venv/bin/python -m homepage.app > /dev/null 2>&1 &"
echo ""
echo "6. Check if it's running:"
echo "   pgrep -f 'python.*homepage.app'"
echo ""
echo "7. Open in browser:"
echo "   http://localhost:5000"
echo ""
echo "Documentation:"
echo "   docs/QUICKSTART.md  - Quick start guide"
echo "   docs/FEATURES.md    - Feature documentation"
echo "   docs/USAGE.md       - Usage guide"
echo ""
echo "Optional: Install development tools"
echo "   ./venv/bin/pip install -e \".[dev]\""
echo ""
echo "To disable autostart:"
echo "   rm $AUTOSTART_DIR/homepage.desktop"
echo ""
