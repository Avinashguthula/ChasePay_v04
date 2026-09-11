// BASE_API_URL is resolved at runtime from the /api/config endpoint via config.js.
// config.js must be loaded before this file.

async function fetchWithAuth(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return null;
    }

    const config = await window.getAppConfig();
    const BASE_API_URL = config.api_url;

    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
    };

    try {
        const response = await fetch(`${BASE_API_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = 'index.html';
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}
