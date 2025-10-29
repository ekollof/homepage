# Quick Start Guide

Get your customizable homepage running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- A terminal

## Installation

```bash
cd ~/Code/homepage
./install.sh
```

## Start the Service

```bash
systemctl --user start homepage.service
```

## Open Your Homepage

Open your browser to: **http://localhost:5000**

## Customize Your Links

Edit `links.toml` to add your own links and categories:

```bash
nano links.toml  # or use your preferred editor
```

After editing, restart the service:

```bash
systemctl --user restart homepage.service
```

## Enable Auto-Start (Optional)

To start the homepage automatically on login:

```bash
systemctl --user enable homepage.service
```

## Theming (Optional)

### Use Pywal Colors

If you have [pywal](https://github.com/dylanaraps/pywal) installed:

```bash
wal -i /path/to/your/wallpaper.jpg
```

The homepage will automatically use the generated colors!

### Set Background Wallpaper

Create a file pointing to your wallpaper:

```bash
echo "/path/to/your/wallpaper.jpg" > ~/.wallpaper
```

The homepage will automatically reload when colors or wallpaper changes.

## Common Commands

```bash
# View service status
systemctl --user status homepage.service

# View logs
journalctl --user -u homepage.service -f

# Stop service
systemctl --user stop homepage.service

# Restart service
systemctl --user restart homepage.service
```

## Need Help?

See the full [README.md](README.md) for detailed documentation.