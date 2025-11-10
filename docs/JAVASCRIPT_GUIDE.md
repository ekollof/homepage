# JavaScript Code Organization Guide

## Overview

JavaScript is organized in modular source files that are combined into a single template for deployment.

## Architecture

### Source Files (Editable)

Located in `src/homepage/static/js/modules/`:

```
01-constants-and-cache.js.j2  - Configuration and DOM caching
02-clock.js.j2                - Clock and date functionality
03-weather.js.j2              - Weather and forecast
04-rss.js.j2                  - RSS feed carousel
05-search.js.j2               - Search and event tracking
06-system-stats.js.j2         - System statistics sidebar
07-edit-mode-core.js.j2       - Edit mode core functionality
08-edit-templates.js.j2       - HTML template generation
09-edit-modals.js.j2          - Add/Edit/Delete modals
10-drag-drop.js.j2            - Drag and drop reordering
11-initialization.js.j2       - Initialization and WebSocket
```

### Generated File (Do Not Edit Directly)

`src/homepage/templates/scripts.js.j2` - Combined from all modules

## Development Workflow

### 1. Edit Source Modules

Edit the appropriate module file:

```bash
# Edit RSS functionality
vim src/homepage/static/js/modules/04-rss.js.j2

# Edit clock functionality  
vim src/homepage/static/js/modules/02-clock.js.j2
```

### 2. Build Combined JavaScript

After editing, rebuild the combined file:

```bash
make build-js
```

This runs `scripts/build_js.py` which:
- Reads all `[0-9][0-9]-*.js.j2` files in numeric order
- Combines them with proper formatting
- Writes to `src/homepage/templates/scripts.js.j2`

### 3. Test and Deploy

```bash
# Run linting
make lint-js

# Test the app
make run

# Restart service if needed
systemctl --user restart homepage.service
```

## Module Descriptions

## Module Descriptions

### 01-constants-and-cache.js.j2
**Purpose:** Configuration constants, DOM element cache, CSS class names  
**Key Features:**
- `CLOCK_FORMAT`, `RELOAD_INTERVAL` - Config constants
- `DOM` object - Cached DOM element references
- `CSS_CLASSES` object - CSS class name constants
- `initDOMCache()` - Initialize DOM cache on load

### 02-clock.js.j2
**Purpose:** Time and date display  
**Key Features:**
- `updateClock()` - Update clock (12h/24h format)
- `updateDate()` - Update date display
- Auto-updates every second

### 03-weather.js.j2
**Purpose:** Weather data fetching and display  
**Key Features:**
- `updateWeather()` - Fetch current weather
- `updateWeatherForecast()` - Fetch forecast data
- `createDailyForecastItem()` - Daily forecast template
- `createHourlyForecastItem()` - Hourly forecast template
- Weather icon mapping

### 04-rss.js.j2
**Purpose:** RSS feed carousel  
**Key Features:**
- `updateRSSFeeds()` - Fetch feeds from server
- `renderRSSCarousel()` - Render with navigation
- `nextRSSItem()`, `prevRSSItem()` - Navigation
- `startRSSAutoRotate()` - Auto-rotation (30s)

### 05-search.js.j2
**Purpose:** Search and event tracking  
**Key Features:**
- `handleSearch()` - Process search submissions
- `checkForReload()` - Poll for config changes
- `saveSearchHistory()` - LocalStorage persistence
- `trackEvent()` - Send analytics to server

### 06-system-stats.js.j2
**Purpose:** Real-time system statistics  
**Key Features:**
- `toggleSystemStats()` - Show/hide sidebar
- `updateSystemStats()` - Fetch and display stats
- `setStatsPosition()` - Position control (left/right/top/bottom)
- `updateSparkline()` - CPU/memory charts
- `formatUptime()` - Uptime formatting

### 07-edit-mode-core.js.j2
**Purpose:** Core edit mode functionality  
**Key Features:**
- `toggleEditMode()` - Enter/exit edit mode
- `loadConfig()` - Load configuration from server
- `fetchMissingFavicons()` - Auto-fetch icons
- `saveAndExit()` - Save and exit
- `fetchAndCacheFavicon()` - Favicon proxy

### 08-edit-templates.js.j2
**Purpose:** HTML template generation  
**Key Features:**
- `createLinkItemHTML()` - Generate link HTML
- `createSubcategoryHTML()` - Generate subcategory
- `createCategoryHTML()` - Generate category
- `updateCategoryDisplay()` - Rebuild entire display
- `saveLinkToConfig()` - Persist to config

### 09-edit-modals.js.j2
**Purpose:** Add/Edit/Delete operations  
**Key Features:**
- `addCategory()`, `editCategory()`, `deleteCategory()`
- `addSubcategory()`, `editSubcategory()`, `deleteSubcategory()`
- `addLink()`, `editLink()`, `deleteLink()`
- `showConfirmDialog()` - Confirmation dialogs
- `closeModal()` - Modal management

### 10-drag-drop.js.j2
**Purpose:** Drag and drop reordering  
**Key Features:**
- Widget reordering (weather, RSS, stats)
- Category reordering
- Link reordering within categories/subcategories
- `enableWidgetDragging()`, `enableCategoryDragging()`, `enableLinkDragging()`
- Persistence to localStorage/config

### 11-initialization.js.j2
**Purpose:** App initialization and WebSocket  
**Key Features:**
- `DOMContentLoaded` setup
- WebSocket client initialization
- Event handler registration
- Keyboard shortcuts
- Real-time update handlers

## Finding Specific Functionality

### Want to modify the clock?
Edit: `02-clock.js.j2`

### Want to change RSS behavior?
Edit: `04-rss.js.j2`

### Want to add a new widget?
1. Create new module (e.g., `12-my-widget.js.j2`)
2. Add your code
3. Run `make build-js`

### Want to change drag-and-drop?
Edit: `10-drag-drop.js.j2`

## Best Practices

1. **Maintain Load Order:** Modules load in numeric order. If module B depends on module A, give B a higher number.

2. **Use Jinja2 Variables:** All config variables are available:
   ```javascript
   {% if config.ENABLE_WEATHER %}
   // Weather-specific code
   {% endif %}
   ```

3. **Document Dependencies:** Add comments noting which modules you depend on:
   ```javascript
   /**
    * Module: My Feature
    * Dependencies: 01-constants-and-cache.js.j2 (DOM object)
    */
   ```

4. **Keep Modules Focused:** Each module should handle one major feature.

5. **Always Rebuild:** After editing, always run `make build-js`.

## Troubleshooting

### Changes not appearing?
1. Did you run `make build-js`?
2. Did you restart the service if using systemd?
3. Clear browser cache (Ctrl+Shift+R)

### Build fails?
Check for JavaScript syntax errors in your module:
```bash
# Lint before building
make lint-js
```

### Module not loading?
1. Check filename matches pattern: `[0-9][0-9]-*.js.j2`
2. Verify file is in `src/homepage/static/js/modules/`
3. Check build output: `python scripts/build_js.py`

## Legacy Note

**Old Structure (Removed):**  
Previous versions had `static/js/{widgets,core,features,editing}/` directories with ES6 modules. These were never integrated and have been removed. The current system uses numbered modules that get combined into a single template.

## See Also

- `src/homepage/static/js/modules/README.md` - Module system details
- `scripts/build_js.py` - Build script implementation
- `Makefile` - Build targets
  - `updateLinkOrder()`
  
- **Subcategory Dragging** (1872-2020): Reorder subcategories
  - `enableSubcategoryDragging()`, `disableSubcategoryDragging()`
  - `handleSubcategoryDragStart()`, `handleSubcategoryDrop()`, etc.
  - `updateSubcategoryOrder()`

### Lines 2021-2136: Initialization and WebSocket
**What:** Page initialization and WebSocket event handlers
**Sections:**
- DOM cache initialization
- Event listener setup (buttons, keyboard shortcuts)
- Clock/date timers
- Weather/RSS update intervals
- WebSocket event handlers (if enabled)
  - `config_changed`, `system_stats_update`, `weather_update`, `rss_update`, `links_update`
- Polling fallback (if WebSocket disabled)

## Quick Reference by Feature

### Adding a New Feature
1. Decide which section it belongs to
2. Add functions in that section
3. Add initialization code at the bottom (lines 2021+)
4. Update this guide

### Modifying Existing Features

| Feature | Lines | Key Functions |
|---------|-------|---------------|
| Clock | 78-111 | `updateClock()`, `updateDate()` |
| Weather | 112-240 | `updateWeather()`, `updateWeatherForecast()` |
| RSS | 241-352 | `updateRSSFeeds()`, `renderRSSCarousel()` |
| Search | 353-428 | `handleSearch()` |
| Stats | 429-770 | `updateSystemStats()`, `toggleSystemStats()` |
| Edit Mode | 771-1430 | `toggleEditMode()`, `updateCategoryDisplay()` |
| Drag/Drop | 1431-2020 | `enableXXXDragging()`, `updateXXXOrder()` |
| Init | 2021-2136 | Event listeners, timers |

### Common Patterns

**DOM Access:**
```javascript
// ✅ Good - Uses cached DOM
DOM.linksContainer.classList.add(CSS_CLASSES.EDIT_MODE);

// ❌ Avoid - Repeated queries
document.getElementById('linksContainer').classList.add('edit-mode');
```

**Template Generation:**
```javascript
// ✅ Good - Use template functions
const html = createCategoryHTML(category, index);

// ❌ Avoid - Inline string building
let html = `<div class="category">...</div>`;
```

**Event Handling:**
```javascript
// ✅ Good - addEventListener
DOM.editToggle.addEventListener('click', toggleEditMode);

// ❌ Avoid - Inline onclick (except in templates)
<button onclick="toggleEditMode()">
```

## Future Modularization

When ready to split into modules, use this structure:
```
01-constants-and-cache.js.j2  (Lines 1-77)
02-clock.js.j2                 (Lines 78-111)
03-weather.js.j2               (Lines 112-240)
04-rss.js.j2                   (Lines 241-352)
05-search.js.j2                (Lines 353-428)
06-system-stats.js.j2          (Lines 429-770)
07-edit-mode-core.js.j2        (Lines 771-920)
08-edit-templates.js.j2        (Lines 921-1098)
09-edit-modals.js.j2           (Lines 1099-1430)
10-drag-drop.js.j2             (Lines 1431-2020)
11-initialization.js.j2        (Lines 2021-2136)
```

Use `make build-js` to combine modules back into single file.

## Tips for Maintenance

1. **Keep sections together** - Don't scatter related functions
2. **Update this guide** - When adding features, update line numbers
3. **Use JSDoc comments** - Document complex functions
4. **Test after changes** - Run `make lint-js && make check-all`
5. **Backup before major refactoring** - `cp scripts.js.j2 scripts.js.j2.backup`

## Related Files

- `scripts/build_js.py` - Module builder script
- `eslint.config.js` - JavaScript linting configuration
- `scripts/render_template.py` - Template renderer for linting
- `Makefile` - Build and lint targets
