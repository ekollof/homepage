/**
 * Search functionality with multi-provider support
 */

import { SEARCH_URLS } from '../core/constants.js.j2';
import { trackEvent, saveSearchHistory } from '../core/utils.js';

/**
 * Handle search form submission
 * @param {Event} event - Form submit event
 */
export function handleSearch(event) {
    event.preventDefault();

    const searchInput = document.getElementById('searchInput');
    const searchProvider = document.getElementById('searchProvider');
    const query = searchInput.value.trim();

    if (!query) {
        return;
    }

    const baseUrl = SEARCH_URLS[searchProvider.value] || SEARCH_URLS['brave'];
    const searchUrl = baseUrl + encodeURIComponent(query);

    // Track search
    trackEvent('search', { provider: searchProvider.value, query: query });

    window.open(searchUrl, '_blank', 'noopener,noreferrer');
    
    // Save to search history
    saveSearchHistory(query, searchProvider.value);
    searchInput.value = '';
}

/**
 * Initialize search functionality
 */
export function initializeSearch() {
    const searchForm = document.querySelector('.search-bar form');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
}
