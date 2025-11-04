# Screenshots

## Desktop View

> **Note:** Add screenshots of your homepage here once deployed

### Default Theme (Gruvbox Dark)
![Homepage Desktop - Gruvbox](images/desktop-gruvbox.png)

### With Pywal Colors
![Homepage Desktop - Pywal](images/desktop-pywal.png)

## Mobile View

### Responsive Layout
![Homepage Mobile](images/mobile-view.png)

## Features

### Search Interface
![Search Bar with Multiple Providers](images/search-providers.png)

### Keyboard Shortcuts
![Keyboard Shortcuts Help](images/keyboard-shortcuts.png)

### Link Categories
![Organized Link Categories](images/link-categories.png)

## Statistics Dashboard

### Metrics View
![Application Statistics](images/stats-dashboard.png)

---

## Creating Screenshots

To create screenshots for documentation:

1. Start the application:
   ```bash
   make run
   ```

2. Open http://localhost:5000 in your browser

3. Take screenshots at different resolutions:
   - Desktop: 1920x1080
   - Tablet: 768x1024
   - Mobile: 375x667

4. Save images to `docs/images/` directory

5. Optimize images:
   ```bash
   # Install imagemagick if needed
   sudo apt install imagemagick

   # Optimize PNG
   convert image.png -quality 85 image-optimized.png

   # Or use optipng
   optipng -o7 image.png
   ```

## Example Screenshots

You can use browser developer tools to test responsive views:

1. Press `F12` to open DevTools
2. Click device toolbar icon (or press `Ctrl+Shift+M`)
3. Select different device presets
4. Take screenshots with browser screenshot tools
