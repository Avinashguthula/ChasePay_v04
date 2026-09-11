// Runtime configuration helper for ChasePay frontend.
// Fetches /api/config once, caches result, exposes window.getAppConfig() as a Promise.
(function () {
    var defaultOrigin = (
        typeof window !== 'undefined' &&
        window.location &&
        window.location.origin &&
        window.location.origin !== 'null' &&
        !window.location.origin.startsWith('file:')
    ) ? window.location.origin : 'http://localhost:8000';

    window.APP_CONFIG = window.APP_CONFIG || {
        api_url: defaultOrigin + '/api',
        frontend_url: defaultOrigin,
        supabase_url: '',
        isLoaded: false
    };

    var fetchPromise = null;

    window.getAppConfig = function () {
        if (window.APP_CONFIG.isLoaded) {
            return Promise.resolve(window.APP_CONFIG);
        }
        if (!fetchPromise) {
            fetchPromise = fetch('/api/config')
                .then(function (res) {
                    if (res.ok) return res.json();
                    throw new Error('Config request failed: ' + res.status);
                })
                .then(function (data) {
                    if (data.api_url) window.APP_CONFIG.api_url = data.api_url;
                    if (data.frontend_url) window.APP_CONFIG.frontend_url = data.frontend_url;
                    if (data.supabase_url) window.APP_CONFIG.supabase_url = data.supabase_url;
                    window.APP_CONFIG.isLoaded = true;
                    return window.APP_CONFIG;
                })
                .catch(function (err) {
                    console.warn('Could not load runtime config from /api/config, using origin default:', err);
                    window.APP_CONFIG.isLoaded = true;
                    return window.APP_CONFIG;
                });
        }
        return fetchPromise;
    };

    // Kick off the fetch immediately on script load
    window.getAppConfig();
})();
