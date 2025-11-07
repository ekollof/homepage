/**
 * Clock and date widget
 */

import { CLOCK_FORMAT } from '../core/constants.js.j2';

/**
 * Update clock display with current time
 */
export function updateClock() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    if (CLOCK_FORMAT === '12') {
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12;
        document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds} ${ampm}`;
    } else {
        hours = String(hours).padStart(2, '0');
        document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;
    }
}

/**
 * Update date display with current date
 */
export function updateDate() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = now.toLocaleDateString('en-US', options);
    document.getElementById('date').textContent = dateString;
}

/**
 * Initialize clock and date widgets
 */
export function initializeClock() {
    // Update immediately
    updateClock();
    updateDate();
    
    // Update clock every second
    setInterval(updateClock, 1000);
    
    // Update date every minute
    setInterval(updateDate, 60000);
}
