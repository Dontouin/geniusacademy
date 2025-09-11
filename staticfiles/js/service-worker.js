const CACHE_NAME = 'genius-academy-cache-v1';
const OFFLINE_URL = '/offline/'; // URL du template offline
const ASSETS_TO_CACHE = [
    '/',
    OFFLINE_URL,
    '/static/css/style.css',
    '/static/css/style.min.css',
    '/static/css/tailwind.css',
    '/static/vendor/bootstrap-5.3.2/css/bootstrap.min.css',
    '/static/vendor/fontawesome-6.5.1/css/all.min.css',
    '/static/js/main.js',
    '/static/vendor/bootstrap-5.3.2/js/bootstrap.bundle.min.js',
    '/static/vendor/jquery-3.7.1/jquery-3.7.1.min.js',
    '/static/img/favicon.png',
    '/static/img/icons/web-app-manifest-192x192.png',
    '/static/img/icons/web-app-manifest-512x512.png',
    '/manifest/site.webmanifest'
];

// Install Event - mise en cache des fichiers essentiels
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Caching assets...');
                return cache.addAll(ASSETS_TO_CACHE);
            })
    );
    self.skipWaiting();
});

// Activate Event - nettoyage des anciens caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// Fetch Event - servir depuis le cache si possible
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse; // Fichier trouvé dans le cache
            }

            // Sinon, fetch et cache dynamique
            return fetch(event.request)
                .then(networkResponse => {
                    return caches.open(CACHE_NAME).then(cache => {
                        // On ne met en cache que les requêtes du même domaine
                        if (event.request.url.startsWith(self.location.origin)) {
                            cache.put(event.request, networkResponse.clone());
                        }
                        return networkResponse;
                    });
                })
                .catch(() => {
                    // Si hors ligne et fichier non trouvé, retourner le template offline
                    if (event.request.mode === 'navigate') {
                        return caches.match(OFFLINE_URL);
                    }
                });
        })
    );
});
