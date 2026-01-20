# Link Editing Feature

The Homepage application includes an in-browser editing mode that allows you to manage your links without manually editing TOML files.

## Overview

The editing feature creates a `links.override.toml` file in your project directory that completely replaces the default `links.toml` when present. This allows you to:
- Keep private links without modifying the tracked configuration
- Delete or modify any links from the base configuration
- Easily reset to defaults by deleting the override file

**How it works:**
- **First edit**: Base config is automatically copied to `links.override.toml`
- **Subsequent edits**: All changes save to override file
- **If override exists**: Override is used exclusively (base is ignored)
- **If override doesn't exist**: Base config is used

**Important:** The `links.override.toml` file is automatically added to `.gitignore` to prevent accidentally committing private links.

## Enabling/Disabling

Edit mode is **enabled by default**. To disable it:

```bash
export HOMEPAGE_ENABLE_EDITING=False
# OR set in .env file:
HOMEPAGE_ENABLE_EDITING=False
```

## Using Edit Mode

### Activating Edit Mode

There are two ways to enter edit mode:
1. Click the **"Edit Mode"** button in the top-right corner
2. Press the `e` key on your keyboard

When active, the button changes to **"Save & Exit"** and categories show edit controls.

### Adding Content

**Add a Category:**
1. Enter edit mode
2. Scroll to the bottom of the page
3. Click **"+ Add Category"**
4. Fill in the form:
   - **Name:** Category display name (e.g., "Development")
   - **Icon:** Emoji to display (e.g., "💻")
5. Click **Save**

**Add a Subcategory:**
1. Enter edit mode
2. Find the parent category
3. Click **"+ Subcategory"** in the category's edit controls
4. Fill in name and icon
5. Click **Save**

**Add a Link:**
1. Enter edit mode
2. Find the category or subcategory where you want to add the link
3. Click **"+ Link"** in the appropriate edit controls
4. Fill in the form:
   - **Name:** Link display name (e.g., "GitHub")
   - **URL:** Full URL including `https://` (e.g., "https://github.com")
   - **Icon:** Emoji to display (e.g., "🔗")
5. Click **Save**

### Editing Content

**Edit a Category or Subcategory:**

1. Enter edit mode
2. Click **"Edit Category"** or **"Edit Subcategory"**
3. Modify the name or icon
4. Click **Save**

**Edit a Link:**

1. Enter edit mode
2. Hover over the link you want to edit
3. Click the **"Edit"** button that appears next to the link
4. Modify the name, URL, or icon
5. Click **Save**

### Deleting Content

**Delete a Category:**

1. Enter edit mode
2. Click **"Delete"** in the category's edit controls
3. Confirm the deletion

**Warning:** Deleting a category removes all its links and subcategories.

**Delete a Subcategory:**

1. Enter edit mode
2. Click **"Delete"** in the subcategory's edit controls
3. Confirm the deletion

**Warning:** Deleting a subcategory removes all its links.

**Delete a Link:**

1. Enter edit mode
2. Hover over the link you want to delete
3. Click the **"×"** button that appears next to the link
4. Confirm the deletion

### Saving Changes

When you exit edit mode, your changes are automatically saved to `links.override.toml`:
1. Click **"Save & Exit"** button (or press `e` again)
2. The application saves your configuration
3. The page reloads with your changes

## Configuration Merging

The app uses a simple override strategy:

1. **If override exists**: Use `links.override.toml` exclusively (ignore base)
2. **If override doesn't exist**: Use `links.toml` (base configuration)

This means:
- You have **full control** - can delete anything from base
- Changes are **isolated** - base file never modified
- Reset is **simple** - just delete override file

### First Edit Behavior

When you first enter edit mode and request the configuration:

1. App checks if `links.override.toml` exists
2. If not, copies `links.toml` → `links.override.toml`
3. Returns the override file content for editing
4. All subsequent saves update override file only

### Example

**links.toml (base - tracked in git):**
```toml
[[category]]
name = "Development"
icon = "💻"
  [[category.links]]
  name = "GitHub"
  url = "https://github.com"
  
  [[category.links]]
  name = "GitLab"
  url = "https://gitlab.com"
```

**After first edit, links.override.toml is created with same content**

**After you delete GitLab and add private link:**
```toml
[[category]]
name = "Development"
icon = "💻"
  [[category.links]]
  name = "GitHub"
  url = "https://github.com"
  
  [[category.links]]
  name = "Internal Server"
  url = "https://internal.company.com"
```

**Result:**
- Base file unchanged (still has GitLab)
- Override file has your changes (GitLab deleted, internal link added)
- App uses override exclusively
- GitLab link is hidden from your view

## Resetting Configuration

To reset to the default configuration:

### Option 1: Via File System
```bash
rm links.override.toml
```

### Option 2: Via API (for advanced users)
```bash
curl -X POST http://localhost:5000/api/config/reset
```

After resetting, reload the page to see the original `links.toml` configuration.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `e` | Toggle edit mode |
| `Esc` | Close modal dialogs |

## Troubleshooting

### Changes not saving

1. Check that `HOMEPAGE_ENABLE_EDITING` is `True`
2. Verify the application has write permissions in its directory
3. Check browser console for errors (F12 → Console)
4. Look for errors in application logs

### Override file corrupted

If `links.override.toml` becomes corrupted:

1. Stop the application
2. Delete or rename `links.override.toml`
3. Restart the application
4. Re-enter your customizations

### Lost all changes

Check if `links.override.toml` exists and contains your data. If you accidentally committed it to git:

```bash
# Remove from git but keep local file
git rm --cached links.override.toml
git commit -m "Remove override file from tracking"
```

## Technical Details

### File Format

The override file uses the same TOML format as `links.toml`. It's written using the `tomli-w` library.

### API Endpoints

- `GET /api/config` - Retrieve merged configuration
- `POST /api/config` - Save configuration to override file
- `POST /api/config/reset` - Delete override file

All endpoints require `HOMEPAGE_ENABLE_EDITING=True`.

### File Watching

The application watches for changes to both `links.toml` and `links.override.toml`. When either file changes, the page automatically reloads to show the updated configuration.

## Security Considerations

1. **Private Links:** The override file is gitignored by default to prevent exposing private URLs
2. **No Authentication:** Edit mode has no authentication - anyone with access to the page can edit
3. **Validation:** The application validates TOML structure but not link content
4. **Backups:** Consider backing up `links.override.toml` regularly if it contains important links

## Best Practices

1. **Keep base config clean:** Use `links.toml` for common/public links shared across installations
2. **Use override for personalization:** Add machine-specific or private links to override
3. **Version control:** Commit `links.toml` but never commit `links.override.toml`
4. **Backup regularly:** Save your override file before major changes
5. **Test changes:** Preview your configuration with `cli.py validate` before committing base changes

## See Also

- [Configuration Guide](USAGE.html#configuration)
- [CLI Tools](USAGE.html#cli-tool)
- [API Documentation](API.md)
