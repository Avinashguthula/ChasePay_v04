const API_URL = "https://chasepay.onrender.com/api";

document.getElementById('login-btn')?.addEventListener('click', async () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const msg = document.getElementById('status-msg');

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            window.location.href = 'dashboard.html';
        } else {
            msg.textContent = data.detail || 'Login failed';
            msg.className = 'mt-4 text-center text-sm text-red-600';
            msg.classList.remove('hidden');
        }
    } catch (error) {
        console.error(error);
        msg.textContent = 'An error occurred';
        msg.className = 'mt-4 text-center text-sm text-red-600';
        msg.classList.remove('hidden');
    }
});

document.getElementById('signup-btn')?.addEventListener('click', async () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const msg = document.getElementById('status-msg');

    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (response.ok) {
            msg.textContent = 'Account created! You can now login.';
            msg.className = 'mt-4 text-center text-sm text-green-600';
            msg.classList.remove('hidden');
        } else {
            msg.textContent = data.detail || 'Signup failed';
            msg.className = 'mt-4 text-center text-sm text-red-600';
            msg.classList.remove('hidden');
        }
    } catch (error) {
        console.error(error);
    }
});

function checkAuth() {
    const token = localStorage.getItem('access_token');
    const publicPages = ['index.html', 'login.html', '/'];
    const isLoginPage = publicPages.some(page => window.location.pathname.endsWith(page));

    if (!token && !isLoginPage) {
        window.location.href = 'login.html';
    }
}

function handleAuthCallback() {
    const hash = window.location.hash;
    if (hash && (hash.includes('access_token') || hash.includes('error'))) {
        const params = new URLSearchParams(hash.substring(1));
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        const type = params.get('type');

        if (accessToken) {
            localStorage.setItem('access_token', accessToken);
            if (refreshToken) localStorage.setItem('refresh_token', refreshToken);

            // Try to get user info from the fragment if available (though Supabase usually just gives the token)
            // Or just redirect to dashboard and let the dashboard fetch user info
            window.location.hash = ''; // Clear hash
            window.location.href = 'dashboard.html';
        } else if (params.get('error')) {
            const msg = document.getElementById('status-msg');
            if (msg) {
                msg.textContent = params.get('error_description') || 'Authentication error';
                msg.className = 'mt-4 text-center text-sm text-red-600';
                msg.classList.remove('hidden');
            }
        }
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// Initialize
handleAuthCallback();
checkAuth();
