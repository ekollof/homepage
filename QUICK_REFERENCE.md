# Quick Reference Guide - Homepage v2.0

## Installation & Setup

```bash
# Quick install
./install.sh

# Or manually
make install-dev
```

## Running the Application

```bash
# Development mode
make run

# With environment variables
export HOMEPAGE_PORT=8080
export HOMEPAGE_ENABLE_METRICS=True
python app.py

# As systemd service
make service-start
```

## CLI Commands

```bash
# Validate configuration
python cli.py validate
python cli.py validate --check-urls

# View statistics
python cli.py stats
python cli.py stats --export metrics.json

# Check health
python cli.py health

# Export configuration
python cli.py export -o links.json
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search bar |
| `?` | Show keyboard shortcuts help |
| `Esc` | Close help / Clear search |
| `Ctrl+1` | Switch to Brave Search |
| `Ctrl+2` | Switch to Google |
| `Ctrl+3` | Switch to DuckDuckGo |
| `Ctrl+4` | Switch to Bing |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main homepage |
| `/health` | GET | Health check |
| `/api/stats` | GET | Usage statistics |
| `/api/track` | POST | Track events |
| `/check_reload` | GET | Check for config changes |
| `/wallpaper` | GET | Serve wallpaper image |
| `/favicon` | GET | Serve favicon |

## Environment Variables

```bash
# Core settings
HOMEPAGE_HOST=127.0.0.1
HOMEPAGE_PORT=5000
HOMEPAGE_DEBUG=False

# Features
HOMEPAGE_ENABLE_CACHE=True
HOMEPAGE_ENABLE_METRICS=True
HOMEPAGE_ENABLE_COMPRESSION=True

# Clock
HOMEPAGE_CLOCK_FORMAT=24  # or 12

# Cache
HOMEPAGE_CACHE_TTL=5  # seconds
```

## Docker

```bash
# Build and run
make docker-build
make docker-run

# Or with docker-compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Development

```bash
# Format code
make format

# Run linters
make lint

# Run all checks
make check

# Run tests
make test

# Run tests with coverage
make test-cov
```

## Service Management

```bash
# Start/stop/restart
make service-start
make service-stop
make service-restart

# View status and logs
make service-status
make logs

# Enable/disable auto-start
make service-enable
make service-disable
```

## Testing URLs

```bash
# Health check
curl http://localhost:5000/health

# Statistics
curl http://localhost:5000/api/stats | jq

# Check reload needed
curl http://localhost:5000/check_reload
```

## Configuration Files

| File | Purpose |
|------|---------|
| `links.toml` | Link configuration |
| `.env` | Environment variables |
| `config.py` | Application config |
| `~/.cache/wal/colors.json` | Pywal colors |
| `~/.wallpaper` | Wallpaper path |

## Troubleshooting

```bash
# Check logs
journalctl --user -u homepage.service -f

# Validate configuration
python cli.py validate

# Check if port is in use
sudo lsof -i :5000

# Test application
curl -f http://localhost:5000/health || echo "Not running"
```

## Common Tasks

### Change Port
```bash
export HOMEPAGE_PORT=8080
systemctl --user restart homepage.service
```

### Enable Metrics
```bash
export HOMEPAGE_ENABLE_METRICS=True
systemctl --user restart homepage.service
```

### Export Statistics
```bash
python cli.py stats --export stats_$(date +%Y%m%d).json
```

### Update Configuration
```bash
# Edit links.toml
vi links.toml

# Page will auto-reload in ~2 seconds
# Or restart service
systemctl --user restart homepage.service
```

### Backup Configuration
```bash
cp links.toml links.toml.backup
python cli.py export -o links_backup.json
```

## File Structure

```
homepage/
├── app.py              # Main application
├── config.py           # Configuration
├── utils.py            # Utilities & caching
├── metrics.py          # Metrics collection
├── cli.py              # CLI tool
├── links.toml          # Your links
├── templates/          # HTML templates
│   └── index.html
├── tests/              # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   └── test_app.py
├── docs/               # Documentation
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── SCREENSHOTS.md
├── Dockerfile          # Docker image
├── docker-compose.yml  # Docker Compose
├── Makefile           # Development tasks
└── requirements.txt    # Dependencies
```

## Performance Tuning

```bash
# Enable all optimizations
export HOMEPAGE_ENABLE_CACHE=True
export HOMEPAGE_ENABLE_COMPRESSION=True
export HOMEPAGE_CACHE_TTL=60

# For production
export HOMEPAGE_ENV=production
export HOMEPAGE_DEBUG=False
export HOMEPAGE_LOG_LEVEL=INFO
```

## Security Checklist

- [ ] Change `HOMEPAGE_SECRET_KEY` in production
- [ ] Use HTTPS with reverse proxy
- [ ] Enable firewall rules
- [ ] Keep dependencies updated
- [ ] Review logs regularly
- [ ] Backup configuration files

## Getting Help

- **Documentation**: See `docs/` directory
- **API Reference**: `docs/API.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Contributing**: `CONTRIBUTING.md`
- **Changelog**: `CHANGELOG.md`

## Quick Links

- Health check: http://localhost:5000/health
- Statistics: http://localhost:5000/api/stats
- Homepage: http://localhost:5000
