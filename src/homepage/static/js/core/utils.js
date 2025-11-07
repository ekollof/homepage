/**
 * Shared utility functions
 */

/**
 * Track event to server for metrics
 * @param {string} eventType - Type of event (search, link_click, etc.)
 * @param {object} data - Event data
 */
export function trackEvent(eventType, data) {
    fetch('/api/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: eventType, data: data, timestamp: Date.now() })
    }).catch(() => {}); // Silently fail
}

/**
 * Save search query to local storage history
 * @param {string} query - Search query
 * @param {string} provider - Search provider used
 */
export function saveSearchHistory(query, provider) {
    try {
        let history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        history.unshift({ query, provider, timestamp: Date.now() });
        history = history.slice(0, 50); // Keep last 50 searches
        localStorage.setItem('searchHistory', JSON.stringify(history));
    } catch (e) {
        console.error('Failed to save search history:', e);
    }
}

/**
 * Format uptime seconds to human-readable string
 * @param {number} seconds - Uptime in seconds
 * @returns {string} Formatted uptime (e.g., "2d 5h 30m")
 */
export function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
}
