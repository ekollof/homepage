/**
 * Favicon fetching and caching service
 */

/**
 * Fetch and cache favicon from URL
 * @param {string} url - Website URL
 * @returns {Promise<string>} Base64 encoded favicon data URI
 */
export async function fetchAndCacheFavicon(url) {
    try {
        // Use our proxy endpoint to avoid CORS issues
        const response = await fetch(`/api/favicon?url=${encodeURIComponent(url)}`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch favicon');
        }
        
        const data = await response.json();
        return data.favicon;
    } catch (error) {
        console.error('Error fetching favicon:', error);
        throw error;
    }
}
