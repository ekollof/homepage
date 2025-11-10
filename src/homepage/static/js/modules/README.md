# JavaScript Modules

## Overview

This directory contains modular JavaScript source files that are combined into the single `scripts.js.j2` template used by the application.

## Current Status

**Partial Implementation** - Infrastructure is in place, but most code remains in the monolithic `scripts.js.j2` file.

## Structure

Modules are named with numeric prefixes to control load order:

```
01-constants-and-cache.js.j2  - Constants and DOM caching (CREATED)
02-clock.js.j2                 - Clock and date functions (CREATED)
03-weather.js.j2               - Weather and forecast (TODO)
04-rss.js.j2                   - RSS feed carousel (TODO)
05-search.js.j2                - Search and tracking (TODO)
06-system-stats.js.j2          - System stats sidebar (TODO)
07-edit-mode-core.js.j2        - Edit mode core (TODO)
08-edit-templates.js.j2        - HTML templates (TODO)
09-edit-modals.js.j2           - Add/Edit/Delete modals (TODO)
10-drag-drop.js.j2             - Drag and drop (TODO)
11-initialization.js.j2        - Init and WebSocket (TODO)
```

## Usage

### Building from Modules

```bash
# Combine all modules into scripts.js.j2
make build-js
```

This runs `scripts/build_js.py` which:
1. Reads all `[0-9][0-9]-*.js.j2` files in order
2. Combines them into a single file
3. Adds proper indentation for Jinja2 template
4. Writes to `src/homepage/templates/scripts.js.j2`

### Creating a New Module

1. **Create the file** with numeric prefix:
   ```bash
   touch src/homepage/static/js/modules/12-my-feature.js.j2
   ```

2. **Write your code** (Jinja2 syntax supported):
   ```javascript
   /**
    * Module: My Feature
    * Description of what this module does
    */
   
   {% if config.ENABLE_MY_FEATURE %}
   function myFeatureFunction() {
       // Your code here
   }
   {% endif %}
   ```

3. **Rebuild**:
   ```bash
   make build-js
   ```

4. **Test**:
   ```bash
   make lint-js
   make check-all
   ```

### Module Guidelines

#### Naming Convention

- Use `XX-feature-name.js.j2` format
- `XX` = two-digit load order (01-99)
- Use kebab-case for feature name
- Extension must be `.js.j2` (Jinja2 template)

#### Dependencies

Modules are loaded in numeric order. If your module depends on another:
- Give it a higher number
- Document dependencies in module header

Example:
```javascript
/**
 * Module: RSS Feed
 * Dependencies: 01-constants-and-cache.js.j2 (DOM object)
 */
```

#### Shared State

Modules share global scope. Available from earlier modules:
- `DOM` - Cached DOM elements
- `CSS_CLASSES` - CSS class constants
- `CLOCK_FORMAT`, `RELOAD_INTERVAL` - Config constants

#### Jinja2 Variables

All Jinja2 variables from the template context are available:
- `{{ config.FEATURE_NAME }}` - Configuration values
- `{% if config.ENABLE_X %}` - Conditional inclusion

## Migration Strategy

The full codebase isn't modularized yet. You have two options:

### Option 1: Incremental Migration

1. Keep existing `scripts.js.j2` as-is
2. New features go into modules
3. Gradually extract existing features when editing them

### Option 2: Full Split

1. Use line numbers from `docs/JAVASCRIPT_GUIDE.md`
2. Extract each section into a module
3. Test thoroughly after each extraction

**Recommendation:** Start with Option 1 (safer).

## Example: Adding a New Feature

Let's add a "dark mode toggle" feature:

```bash
# 1. Create module
cat > src/homepage/static/js/modules/12-dark-mode.js.j2 << 'EOF'
/**
 * Module: Dark Mode Toggle
 * Handles dark/light theme switching
 */

{% if config.ENABLE_DARK_MODE %}
/**
 * Toggle dark mode on/off
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
}

// Initialize dark mode from localStorage
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
{% endif %}
EOF

# 2. Build
make build-js

# 3. Test
make lint-js

# 4. Run app
make run
```

## Troubleshooting

### Build Fails

```bash
# Check if all modules are valid JavaScript
for f in src/homepage/static/js/modules/*.js.j2; do
    echo "Checking $f..."
    # Render and check syntax (basic)
    head -5 "$f"
done
```

### Module Not Included

- Check filename matches `[0-9][0-9]-*.js.j2` pattern
- Rebuild: `make build-js`
- Check build script output for errors

### Load Order Issues

If a module uses undefined variables:
1. Check which module defines that variable
2. Ensure your module has a higher number
3. Rebuild and test

## Build Script

The build script (`scripts/build_js.py`) is simple:

```python
# Pseudocode:
1. Find all modules in numeric order
2. For each module:
   - Add module header comment
   - Append module content
   - Add blank line
3. Write combined output with indentation
```

See `scripts/build_js.py` for implementation.

## Integration

### Makefile Targets

- `make build-js` - Build JavaScript from modules
- `make lint-js` - Lint the built JavaScript
- `make check-all` - Full checks (Python + JavaScript)

### Git Workflow

```bash
# 1. Edit module
vim src/homepage/static/js/modules/05-search.js.j2

# 2. Build
make build-js

# 3. Test
make lint-js

# 4. Commit BOTH module and built file
git add src/homepage/static/js/modules/05-search.js.j2
git add src/homepage/templates/scripts.js.j2
git commit -m "feat: update search functionality"
```

## Future Enhancements

Potential improvements to the module system:

1. **Source maps** - Track which module each line comes from
2. **Auto-rebuild** - Watch modules and auto-rebuild on change
3. **Module linting** - Lint individual modules before combining
4. **Dependency validation** - Check that dependencies are met
5. **Hot reload** - Reload modules in browser without full page refresh

## Questions?

See also:
- `docs/JAVASCRIPT_GUIDE.md` - Code organization guide
- `scripts/build_js.py` - Build script implementation
- `Makefile` - Build targets
