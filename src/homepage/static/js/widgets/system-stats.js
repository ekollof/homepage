/**
 * System statistics sidebar widget
 */

import { SYSTEM_STATS_POSITION, SYSTEM_STATS_REFRESH_INTERVAL } from '../core/constants.js.j2';
import { formatUptime } from '../core/utils.js';

let systemStatsVisible = false;
let systemStatsPosition = localStorage.getItem('statsPosition') || SYSTEM_STATS_POSITION;
let systemStatsInterval = null;
let cpuHistory = [];
let memoryHistory = [];
const maxHistoryPoints = 30;

/**
 * Toggle system stats sidebar visibility
 */
export function toggleSystemStats() {
    systemStatsVisible = !systemStatsVisible;
    const sidebar = document.getElementById('systemStatsSidebar');
    const expandedContent = document.getElementById('statsExpandedContent');
    const slimBar = document.getElementById('statsSlimBar');
    
    if (systemStatsVisible) {
        sidebar.classList.add('expanded');
        expandedContent.style.display = 'block';
        slimBar.style.display = 'none';
        updateSystemStats();
        systemStatsInterval = setInterval(updateSystemStats, SYSTEM_STATS_REFRESH_INTERVAL);
    } else {
        sidebar.classList.remove('expanded');
        expandedContent.style.display = 'none';
        slimBar.style.display = 'block';
        if (systemStatsInterval) {
            clearInterval(systemStatsInterval);
            systemStatsInterval = null;
        }
    }
}

/**
 * Set sidebar position (left, right, top, bottom)
 * @param {string} position - Position identifier
 */
export function setStatsPosition(position) {
    const sidebar = document.getElementById('systemStatsSidebar');
    sidebar.classList.remove('position-left', 'position-right', 'position-top', 'position-bottom');
    sidebar.classList.add(`position-${position}`);
    systemStatsPosition = position;
    localStorage.setItem('statsPosition', position);
}

/**
 * Fetch and update system stats display
 */
export function updateSystemStats() {
    fetch('/api/system-stats')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('System stats error:', data.error);
                return;
            }

            // Update icon panel and slim bar
            const cpuPercent = `${Math.round(data.cpu_percent)}%`;
            const memoryPercent = `${Math.round(data.memory_percent)}%`;
            const diskPercent = `${Math.round(data.disk_percent)}%`;
            const networkTotal = `${(data.network_sent_mb + data.network_recv_mb).toFixed(1)}M`;
            
            document.getElementById('cpuIconValue').textContent = cpuPercent;
            document.getElementById('memoryIconValue').textContent = memoryPercent;
            document.getElementById('diskIconValue').textContent = diskPercent;
            document.getElementById('networkIconValue').textContent = networkTotal;
            
            document.getElementById('cpuSlimValue').textContent = cpuPercent;
            document.getElementById('memorySlimValue').textContent = memoryPercent;
            document.getElementById('diskSlimValue').textContent = diskPercent;
            document.getElementById('networkSlimValue').textContent = networkTotal;

            // Update CPU section
            updateStatBar('cpuBar', data.cpu_percent);
            document.getElementById('cpuValue').textContent = `${Math.round(data.cpu_percent)}%`;
            document.getElementById('cpuCores').textContent = `${data.cpu_count} cores`;
            document.getElementById('cpuFreq').textContent = `${Math.round(data.cpu_freq_current)} MHz`;

            // Update CPU sparkline
            cpuHistory.push(data.cpu_percent);
            if (cpuHistory.length > maxHistoryPoints) cpuHistory.shift();
            updateSparkline('cpuSparklinePath', cpuHistory);

            // Update Memory section
            updateStatBar('memoryBar', data.memory_percent);
            document.getElementById('memoryValue').textContent = `${Math.round(data.memory_percent)}%`;
            document.getElementById('memoryUsed').textContent = `${Math.round(data.memory_used_mb)} MB`;
            document.getElementById('memoryTotal').textContent = `${Math.round(data.memory_total_mb)} MB`;

            // Update Memory sparkline
            memoryHistory.push(data.memory_percent);
            if (memoryHistory.length > maxHistoryPoints) memoryHistory.shift();
            updateSparkline('memorySparklinePath', memoryHistory);

            // Update Disk section
            updateStatBar('diskBar', data.disk_percent);
            document.getElementById('diskValue').textContent = `${Math.round(data.disk_percent)}%`;
            document.getElementById('diskUsed').textContent = `${data.disk_used_gb.toFixed(1)} GB`;
            document.getElementById('diskTotal').textContent = `${data.disk_total_gb.toFixed(1)} GB`;

            // Update Network section
            document.getElementById('networkRecv').textContent = `${data.network_recv_mb.toFixed(1)} MB`;
            document.getElementById('networkSent').textContent = `${data.network_sent_mb.toFixed(1)} MB`;

            // Update Battery section (conditional)
            if (data.battery) {
                const batterySection = document.getElementById('batterySection');
                batterySection.style.display = 'block';
                updateStatBar('batteryBar', data.battery.percent);
                document.getElementById('batteryValue').textContent = `${Math.round(data.battery.percent)}%`;
                
                let statusText = data.battery.plugged ? '🔌 Charging' : '🔋 Discharging';
                if (data.battery.time_left) {
                    const hours = Math.floor(data.battery.time_left / 3600);
                    const minutes = Math.floor((data.battery.time_left % 3600) / 60);
                    statusText += ` (${hours}h ${minutes}m)`;
                }
                document.getElementById('batteryStatus').textContent = statusText;
            }

            // Update System info
            document.getElementById('processCount').textContent = data.processes;
            document.getElementById('uptime').textContent = formatUptime(data.uptime_seconds);

            // Update Temperature (conditional)
            if (data.temperature_avg !== undefined) {
                document.getElementById('temperatureInfo').style.display = 'inline';
                document.getElementById('temperature').textContent = Math.round(data.temperature_avg);
            }
        })
        .catch(error => {
            console.error('Failed to fetch system stats:', error);
        });
}

/**
 * Update stat bar width
 * @param {string} barId - Element ID of the bar
 * @param {number} percentage - Percentage value (0-100)
 */
function updateStatBar(barId, percentage) {
    const bar = document.getElementById(barId);
    bar.style.setProperty('--bar-width', `${percentage}%`);
}

/**
 * Update SVG sparkline path
 * @param {string} pathId - Element ID of the SVG path
 * @param {Array<number>} data - Array of data points
 */
function updateSparkline(pathId, data) {
    if (data.length === 0) return;

    const points = data.map((value, index) => {
        const x = (index / (maxHistoryPoints - 1)) * 120;
        const y = 30 - (value / 100) * 30;
        return `${x},${y}`;
    }).join(' ');

    document.getElementById(pathId).setAttribute('points', points);
}

/**
 * Initialize system stats sidebar
 */
export function initializeSystemStats() {
    const sidebar = document.getElementById('systemStatsSidebar');
    setStatsPosition(systemStatsPosition);
    
    // Start updating slim bar immediately
    updateSystemStats();
    setInterval(updateSystemStats, SYSTEM_STATS_REFRESH_INTERVAL);
    
    // Add keyboard shortcut for system stats (s key)
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (e.key === 's' || e.key === 'S') {
            e.preventDefault();
            toggleSystemStats();
        }
    });
}

// Expose toggle function to window for onclick handlers
window.toggleSystemStats = toggleSystemStats;
