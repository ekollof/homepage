/**
 * File change detection and auto-reload
 */

import { RELOAD_INTERVAL } from '../core/constants.js.j2';

/**
 * Check server for file changes and reload if needed
 */
export function checkForReload() {
    // Don't reload if in edit mode - user is actively editing
    if (window.editMode) {
        return;
    }
    
    fetch('/check_reload')
        .then(response => response.json())
        .then(data => {
            if (data.reload) {
                window.location.reload();
            }
        })
        .catch(error => console.error('Error checking for reload:', error));
}

/**
 * Initialize reload checker
 */
export function initializeReloadChecker() {
    setInterval(checkForReload, RELOAD_INTERVAL);
}
