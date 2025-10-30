#!/bin/bash

set -e

echo "=========================================="
echo "Homepage Installation Script"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installation directory: $SCRIPT_DIR"
echo ""

# Create virtual environment
echo "[1/4] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Install dependencies
echo "[2/4] Installing dependencies..."
./venv/bin/pip install --upgrade pip > /dev/null 2>&1
./venv/bin/pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create example config if it doesn't exist
echo "[3/4] Checking configuration..."
if [ ! -f "links.toml" ]; then
    echo "⚠ links.toml not found - using default configuration"
else
    echo "✓ links.toml exists"
fi
echo ""

# Install systemd service
echo "[4/4] Setting up systemd service..."
SERVICE_DIR="$HOME/.config/systemd/user"
mkdir -p "$SERVICE_DIR"
cp homepage.service "$SERVICE_DIR/"
systemctl --user daemon-reload
echo "✓ Service file installed"
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
echo "2. Edit links.toml to customize your links"
echo ""
echo "3. Start the service:"
echo "   systemctl --user start homepage.service"
echo ""
echo "4. Enable auto-start on boot:"
echo "   systemctl --user enable homepage.service"
echo ""
echo "5. Check service status:"
echo "   systemctl --user status homepage.service"
echo ""
echo "6. View logs:"
echo "   journalctl --user -u homepage.service -f"
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
echo "   ./venv/bin/pip install -r requirements-dev.txt"
echo ""
