/**
 * Edit mode core functionality
 */

import { updateCategoryDisplay } from './category-editor.js';

export let editMode = false;
export let currentConfig = null;
export let editContext = null;

/**
 * Toggle edit mode on/off
 */
export function toggleEditMode() {
    editMode = !editMode;
    window.editMode = editMode; // Expose to window for other modules
    
    const container = document.getElementById('linksContainer');
    const widgetsContainer = document.getElementById('widgetsContainer');
    const toggle = document.getElementById('editToggle');
    const editIcon = document.getElementById('editIcon');
    const editText = document.getElementById('editText');

    if (editMode) {
        container.classList.add('edit-mode');
        if (widgetsContainer) {
            widgetsContainer.parentElement.classList.add('edit-mode');
            if (typeof window.enableWidgetDragging === 'function') {
                window.enableWidgetDragging();
            }
        }
        
        // Enable dragging from drag-drop module
        if (typeof window.enableCategoryDragging === 'function') window.enableCategoryDragging();
        if (typeof window.enableLinkDragging === 'function') window.enableLinkDragging();
        if (typeof window.enableSubcategoryDragging === 'function') window.enableSubcategoryDragging();
        
        toggle.classList.add('active');
        editIcon.textContent = '💾';
        editText.textContent = 'Save & Exit';
        loadConfig();
    } else {
        container.classList.remove('edit-mode');
        if (widgetsContainer) {
            widgetsContainer.parentElement.classList.remove('edit-mode');
            if (typeof window.disableWidgetDragging === 'function') {
                window.disableWidgetDragging();
            }
        }
        
        // Disable dragging
        if (typeof window.disableCategoryDragging === 'function') window.disableCategoryDragging();
        if (typeof window.disableLinkDragging === 'function') window.disableLinkDragging();
        if (typeof window.disableSubcategoryDragging === 'function') window.disableSubcategoryDragging();
        
        toggle.classList.remove('active');
        editIcon.textContent = '✏️';
        editText.textContent = 'Edit Mode';
        saveAndExit();
    }
}

/**
 * Load configuration from server
 */
export function loadConfig() {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            currentConfig = data;
            console.log('Configuration loaded', currentConfig);
            
            // Load widget order from config
            loadWidgetOrder();
            
            // Fetch and cache any missing favicons on load
            fetchMissingFavicons();
        })
        .catch(error => console.error('Failed to load config:', error));
}

/**
 * Fetch favicons for links with empty icons
 */
async function fetchMissingFavicons() {
    if (!currentConfig) return;
    
    const { fetchAndCacheFavicon } = await import('./favicon-service.js');
    let hasChanges = false;
    
    for (let catIndex = 0; catIndex < currentConfig.category.length; catIndex++) {
        const category = currentConfig.category[catIndex];
        
        // Check category links
        if (category.links) {
            for (let linkIndex = 0; linkIndex < category.links.length; linkIndex++) {
                const link = category.links[linkIndex];
                if (link.icon === '' || !link.icon) {
                    console.log('Fetching favicon for:', link.name);
                    try {
                        const faviconData = await fetchAndCacheFavicon(link.url);
                        link.icon = faviconData;
                        hasChanges = true;
                    } catch (error) {
                        console.error('Failed to fetch favicon for', link.name, error);
                    }
                }
            }
        }
        
        // Check subcategory links
        if (category.subcategory) {
            for (let subIndex = 0; subIndex < category.subcategory.length; subIndex++) {
                const subcategory = category.subcategory[subIndex];
                if (subcategory.links) {
                    for (let linkIndex = 0; linkIndex < subcategory.links.length; linkIndex++) {
                        const link = subcategory.links[linkIndex];
                        if (link.icon === '' || !link.icon) {
                            console.log('Fetching favicon for:', link.name);
                            try {
                                const faviconData = await fetchAndCacheFavicon(link.url);
                                link.icon = faviconData;
                                hasChanges = true;
                            } catch (error) {
                                console.error('Failed to fetch favicon for', link.name, error);
                            }
                        }
                    }
                }
            }
        }
    }
    
    // If we fetched any favicons, update the DOM
    if (hasChanges) {
        console.log('Favicons fetched, updating display');
        updateCategoryDisplay(currentConfig);
    }
}

/**
 * Save configuration and exit edit mode
 */
export function saveAndExit() {
    if (!currentConfig) return;

    // Show saving indicator
    const toggle = document.getElementById('editToggle');
    const originalText = toggle.innerHTML;
    toggle.innerHTML = '<span>💾</span><span>Saving...</span>';
    toggle.style.pointerEvents = 'none';

    fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentConfig)
    })
    .then(response => {
        if (!response.ok) throw new Error('Save failed');
        return response.json();
    })
    .then(() => {
        console.log('Configuration saved');
        // Add cache-busting parameter to force reload
        setTimeout(() => {
            window.location.href = window.location.pathname + '?t=' + Date.now();
        }, 500);
    })
    .catch(error => {
        console.error('Failed to save config:', error);
        alert('Failed to save configuration. Please try again.');
        toggle.innerHTML = originalText;
        toggle.style.pointerEvents = 'auto';
    });
}

/**
 * Load widget order from configuration
 */
function loadWidgetOrder() {
    // Load from config instead of localStorage
    if (!currentConfig || !currentConfig.widget_order) return;
    
    try {
        const order = currentConfig.widget_order;
        const widgetsContainer = document.getElementById('widgetsContainer');
        if (!widgetsContainer) return;
        
        order.forEach(widgetName => {
            const widget = widgetsContainer.querySelector(`[data-widget="${widgetName}"]`);
            if (widget) {
                widgetsContainer.appendChild(widget);
            }
        });
    } catch (e) {
        console.error('Failed to load widget order:', e);
    }
}

/**
 * Get current config (for other modules)
 */
export function getConfig() {
    return currentConfig;
}

/**
 * Set current config (for other modules)
 */
export function setConfig(config) {
    currentConfig = config;
}

/**
 * Get edit context
 */
export function getEditContext() {
    return editContext;
}

/**
 * Set edit context
 */
export function setEditContext(context) {
    editContext = context;
}

// Expose toggle to window for onclick handlers
window.toggleEditMode = toggleEditMode;

// Add 'e' keyboard shortcut for edit mode
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'e' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        toggleEditMode();
    }
});
