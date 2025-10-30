# Usage Guide

Complete guide to using your Homepage web application.

## Overview

Your homepage consists of three main sections:
1. **Header**: Clock, date, and web search
2. **Links**: Organized categories and subcategories
3. **Background**: Dynamic wallpaper and color scheme

## Using the Web Search

### Search Bar Location

The search bar is located in the header section, directly below the date display.

### Performing a Search

1. **Select a search provider** from the dropdown menu:
   - **Brave Search** (default)
   - **Google**
   - **DuckDuckGo**
   - **Bing**

2. **Type your search query** in the text input field

3. **Press Enter** or click outside the field to submit

4. **Results open in a new tab** with your selected search provider

5. **Input automatically clears** after the search

### Search Provider Details

#### Brave Search
- Privacy-focused search engine
- Independent index
- No tracking
- Default provider

#### Google
- Most comprehensive results
- Personalized if logged in
- Feature-rich (images, maps, etc.)

#### DuckDuckGo
- Privacy-focused
- No tracking or personalization
- Clean interface
- Bangs support (e.g., !w for Wikipedia)

#### Bing
- Microsoft's search engine
- Integration with Microsoft services
- Rewards program

### Keyboard Shortcuts

- **Enter**: Submit search
- **Escape**: Clear search input (manual)
- **Tab**: Navigate between provider selector and search input

### Search Tips

- Queries are properly URL-encoded (handles spaces and special characters)
- Search provider selection persists across searches
- No character limit on queries
- Works offline (opens when internet connection is restored)

## Navigating Links

### Link Organization

Links are organized hierarchically:

```
Category
├── Direct Link 1
├── Direct Link 2
├── Subcategory 1
│   ├── Link A
│   └── Link B
└── Subcategory 2
    ├── Link C
    └── Link D
```

### Opening Links

- **Click any link** to open in a new tab
- All external links have security attributes (`noopener noreferrer`)
- Links maintain your browser's default behavior (middle-click, right-click context menu)

### Visual Indicators

- **Category titles**: Large colored headers with icons
- **Subcategories**: Indented with distinct color
- **Links**: Smaller text with icons
- **Hover effects**: Links highlight on mouse hover

## Clock and Date

### Digital Clock

- Located at the top center of the page
- **24-hour format** (00:00:00 to 23:59:59)
- Updates every second
- Zero-padded (e.g., 09:05:03)

### Date Display

- Shows full date below clock
- Format: **Weekday, Month Day, Year**
- Example: "Monday, October 29, 2024"
- Updates automatically at midnight

## Theme Customization

### Pywal Integration

If you use [pywal](https://github.com/dylanaraps/pywal), the homepage automatically adapts to your color scheme:

1. Generate colors with pywal:
   ```bash
   wal -i /path/to/wallpaper.jpg
   ```

2. Page automatically detects `~/.cache/wal/colors.json`

3. Page reloads within 2 seconds to apply new colors

4. All UI elements update (text, borders, backgrounds, links)

### Fallback Theme

If pywal is not detected, the page uses **Gruvbox Dark** theme:
- Warm, retro-inspired colors
- High contrast for readability
- Consistent color palette

### Color Mapping

Different UI elements use specific colors from your theme:
- **Clock**: Accent color (typically blue)
- **Date**: Secondary accent (typically cyan/teal)
- **Category titles**: Warning color (typically yellow/orange)
- **Subcategory titles**: Error color (typically red/orange)
- **Links**: Accent color (typically cyan/green)
- **Borders**: Dim color for subtle separation

## Background Wallpaper

### Setting Your Wallpaper

Create or edit `~/.wallpaper` with the path to your image:

```bash
echo "/path/to/your/wallpaper.jpg" > ~/.wallpaper
```

### Supported Formats

The wallpaper endpoint serves any image format your browser supports:
- JPEG/JPG
- PNG
- WebP
- GIF
- BMP
- SVG

### Wallpaper Display

- **Cover mode**: Scales to fill entire viewport
- **Centered**: Image centered on screen
- **Fixed**: Background doesn't scroll with content
- **Dark overlay**: 70% opacity black overlay for readability

### Changing Wallpaper

1. Update `~/.wallpaper` file with new path
2. Page automatically reloads within 2 seconds
3. New wallpaper appears immediately

### No Wallpaper

If no wallpaper is set:
- Background is pure black (#000000)
- Dark overlay still applies
- All text remains readable

## Auto-Reload Feature

### What Triggers Reload

The page automatically reloads when:
- `~/.cache/wal/colors.json` is modified
- `~/.wallpaper` file is modified

### Reload Timing

- JavaScript polls server every 2 seconds
- Detection is near-instant (within 2-4 seconds)
- Page performs full reload (refresh)
- Scroll position resets to top

### Manual Reload

You can always reload manually:
- **F5** or **Ctrl+R** (standard browser refresh)
- **Ctrl+Shift+R** (hard refresh, clears cache)

## Responsive Design

### Desktop View

- Multi-column grid layout
- Categories arranged in auto-fitting columns
- Maximum width: 1400px
- Optimal for large screens

### Tablet View (768px - 480px)

- Single column layout
- Larger tap targets
- Adjusted font sizes
- Optimized spacing

### Mobile View (<480px)

- Compact single column
- Search bar stacks vertically
- Reduced padding
- Smaller fonts
- Touch-optimized

### Auto-Adaptation

The page automatically adjusts based on:
- **Screen width**: Responsive breakpoints
- **Device orientation**: Works in portrait and landscape
- **Viewport size**: Proper scaling on all devices

## Browser Compatibility

### Recommended Browsers

- **Chrome/Chromium**: Full support, best performance
- **Firefox**: Full support
- **Safari**: Full support (macOS/iOS)
- **Edge**: Full support
- **Brave**: Full support (recommended)

### Required Features

Your browser must support:
- ES6 JavaScript (2015+)
- CSS Grid
- CSS Flexbox
- Fetch API
- Local Storage (for browser defaults)

### Tested Platforms

- Linux (primary platform)
- macOS
- Windows 10/11
- Android (Chrome/Firefox)
- iOS (Safari)

## Tips and Tricks

### Quick Access

Bookmark the homepage:
- Set as browser home page
- Set as new tab page (browser extension needed)
- Pin tab for quick access

### Search Provider Strategy

- **Privacy-focused**: Use Brave or DuckDuckGo
- **Comprehensive results**: Use Google
- **Microsoft ecosystem**: Use Bing
- **Mixed approach**: Switch based on query type

### Link Organization

- Put most-used links in top categories
- Group related services together
- Use descriptive category names
- Add visual icons for quick recognition

### Multiple Devices

- Access from any device on your network (if you expose the port)
- Responsive design works on all screen sizes
- Sync link configuration via dotfiles

### Theming Workflow

1. Choose wallpaper
2. Run `wal -i wallpaper.jpg`
3. Update `~/.wallpaper` file
4. Homepage updates automatically
5. Entire system matches (if using pywal for other apps)

## Troubleshooting

### Search Not Working

- Check that JavaScript is enabled
- Verify internet connection
- Try a different search provider
- Check browser console for errors

### Links Not Opening

- Verify URLs in `links.toml`
- Check popup blocker settings
- Ensure links have proper `http://` or `https://` prefix

### Colors Not Updating

- Verify `~/.cache/wal/colors.json` exists
- Check file permissions (must be readable)
- Wait 2-4 seconds for auto-reload
- Manual refresh with F5

### Wallpaper Not Showing

- Verify `~/.wallpaper` contains valid path
- Check image file exists and is readable
- Check browser console for 404 errors
- Verify Flask server is running

### Page Not Reloading

- Check browser console for errors
- Verify `/check_reload` endpoint responds
- Restart the service: `systemctl --user restart homepage.service`
- Check service logs: `journalctl --user -u homepage.service`

## Advanced Usage

### Custom Search Providers

Edit `app.py` and modify the `searchUrls` object:

```javascript
const searchUrls = {
    'custom': 'https://example.com/search?q=',
    // ... existing providers
};
```

Add corresponding option in HTML:

```html
<option value="custom">Custom Search</option>
```

### Keyboard-Focused Workflow

1. Open homepage
2. Type to focus search (if browser supports)
3. Enter query, press Enter
4. Or Tab to navigate to links
5. Enter to open highlighted link

### Integration with Tools

- **Alfred/Rofi**: Launch browser to homepage URL
- **i3/Sway**: Bind key to open browser to homepage
- **Pywal hooks**: Auto-update wallpaper on scheme change
- **Cron/systemd timers**: Rotate wallpapers automatically

## Performance Notes

### First Load

- Initial page load: ~100-300ms
- Wallpaper load: Depends on image size
- Total ready: <1 second on fast connection

### Ongoing Usage

- Clock updates: Every 1 second (minimal CPU)
- Reload checks: Every 2 seconds (minimal network)
- Link clicks: Instant (new tab)
- Search: Instant (client-side)

### Optimization Tips

- Use compressed images for wallpaper (WebP recommended)
- Keep link count reasonable (<100 for best performance)
- Use system wallpaper for fastest load
- Disable auto-reload if not using pywal

## Privacy Considerations

### Data Collection

The homepage does NOT collect:
- Search queries (handled client-side)
- Click tracking on links
- Usage statistics
- Personal information

### Search Privacy

- Queries go directly to selected search provider
- No server-side logging
- Privacy depends on chosen search engine
- Use Brave/DuckDuckGo for maximum privacy

### Local Only

- Server binds to localhost only (127.0.0.1)
- Not accessible from network (by default)
- All data stays on your machine
- No external API calls

## Getting Help

### Documentation

- **README.md**: Installation and configuration
- **QUICKSTART.md**: Fast setup guide
- **FEATURES.md**: Complete feature list
- **TECHNICAL.md**: Implementation details
- **USAGE.md**: This file

### Logs

Check service logs for errors:

```bash
journalctl --user -u homepage.service -f
```

### Support

- Check documentation first
- Review GitHub issues (if applicable)
- Check browser console for JavaScript errors
- Verify systemd service status

## Summary

Your homepage is designed to be:
- **Fast**: Minimal requests, instant response
- **Private**: No tracking, local-only by default
- **Customizable**: TOML config, pywal theming
- **Functional**: Quick search, organized links
- **Beautiful**: Dynamic theming, smooth animations

Enjoy your personalized homepage! 🚀