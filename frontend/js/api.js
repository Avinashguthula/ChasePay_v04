const BASE_API_URL = "https://chasepay.onrender.com/api";

async function fetchWithAuth(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return null;
    }

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
