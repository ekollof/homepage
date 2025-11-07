/**
 * Main initialization module
 * Imports and initializes all features based on configuration
 */

import { ENABLE_WEATHER, ENABLE_RSS, ENABLE_SYSTEM_STATS } from './constants.js.j2';
import { initializeClock } from '../widgets/clock.js';
import { initializeWeather } from '../widgets/weather.js';
import { initializeRSS } from '../widgets/rss.js';
import { initializeSystemStats } from '../widgets/system-stats.js';
import { initializeSearch } from '../features/search.js';
import { initializeKeyboardShortcuts } from '../features/keyboard.js';
import { initializeReloadChecker } from '../features/reload-checker.js';
import { initializeModals } from '../editing/modal-manager.js';
import { trackEvent } from './utils.js';

/**
 * Initialize all application features
 */
function initializeApp() {
    // Core widgets (always enabled)
    initializeClock();
    
    // Optional widgets
    if (ENABLE_WEATHER) {
        initializeWeather();
    }
    
    if (ENABLE_RSS) {
        initializeRSS();
    }
    
    if (ENABLE_SYSTEM_STATS) {
        initializeSystemStats();
    }
    
    // Features
    initializeSearch();
    initializeKeyboardShortcuts();
    initializeReloadChecker();
    
    // Modals (for help overlay and editing)
    initializeModals();
    
    // Track link clicks
    document.querySelectorAll('.link-item a').forEach(link => {
        link.addEventListener('click', (e) => {
            trackEvent('link_click', { 
                name: e.currentTarget.dataset.link,
                url: e.currentTarget.href 
            });
        });
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
