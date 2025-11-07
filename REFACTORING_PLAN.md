# Homepage Refactoring Plan

## Current State Analysis

**File Sizes:**
- `app.py`: 1,302 lines (monolithic route handlers + utilities)
- `scripts.js.j2`: 1,784 lines (all JS in one file)
- `styles.css.j2`: 1,276 lines (all CSS in one file)
- `index.html.j2`: 410 lines (all HTML in one file)

**Problems:**
1. Single 1300+ line app.py with mixed concerns
2. Single 1800+ line JS file with all functionality
3. All HTML templates in one 400+ line file
4. Difficult to navigate and maintain
5. Hard to test individual components

---

## Proposed Structure

### 1. Python Backend Refactoring

```
src/homepage/
├── __init__.py
├── app.py                  # Main Flask app (100-150 lines)
├── config.py              # ✅ Already good
├── metrics.py             # ✅ Already good
├── utils.py               # ✅ Already good
├── cli.py                 # ✅ Already good
├── routes/                # NEW: Route blueprints
│   ├── __init__.py
│   ├── core.py           # /, /health, /check_reload
│   ├── api.py            # /api/stats, /api/track
│   ├── weather.py        # /api/weather, /api/weather/forecast
│   ├── system_stats.py   # /api/system-stats
│   ├── rss.py            # /api/rss
│   ├── editing.py        # /api/config, /api/save-config
│   └── assets.py         # /wallpaper, /favicon, /styles.css, /scripts.js
├── services/              # NEW: Business logic
│   ├── __init__.py
│   ├── weather_service.py    # Weather API logic
│   ├── geoip_service.py      # GeoIP lookup logic
│   ├── rss_service.py        # RSS feed parsing
│   ├── system_stats_service.py  # System stats collection
│   └── favicon_service.py    # Favicon extraction
└── templates/             # Modular templates
    ├── base.html.j2          # Base layout
    ├── index.html.j2         # Main page (simplified)
    ├── components/           # NEW: Reusable components
    │   ├── header.html.j2    # Clock, date, search
    │   ├── weather.html.j2   # Weather widget
    │   ├── rss.html.j2       # RSS carousel
    │   ├── system_stats.html.j2  # System stats sidebar
    │   ├── links.html.j2     # Links container
    │   └── modals.html.j2    # Edit/confirm modals
    ├── static/               # NEW: Separate JS/CSS modules
    │   ├── js/
    │   │   ├── main.js.j2           # Entry point
    │   │   ├── clock.js.j2          # Clock/date functionality
    │   │   ├── weather.js.j2        # Weather updates
    │   │   ├── rss.js.j2            # RSS carousel
    │   │   ├── system-stats.js.j2   # System stats
    │   │   ├── search.js.j2         # Search handling
    │   │   ├── editing.js.j2        # Edit mode
    │   │   ├── keyboard.js.j2       # Keyboard shortcuts
    │   │   └── utils.js.j2          # Shared utilities
    │   └── css/
    │       ├── main.css.j2          # Base styles
    │       ├── layout.css.j2        # Grid/layout
    │       ├── components.css.j2    # Component styles
    │       ├── weather.css.j2       # Weather styles
    │       ├── rss.css.j2           # RSS styles
    │       ├── system-stats.css.j2  # System stats styles
    │       ├── editing.css.j2       # Edit mode styles
    │       └── responsive.css.j2    # Media queries
    ├── scripts.js.j2         # DEPRECATED: Combine modules
    └── styles.css.j2         # DEPRECATED: Combine modules
```

---

## Implementation Phases

### Phase 1: Backend Refactoring (Routes & Services)

**Goal:** Split app.py into blueprints and services

**Steps:**

1. **Create services layer** (business logic extraction)
   ```python
   # services/weather_service.py
   class WeatherService:
       def get_current_weather(lat, lon) -> dict
       def get_hourly_forecast(lat, lon) -> dict
       def get_daily_forecast(lat, lon) -> dict
   
   # services/system_stats_service.py
   class SystemStatsService:
       def get_stats() -> dict
   
   # services/rss_service.py
   class RSSService:
       def fetch_feeds(urls: list) -> list[dict]
   ```

2. **Create route blueprints** (HTTP layer)
   ```python
   # routes/weather.py
   from flask import Blueprint
   weather_bp = Blueprint('weather', __name__)
   
   @weather_bp.route('/api/weather')
   def get_weather():
       # Use WeatherService
   ```

3. **Refactor app.py**
   - Keep only: app initialization, blueprint registration, config
   - Move route handlers to blueprints
   - Move business logic to services
   - Target: ~100-150 lines

**Benefits:**
- Easier to test (services are pure functions)
- Clear separation of concerns
- Blueprints can be disabled via config
- Reusable services

---

### Phase 2: Frontend Refactoring (Templates)

**Goal:** Modularize HTML using Jinja2 includes

**Steps:**

1. **Create component templates**
   ```jinja
   {# templates/components/header.html.j2 #}
   <div class="header">
       <div class="clock" id="clock">00:00:00</div>
       <div class="date" id="date">Loading...</div>
       {% include 'components/search.html.j2' %}
   </div>
   ```

2. **Update index.html.j2**
   ```jinja
   {% extends 'base.html.j2' %}
   {% block content %}
       {% include 'components/header.html.j2' %}
       {% include 'components/weather.html.j2' %}
       {% include 'components/rss.html.j2' %}
       {% include 'components/system_stats.html.j2' %}
       {% include 'components/links.html.j2' %}
       {% include 'components/modals.html.j2' %}
   {% endblock %}
   ```

**Benefits:**
- Each widget in its own file
- Easy to find/edit specific components
- Conditional includes based on config
- Reusable across pages

---

### Phase 3: JavaScript Refactoring

**Goal:** Split JS into modules by feature

**Steps:**

1. **Create module structure**
   ```javascript
   // static/js/utils.js.j2
   const utils = {
       trackEvent: (type, data) => { ... },
       formatUptime: (seconds) => { ... }
   };
   
   // static/js/clock.js.j2
   const clockModule = {
       updateClock: () => { ... },
       updateDate: () => { ... },
       init: () => { 
           setInterval(clockModule.updateClock, 1000);
       }
   };
   
   // static/js/weather.js.j2
   const weatherModule = {
       updateWeather: () => { ... },
       updateForecast: () => { ... },
       init: () => { ... }
   };
   ```

2. **Create main.js.j2 entry point**
   ```javascript
   document.addEventListener('DOMContentLoaded', () => {
       clockModule.init();
       {% if config.ENABLE_WEATHER %}
       weatherModule.init();
       {% endif %}
       {% if config.ENABLE_RSS %}
       rssModule.init();
       {% endif %}
       {% if config.ENABLE_SYSTEM_STATS %}
       systemStatsModule.init();
       {% endif %}
       keyboardModule.init();
   });
   ```

3. **Update scripts.js.j2** (combine modules)
   ```jinja
   {% include 'static/js/utils.js.j2' %}
   {% include 'static/js/clock.js.j2' %}
   {% if config.ENABLE_WEATHER %}
   {% include 'static/js/weather.js.j2' %}
   {% endif %}
   ...
   {% include 'static/js/main.js.j2' %}
   ```

**Benefits:**
- Easy to find specific functionality
- Can disable modules via config
- Better organization
- Easier debugging

---

### Phase 4: CSS Refactoring

**Goal:** Split CSS by concern

**Steps:**

1. **Create CSS modules**
   ```css
   /* static/css/layout.css.j2 */
   .container { ... }
   .header { ... }
   
   /* static/css/components.css.j2 */
   .widget-wrapper { ... }
   .category { ... }
   
   /* static/css/weather.css.j2 */
   .weather { ... }
   .forecast-container { ... }
   ```

2. **Update styles.css.j2** (combine modules)
   ```jinja
   {% include 'static/css/main.css.j2' %}
   {% include 'static/css/layout.css.j2' %}
   {% include 'static/css/components.css.j2' %}
   {% if config.ENABLE_WEATHER %}
   {% include 'static/css/weather.css.j2' %}
   {% endif %}
   ...
   ```

---

## Migration Strategy

### Option A: Big Bang (Risky)
- Refactor everything at once
- High risk of breaking changes
- Fast if successful

### Option B: Incremental (Recommended)
1. **Week 1:** Backend refactoring
   - Create services/
   - Create routes/
   - Update app.py
   - Run all tests, ensure backward compatibility

2. **Week 2:** Template refactoring
   - Create templates/components/
   - Update index.html.j2 with includes
   - Test rendering

3. **Week 3:** JavaScript refactoring
   - Create static/js/
   - Split into modules
   - Update scripts.js.j2
   - Test all functionality

4. **Week 4:** CSS refactoring
   - Create static/css/
   - Split into modules
   - Update styles.css.j2
   - Test styling

### Option C: Hybrid (Best)
- Do backend refactoring first (Phase 1) - complete break
- Keep frontend monolithic for now
- Later, do frontend refactoring when bandwidth allows

---

## Testing Strategy

**Per Phase:**
1. Run existing tests after each change
2. Add new tests for services
3. Manual smoke testing
4. Git commit after each successful phase

**Rollback Plan:**
- Each phase is a separate branch
- Can rollback individual phases
- Keep old files as .deprecated until stable

---

## Breaking Changes to Avoid

1. **Don't change URL routes** - keep all `/api/*` paths
2. **Don't change config variable names** - maintain backward compat
3. **Don't change function signatures** used by templates
4. **Don't change CSS class names** used by JS

---

## Expected Benefits

### Code Quality
- **Maintainability:** Easier to find and fix bugs
- **Testability:** Pure services are easier to test
- **Readability:** Smaller files, clearer intent

### Developer Experience
- **Faster navigation:** Find code in seconds
- **Easier onboarding:** Clear structure for new contributors
- **Better IDE support:** Smaller files = better autocomplete

### Performance
- **Selective loading:** Only include needed modules
- **Better caching:** Browser can cache separate files
- **Lazy loading potential:** Load features on demand

---

## Estimated Effort

**Phase 1 (Backend):** 8-12 hours
**Phase 2 (Templates):** 4-6 hours  
**Phase 3 (JavaScript):** 6-8 hours
**Phase 4 (CSS):** 4-6 hours

**Total:** 22-32 hours of development + testing

---

## Next Steps

1. **Review this plan** - Get feedback
2. **Choose migration strategy** - Incremental recommended
3. **Start with Phase 1** - Backend is safest to refactor first
4. **Create feature branch** - `refactor/backend-services`
5. **Implement services layer** - Start with weather service
6. **Test thoroughly** - Ensure no regressions
7. **Merge and repeat** - Move to next phase

---

## Questions to Answer

1. Should we keep inline CSS/JS (current) or serve separate files?
   - **Current:** Everything inline (no HTTP requests, but large initial load)
   - **Proposed:** Modular but still combined at render time (best of both)

2. Should services be classes or modules?
   - **Classes:** Better for dependency injection, testing
   - **Modules:** Simpler, more Pythonic for stateless operations
   - **Recommendation:** Start with modules, convert to classes if needed

3. How to handle Jinja2 template variables in JS modules?
   - Keep using .j2 extension
   - Render at template time (current approach)
   - Alternatively: Expose config as JSON endpoint

4. Should we introduce a build step?
   - **No:** Keep simplicity, use Jinja2 includes
   - **Yes:** Use webpack/vite for real modules (more complex)
   - **Recommendation:** No build step initially, inline everything

---

## Success Criteria

✅ All existing tests pass
✅ No visual regressions
✅ All features work identically
✅ Files < 300 lines each
✅ Clear separation of concerns
✅ Documentation updated
✅ Code quality checks pass
