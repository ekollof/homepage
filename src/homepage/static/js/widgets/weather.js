/**
 * Weather widget with current conditions and forecast
 */

let forecastMode = 'daily';  // 'hourly' or 'daily'
let forecastExpanded = false;

/**
 * Update current weather display
 */
export function updateWeather() {
    const weatherElement = document.getElementById('weather');
    if (!weatherElement) return;

    fetch('/api/weather')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                weatherElement.innerHTML = `<span class="weather-loading">Weather unavailable</span>`;
                console.warn('Weather API error:', data.error);
                return;
            }

            const tempUnit = data.units === 'metric' ? '°C' : '°F';
            const windUnit = data.units === 'metric' ? 'km/h' : 'mph';

            weatherElement.innerHTML = `
                <span class="weather-location">${data.location}</span>
                <span class="weather-temp">${Math.round(data.temperature)}${tempUnit}</span>
                <span class="weather-desc">${data.description}</span>
                <span class="weather-details">
                    <span>💧 ${data.humidity}%</span>
                    <span>💨 ${Math.round(data.wind_speed)} ${windUnit}</span>
                </span>
            `;
        })
        .catch(error => {
            // Silently fail for network errors (don't spam console)
            if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
                weatherElement.innerHTML = `<span class="weather-loading">No network</span>`;
            } else {
                weatherElement.innerHTML = `<span class="weather-loading">Weather unavailable</span>`;
                console.warn('Weather fetch failed:', error.message);
            }
        });
}

/**
 * Update weather forecast display (hourly or daily)
 */
export function updateWeatherForecast() {
    const forecastElement = document.getElementById('weatherForecast');
    if (!forecastElement) return;

    const endpoint = forecastMode === 'daily' ? '/api/weather/forecast/daily' : '/api/weather/forecast';

    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const forecastData = forecastMode === 'daily' ? data.daily : data.hourly;
            if (data.error || !forecastData || forecastData.length === 0) {
                forecastElement.innerHTML = `<div class="forecast-loading">Forecast unavailable</div>`;
                return;
            }

            const tempUnit = data.units === 'metric' ? '°C' : '°F';
            const containerClass = forecastMode === 'daily' ? 'forecast-days' : 'forecast-hours';
            let html = `<div class="${containerClass}">`;

            if (forecastMode === 'daily') {
                forecastData.forEach(item => {
                    const precipDisplay = item.precipitation_probability > 0 
                        ? `<div class="forecast-precip">${item.precipitation_probability}%</div>`
                        : '';
                    
                    html += `
                        <div class="forecast-item">
                            <div class="forecast-day">${item.day}</div>
                            <div class="forecast-emoji">${item.weather_emoji}</div>
                            <div class="forecast-temp-range">${item.temperature_max}/${item.temperature_min}${tempUnit}</div>
                            ${precipDisplay}
                        </div>
                    `;
                });
            } else {
                forecastData.forEach(item => {
                    const precipDisplay = item.precipitation_probability > 0 
                        ? `<div class="forecast-precip">${item.precipitation_probability}%</div>`
                        : '';
                    
                    html += `
                        <div class="forecast-item">
                            <div class="forecast-time">${item.hour}</div>
                            <div class="forecast-emoji">${item.weather_emoji}</div>
                            <div class="forecast-temp">${item.temperature}${tempUnit}</div>
                            ${precipDisplay}
                        </div>
                    `;
                });
            }

            html += '</div>';
            forecastElement.innerHTML = html;
        })
        .catch(error => {
            if (!error.message.includes('NetworkError') && !error.message.includes('Failed to fetch')) {
                console.warn('Forecast fetch failed:', error.message);
            }
            forecastElement.innerHTML = `<div class="forecast-loading">Forecast unavailable</div>`;
        });
}

/**
 * Initialize weather widget
 */
export function initializeWeather() {
    // Update weather on load and every 10 minutes
    updateWeather();
    setInterval(updateWeather, 600000);
    
    // Forecast expand/collapse functionality
    const forecastExpandBtn = document.getElementById('forecastExpandBtn');
    const forecastContainer = document.getElementById('forecastContainer');

    if (forecastExpandBtn && forecastContainer) {
        forecastExpandBtn.addEventListener('click', () => {
            forecastExpanded = !forecastExpanded;
            if (forecastExpanded) {
                forecastContainer.style.display = 'block';
                forecastExpandBtn.textContent = '📅 Hide Forecast';
                // Load forecast when expanded for the first time
                if (forecastContainer.dataset.loaded !== 'true') {
                    updateWeatherForecast();
                    forecastContainer.dataset.loaded = 'true';
                }
            } else {
                forecastContainer.style.display = 'none';
                forecastExpandBtn.textContent = '📅 Show Forecast';
            }
        });
    }

    // Forecast mode toggle functionality
    const forecastModeToggle = document.getElementById('forecastModeToggle');
    if (forecastModeToggle) {
        forecastModeToggle.addEventListener('click', () => {
            forecastMode = forecastMode === 'hourly' ? 'daily' : 'hourly';
            forecastModeToggle.textContent = forecastMode === 'hourly' ? 'Hourly' : 'Daily';
            updateWeatherForecast();
        });
    }

    // Update forecast every 10 minutes if expanded
    setInterval(() => {
        if (forecastExpanded) {
            updateWeatherForecast();
        }
    }, 600000);
}
