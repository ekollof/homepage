# Homepage Feature Ideas

This document contains feature ideas that leverage the modularized JavaScript architecture and WebSocket infrastructure.

Last updated: 2024-11-10

---

## 🔥 High Impact Features (Leverage WebSocket Real-Time)

### 1. 📱 Live Activity Feed

**Module:** `12-activity-feed.js.j2`

**Description:**
- Show real-time events across the homepage
- Display activities like "User searched for Python", "Weather updated", "New RSS item"
- WebSocket broadcasts all user actions
- Optional per-user privacy settings
- Useful for: Family dashboards, team spaces

**Implementation:**
- Estimated: ~150 lines
- Dependencies: WebSocket already streams events
- Complexity: Medium

---

### 2. 🔔 Smart Notifications

**Module:** `12-notifications.js.j2`

**Description:**
- Browser notifications for RSS keywords (e.g., "Python", "Security")
- System alert thresholds (CPU > 90%, Disk > 95%)
- Weather alerts (rain, temperature drops)
- Customizable per-user notification rules
- Notification history and management

**Implementation:**
- Estimated: ~200 lines
- Dependencies: Uses existing WebSocket events, Browser Notification API
- Complexity: Medium

**Backend Support:**
- Add notification rules to config
- Filter RSS items by keywords
- Check system stats against thresholds
- Emit WebSocket events for alerts

---

### 3. 💬 Quick Notes / Scratchpad

**Module:** `12-notes.js.j2`

**Description:**
- Floating notepad widget (like sticky notes)
- Real-time sync across devices via WebSocket
- Markdown support with preview
- Auto-save functionality
- Perfect for: Quick reminders, shopping lists, todo items

**Implementation:**
- Estimated: ~250 lines
- Dependencies: Drag/drop already exists, markdown parser (~50KB)
- Complexity: Medium

**Backend Support:**
- `/api/notes` endpoints (GET, POST, PUT, DELETE)
- Store notes in JSON file or database
- WebSocket events for note changes

---

### 4. 🎯 Pinned Items

**Module:** `12-pinned.js.j2`

**Description:**
- Pin frequently used links to top bar
- Right-click any link → "Pin to top"
- Real-time sync when pins change
- Cross-device synchronization
- Maximum 5-10 pinned items

**Implementation:**
- Estimated: ~150 lines
- Dependencies: Reuses edit mode code
- Complexity: Low-Medium

**Backend Support:**
- Store pinned links in separate config section
- WebSocket broadcast on pin/unpin

---

### 5. 📊 Live Charts (System Stats History)

**Module:** `12-charts.js.j2`

**Description:**
- Real-time line charts for CPU/Memory/Network
- 24-hour history graphs with time axis
- Click to zoom, export data as CSV/PNG
- Configurable time ranges (1h, 6h, 24h, 7d)
- Uses existing sparkline code, enhanced

**Implementation:**
- Estimated: ~300 lines
- Dependencies: Chart.js (~200KB, cache locally), existing system stats
- Complexity: Medium-High

**Backend Support:**
- Store historical data (ring buffer, 24h+)
- `/api/system-stats/history` endpoint
- Configurable retention period

---

## 🎨 Medium Impact Features (UI/UX Enhancements)

### 6. 🎨 Theme Switcher

**Module:** `12-themes.js.j2`

**Description:**
- Multiple color schemes (Gruvbox, Dracula, Nord, Solarized, Catppuccin)
- Live preview without reload
- Per-device theme preferences (localStorage)
- Auto dark/light mode based on time of day
- Custom theme creator

**Implementation:**
- Estimated: ~200 lines
- Dependencies: CSS variables already in use
- Complexity: Low-Medium

**Backend Support:**
- Serve theme JSON files
- Optional: Save user theme preference

---

### 7. 🔍 Global Search

**Module:** `12-global-search.js.j2`

**Description:**
- Fuzzy search across ALL links (not just web search)
- Keyboard shortcut (Ctrl+K or Cmd+K)
- Recent searches, autocomplete
- Search in link titles, URLs, categories
- Search result highlighting

**Implementation:**
- Estimated: ~250 lines
- Dependencies: Fuse.js for fuzzy search (~25KB), existing link data
- Complexity: Medium

**Features:**
- Type-ahead suggestions
- Search history (localStorage)
- Navigate results with arrow keys
- Enter to open, Esc to close

---

### 8. 📌 Custom Widgets

**Module:** `12-widget-store.js.j2`

**Description:**
- Widget marketplace/library
- Available widgets:
  - Calculator
  - Unit Converter
  - Timer/Stopwatch
  - Pomodoro Timer
  - Currency Converter
  - World Clocks
- Drag to reorder (already implemented)
- Enable/disable widgets

**Implementation:**
- Estimated: ~200 lines per widget
- Dependencies: Widget-specific APIs (e.g., currency rates)
- Complexity: Medium (varies per widget)

**Architecture:**
- Plugin system for widgets
- Each widget is a self-contained module
- Widget registry and discovery

---

### 9. 🗂️ Link Tags/Labels

**Module:** Enhancement to existing edit modules

**Description:**
- Tag links (e.g., "work", "personal", "urgent", "favorites")
- Filter links by tags
- Tag-based search
- Color-coded tags with customizable colors
- Multiple tags per link

**Implementation:**
- Estimated: ~150 lines
- Dependencies: Extend existing config format
- Complexity: Low-Medium

**Config Changes:**
```toml
[[category.links]]
name = "GitHub"
url = "https://github.com"
tags = ["work", "code", "important"]
```

---

### 10. 📱 Mobile Gestures

**Module:** `12-touch-gestures.js.j2`

**Description:**
- Swipe to navigate categories (left/right)
- Pull-to-refresh for weather/RSS
- Long-press for context menu
- Touch-optimized edit mode
- Pinch to zoom categories

**Implementation:**
- Estimated: ~200 lines
- Dependencies: Hammer.js (~30KB) or native touch events
- Complexity: Medium

**Mobile Optimizations:**
- Larger touch targets
- Bottom navigation bar
- Swipe gestures for common actions

---

## 🚀 Advanced Features (Data & Integration)

### 11. 🔗 Link Analytics

**Module:** `12-analytics.js.j2`

**Description:**
- Click heatmap (most used links)
- Usage patterns (hourly/daily/weekly)
- Link suggestions based on patterns
- Export reports (CSV, JSON)
- Privacy-focused (all local data)

**Implementation:**
- Estimated: ~250 lines
- Dependencies: Uses existing metrics system
- Complexity: Medium

**Features:**
- Top 10 most clicked links
- Usage by time of day
- Unused link detection
- Link recommendation engine

---

### 12. 🌐 Multi-User Support

**Module:** `12-users.js.j2`

**Description:**
- User profiles with separate link sets
- Share links between users
- Per-user themes and settings
- WebSocket broadcasts user presence
- User switching without logout

**Implementation:**
- Estimated: ~400 lines
- Dependencies: Backend authentication system
- Complexity: High

**Backend Changes:**
- User authentication (sessions or JWT)
- Per-user config files
- Shared links collection
- User presence tracking

---

### 13. 🔄 Sync with Browser Bookmarks

**Module:** `12-bookmark-sync.js.j2`

**Description:**
- Import Chrome/Firefox bookmarks
- Export links as bookmarks HTML
- Two-way sync option (advanced)
- Bookmark folder mapping to categories
- Duplicate detection

**Implementation:**
- Estimated: ~300 lines
- Dependencies: FileReader API, browser bookmark format parsers
- Complexity: Medium-High

**Features:**
- Drag & drop bookmark HTML file
- Map bookmark folders to categories
- Selective import (choose folders)
- Export with folder structure

---

### 14. 🤖 AI Link Suggestions

**Module:** `12-ai-suggestions.js.j2`

**Description:**
- Suggest links based on usage patterns
- Auto-categorization of new links
- Duplicate link detection
- Similar link recommendations
- All processing done locally (no external API)

**Implementation:**
- Estimated: ~200 lines
- Dependencies: Simple ML algorithms (no libraries)
- Complexity: Medium

**Algorithms:**
- TF-IDF for text similarity
- Cosine similarity for recommendations
- Simple clustering for auto-categorization
- Pattern matching for duplicates

---

### 15. 🎮 Keyboard Shortcuts Everywhere

**Module:** `12-shortcuts.js.j2`

**Description:**
- Vim-style navigation (j/k for up/down, h/l for left/right)
- Custom keyboard shortcuts for any action
- Shortcut recorder/editor
- Cheat sheet overlay (?)
- Import/export shortcut profiles

**Implementation:**
- Estimated: ~200 lines
- Dependencies: Mousetrap.js (~20KB) or native KeyboardEvent
- Complexity: Medium

**Default Shortcuts:**
- `/` - Focus search
- `?` - Show help
- `e` - Toggle edit mode
- `Ctrl+K` - Global search
- `j/k` - Navigate links
- `Enter` - Open link
- `Esc` - Close modals

---

## 🎁 Quick Win Features (Easy to Implement)

### 16. 🎲 Random Link

**Description:**
- "I'm feeling lucky" button
- Opens random link from favorites/all links
- Weighted by usage (more used = higher probability)
- Keyboard shortcut support

**Implementation:**
- Estimated: ~20 lines
- Complexity: Very Low

**Location:** Add to search bar or top buttons

---

### 17. 🔗 QR Code Generator

**Description:**
- Right-click link → "Generate QR code"
- Share links to mobile easily
- Copy QR code as image
- Print QR codes

**Implementation:**
- Estimated: ~50 lines
- Dependencies: qrcode.js (~30KB, cache locally)
- Complexity: Very Low

**UI:**
- Context menu option
- Modal with QR code display
- Download/print options

---

### 18. 📋 Clipboard History

**Description:**
- Track copied links from homepage
- Quick paste from history
- Search clipboard history
- Maximum 50 items

**Implementation:**
- Estimated: ~100 lines
- Dependencies: Clipboard API, localStorage
- Complexity: Low

**Features:**
- Copy link URL on click
- View history in sidebar
- Clear history option

---

### 19. ⏱️ Time Tracking

**Description:**
- Track time spent on different sites
- Daily/weekly reports
- Productivity insights
- Export time logs

**Implementation:**
- Estimated: ~150 lines
- Dependencies: localStorage, idle detection
- Complexity: Low-Medium

**Features:**
- Automatic tracking when link opened
- Idle time detection (5 min threshold)
- Daily summaries
- Privacy-focused (all local)

---

### 20. 🎵 Background Music/Sounds

**Description:**
- Ambient sounds while browsing homepage
- Focus timer sounds (Pomodoro)
- White noise, rain, coffee shop, etc.
- Volume control

**Implementation:**
- Estimated: ~100 lines
- Dependencies: Web Audio API, sound files (~1-5MB)
- Complexity: Low

**Sounds:**
- Rain
- Ocean waves
- Coffee shop
- Forest
- White/Pink noise
- Focus timer bell

---

## 🏆 Top 3 Recommended Features

Based on impact, effort, and synergy with existing features:

### 🥇 #1: Smart Notifications

**Why:**
- Leverages existing WebSocket infrastructure perfectly
- Adds real value with minimal effort
- Makes RSS and system stats more useful
- Users get actionable alerts

**Effort:** Medium (~200 lines)  
**Impact:** High  
**Priority:** ⭐⭐⭐⭐⭐

---

### 🥈 #2: Global Search

**Why:**
- Dramatically improves usability
- Solves "where is that link?" problem
- Fast fuzzy search feels modern
- Keyboard-first UX

**Effort:** Medium (~250 lines)  
**Impact:** High  
**Priority:** ⭐⭐⭐⭐⭐

---

### 🥉 #3: Live Charts

**Why:**
- Makes system stats actually useful
- Visual feedback is engaging
- Historical data adds value
- Shows off WebSocket capabilities

**Effort:** Medium (~300 lines)  
**Impact:** Medium-High  
**Priority:** ⭐⭐⭐⭐

---

## Implementation Notes

### Module Architecture

All new features should follow the established module pattern:

```javascript
/**
 * Module: Feature Name
 * Description of what this module does
 */

{% if config.ENABLE_FEATURE_NAME %}
// Feature state variables
let featureState = null;

/**
 * Initialize feature
 */
function initFeature() {
    // Implementation
}

// Feature functions...

{% endif %}
```

### WebSocket Integration

New features using WebSocket should:

1. Listen for events in Module 11 (initialization)
2. Emit events via existing `wsClient.emit()`
3. Handle connection/disconnection gracefully
4. Fall back to polling when WebSocket unavailable

### Configuration

New features should:

1. Add `ENABLE_FEATURE_NAME` to config.py
2. Add feature-specific settings if needed
3. Respect feature flags (can be disabled)
4. Provide sensible defaults

### Testing

Each new feature should have:

1. Unit tests for core functions
2. Integration tests for WebSocket events
3. E2E tests for user interactions
4. Performance tests for heavy features

---

## Contributing

To propose a new feature:

1. Create an issue with the feature template
2. Discuss implementation approach
3. Prototype in a new module
4. Submit PR with tests and documentation

For questions about these features, see:
- `docs/JAVASCRIPT_GUIDE.md` - Code organization
- `src/homepage/static/js/modules/README.md` - Module system

---

*This document is a living reference. Features can be added, removed, or reprioritized based on user feedback and development capacity.*
