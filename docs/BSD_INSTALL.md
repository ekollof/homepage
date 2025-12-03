# BSD Installation Guide

Quick reference for installing Homepage on FreeBSD, OpenBSD, and NetBSD.

## System Requirements

- Python 3.10 or higher
- XDG-compliant desktop environment (GNOME, KDE, XFCE, etc.)

### Installing Python

**FreeBSD:**
```bash
pkg install python310
# Or latest:
pkg install python3
```

**OpenBSD:**
```bash
pkg_add python3
```

**NetBSD:**
```bash
pkgin install python310
```

## Installation

### Quick Install (Recommended)

```bash
cd /path/to/homepage
./scripts/install.sh
```

The installer automatically detects BSD systems and:
- Creates virtual environment
- Installs all dependencies
- Creates XDG autostart desktop file at `~/.config/autostart/homepage.desktop`
- Configures auto-start on login

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv

# Install package
./venv/bin/pip install -e .

# Install XDG autostart
make autostart-install
```

## Running the Server

### Start Immediately

```bash
# Start in background
make start-daemon

# Or manually
nohup ./venv/bin/python -m homepage.app > /tmp/homepage.log 2>&1 &
```

### Auto-start on Login

The XDG autostart desktop file is installed automatically. The server will start on your next login.

## Service Management

### Check Status

```bash
# Check if running
pgrep -f "python.*homepage.app"

# Or with details
ps aux | grep homepage.app
```

### View Logs

```bash
# Tail the log file
tail -f /tmp/homepage.log

# Or view entire log
cat /tmp/homepage.log
```

### Stop Server

```bash
# Using make
make stop-daemon

# Or manually
pkill -f "python.*homepage.app"
```

### Disable/Enable Autostart

```bash
# Disable autostart
make autostart-disable

# Enable autostart
make autostart-enable

# Or remove desktop file entirely
rm ~/.config/autostart/homepage.desktop
```

## Configuration

Configuration is identical to Linux. See main documentation:

- `data/links.toml` - Link configuration
- `.env` - Environment variables (optional)

Example `.env`:
```bash
HOMEPAGE_ENV=production
HOMEPAGE_HOST=127.0.0.1
HOMEPAGE_PORT=5000
HOMEPAGE_ENABLE_WEATHER=True
HOMEPAGE_ENABLE_METRICS=True
```

## Development

All development commands work the same:

```bash
# Run locally (development mode)
make run

# Run tests
make test

# Check code quality
make check

# Install dev dependencies
./venv/bin/pip install -e ".[dev]"
```

## Platform-Specific Notes

### FreeBSD

- Works out of the box with most desktop environments
- Tested on FreeBSD 13.x and 14.x
- If using a custom window manager without XDG support, consider adding to `~/.xinitrc`:
  ```bash
  (cd /path/to/homepage && ./venv/bin/python -m homepage.app > /tmp/homepage.log 2>&1) &
  ```

### OpenBSD

- Lightweight window managers may not support XDG autostart
- Alternative: Use cron with `@reboot`:
  ```bash
  crontab -e
  # Add:
  @reboot cd /path/to/homepage && ./venv/bin/python -m homepage.app > /tmp/homepage.log 2>&1
  ```

### NetBSD

- XDG autostart works with GNOME, KDE, XFCE
- Ensure you have a desktop environment installed

## Troubleshooting

### Server Not Starting

1. Check Python version: `python3 --version` (must be 3.10+)
2. Check virtual environment: `ls venv/bin/python`
3. Try running manually: `./venv/bin/python -m homepage.app`
4. Check logs: `tail -f /tmp/homepage.log`

### Autostart Not Working

1. Verify desktop file exists: `cat ~/.config/autostart/homepage.desktop`
2. Check Hidden flag: should be `Hidden=false`
3. Verify desktop environment supports XDG autostart
4. Check desktop environment logs

### Port Already in Use

```bash
# Find process using port 5000
sockstat -4 -l | grep 5000  # FreeBSD
fstat | grep 5000           # OpenBSD
netstat -an | grep 5000     # All BSD

# Kill the process
kill <PID>

# Or change port in .env
echo "HOMEPAGE_PORT=8080" > .env
```

## Accessing the Homepage

Once running, open in browser:
```
http://localhost:5000
```

For remote access, see [DEPLOYMENT.md](DEPLOYMENT.md) for reverse proxy setup.

## Further Documentation

- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Full deployment guide
- [FEATURES.md](FEATURES.md) - Feature documentation
- [USAGE.md](USAGE.md) - Usage guide
