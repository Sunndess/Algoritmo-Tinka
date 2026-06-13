const CACHE_NAME = 'tinka-cache-v1';
const OFFLINE_URL = '/';

const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/app.js',
  '/manifest.json'
];

// Instalar y cachear recursos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Cacheando archivos de la app');
      return cache.addAll(ASSETS_TO_CACHE).catch(err => {
        console.log('Algunos archivos no pudieron cachearse:', err);
        return cache.addAll([OFFLINE_URL]);
      });
    })
  );
  self.skipWaiting();
});

// Activar y limpiar cachés antiguos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Eliminando cache anterior:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Estrategia de red primero, caché como fallback
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  // Para solicitudes API, usar network-first
  if (event.request.url.includes('/update') || event.request.url.includes('/predict')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return new Response(
            JSON.stringify({
              status: 'error',
              message: 'Sin conexión. No se puede acceder al servidor.'
            }),
            { 
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
    );
    return;
  }

  // Para recursos estáticos, usar cache-first
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request)
        .then(response => {
          if (!response || response.status !== 200) {
            return response;
          }
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          return response;
        })
        .catch(() => caches.match(OFFLINE_URL))
      )
  );
});
