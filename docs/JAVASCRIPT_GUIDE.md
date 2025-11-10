# JavaScript Code Organization Guide

## Overview

The JavaScript code in `src/homepage/templates/scripts.js.j2` is organized into logical sections. This guide helps you quickly find and modify specific functionality.

## File Structure (~2,150 lines)

### Lines 1-77: Constants and DOM Cache
**What:** Configuration constants, DOM element cache, CSS class names
**Key Functions:**
- `initDOMCache()` - Initialize DOM element references
- `DOM` object - Cached DOM elements
- `CSS_CLASSES` object - CSS class name constants

### Lines 78-111: Clock and Date
**What:** Time and date display
**Key Functions:**
- `updateClock()` - Update clock display (12h/24h format)
- `updateDate()` - Update date display

### Lines 112-240: Weather and Forecast
**What:** Weather data fetching and display
**Key Functions:**
- `updateWeather()` - Fetch and display current weather
- `createDailyForecastItem()` - Template for daily forecast
- `createHourlyForecastItem()` - Template for hourly forecast
- `updateWeatherForecast()` - Fetch and render weather forecast

### Lines 241-352: RSS Feed Carousel
**What:** RSS feed display and navigation
**Key Functions:**
- `updateRSSFeeds()` - Fetch RSS feeds from server
- `renderRSSCarousel()` - Render RSS carousel with navigation
- `nextRSSItem()`, `prevRSSItem()` - Navigation
- `startRSSAutoRotate()`, `resetRSSAutoRotate()` - Auto-rotation

### Lines 353-428: Search and Tracking
**What:** Search functionality and event tracking
**Key Functions:**
- `checkForReload()` - Check for configuration changes
- `handleSearch()` - Handle search form submission
- `saveSearchHistory()` - Save to localStorage
- `trackEvent()` - Send analytics to server

### Lines 429-770: System Stats Sidebar
**What:** Real-time system statistics display
**Key Functions:**
- `toggleSystemStats()` - Show/hide stats sidebar
- `setStatsPosition()` - Position sidebar (left/right/top/bottom)
- `updateSystemStats()` - Fetch and update system stats
- `updateStatBar()` - Update progress bars
- `updateSparkline()` - Update sparkline charts
- `formatUptime()` - Format uptime string

### Lines 771-920: Edit Mode Core
**What:** Core edit mode functionality
**Key Functions:**
- `toggleEditMode()` - Toggle between view and edit mode
- `loadConfig()` - Load configuration from server
- `fetchMissingFavicons()` - Auto-fetch missing icons
- `saveAndExit()` - Save configuration and exit
- `getCategoryFromElement()` - Helper to get category data
- `fetchAndCacheFavicon()` - Fetch favicon via proxy

### Lines 921-1098: Edit Mode Templates
**What:** HTML generation for edit mode
**Key Functions:**
- `saveLinkToConfig()` - Save link to configuration
- `createLinkIconHTML()` - Generate icon HTML
- `createLinkItemHTML()` - Generate link item HTML
- `createLinksListHTML()` - Generate links list
- `createSubcategoryHTML()` - Generate subcategory HTML
- `createCategoryHTML()` - Generate category HTML
- `updateCategoryDisplay()` - Rebuild entire display from config

### Lines 1099-1430: Edit Mode Modals
**What:** Add/Edit/Delete operations for categories, subcategories, links
**Key Functions:**
- `addCategory()`, `editCategory()`, `deleteCategory()`
- `addSubcategory()`, `editSubcategory()`, `deleteSubcategory()`
- `addLink()`, `editLink()`, `deleteLink()`
- `closeModal()` - Close edit modal
- `showConfirmDialog()`, `closeConfirmModal()` - Confirmation dialogs

### Lines 1431-2020: Drag and Drop
**What:** Drag and drop functionality for reordering
**Sections:**
- **Widget Dragging** (1431-1560): Reorder widgets
  - `enableWidgetDragging()`, `disableWidgetDragging()`
  - `handleDragStart()`, `handleDrop()`, etc.
  - `updateWidgetOrder()`, `loadWidgetOrder()`
  
- **Category Dragging** (1609-1726): Reorder categories
  - `enableCategoryDragging()`, `disableCategoryDragging()`
  - `handleCategoryDragStart()`, `handleCategoryDrop()`, etc.
  - `updateCategoryOrder()`
  
- **Link Dragging** (1727-1871): Reorder links
  - `enableLinkDragging()`, `disableLinkDragging()`
  - `handleLinkDragStart()`, `handleLinkDrop()`, etc.
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
