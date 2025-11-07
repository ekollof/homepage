/**
 * RSS feed carousel widget
 */

let rssItems = [];
let currentRSSIndex = 0;
let rssAutoRotate = null;

/**
 * Fetch RSS feeds from server
 */
export function updateRSSFeeds() {
    const rssElement = document.getElementById('rssWidget');
    if (!rssElement) return;

    fetch('/api/rss')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error || !data.items || data.items.length === 0) {
                rssElement.innerHTML = `<div class="rss-error">No RSS items available</div>`;
                return;
            }

            rssItems = data.items;
            currentRSSIndex = 0;
            renderRSSCarousel();
            startRSSAutoRotate();
        })
        .catch(error => {
            rssElement.innerHTML = `<div class="rss-error">RSS feeds unavailable</div>`;
            console.warn('RSS fetch failed:', error.message);
        });
}

/**
 * Render RSS carousel with current items
 */
export function renderRSSCarousel() {
    const rssElement = document.getElementById('rssWidget');
    if (!rssElement || rssItems.length === 0) return;

    let html = `
        <div class="rss-title">
            <span>📰 Latest News</span>
            <div class="rss-nav">
                <button class="rss-nav-btn" onclick="window.prevRSSItem()" aria-label="Previous">‹</button>
                <span class="rss-counter">${currentRSSIndex + 1} / ${rssItems.length}</span>
                <button class="rss-nav-btn" onclick="window.nextRSSItem()" aria-label="Next">›</button>
            </div>
        </div>
        <div class="rss-carousel">
            <div class="rss-items" style="transform: translateX(-${currentRSSIndex * 100}%)">
    `;
    
    rssItems.forEach(item => {
        const date = item.published ? new Date(item.published).toLocaleDateString() : '';
        html += `
            <div class="rss-item">
                <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="rss-item-link">
                    ${item.title}
                </a>
                <div class="rss-item-meta">
                    <span class="rss-item-feed">${item.feed_title}</span>
                    ${date ? `<span class="rss-item-date">${date}</span>` : ''}
                </div>
                ${item.description ? `<div class="rss-item-description">${item.description}</div>` : ''}
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    rssElement.innerHTML = html;
}

/**
 * Navigate to next RSS item
 */
export function nextRSSItem() {
    if (rssItems.length === 0) return;
    currentRSSIndex = (currentRSSIndex + 1) % rssItems.length;
    renderRSSCarousel();
    resetRSSAutoRotate();
}

/**
 * Navigate to previous RSS item
 */
export function prevRSSItem() {
    if (rssItems.length === 0) return;
    currentRSSIndex = (currentRSSIndex - 1 + rssItems.length) % rssItems.length;
    renderRSSCarousel();
    resetRSSAutoRotate();
}

/**
 * Start automatic rotation timer
 */
function startRSSAutoRotate() {
    if (rssAutoRotate) clearInterval(rssAutoRotate);
    rssAutoRotate = setInterval(() => {
        nextRSSItem();
    }, 30000); // 30 seconds
}

/**
 * Reset automatic rotation timer
 */
function resetRSSAutoRotate() {
    startRSSAutoRotate();
}

/**
 * Initialize RSS widget
 */
export function initializeRSS() {
    // Update RSS feeds on load and every 5 minutes
    updateRSSFeeds();
    setInterval(updateRSSFeeds, 300000);
}

// Expose navigation functions to window for onclick handlers
window.nextRSSItem = nextRSSItem;
window.prevRSSItem = prevRSSItem;
