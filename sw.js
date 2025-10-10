const CACHE_VERSION = 'pexedu-cache-v2';
const STATIC_ASSETS = ['index.html', 'manifest.webmanifest', 'favicon.svg'];

function getAbsoluteUrl(path) {
  return new URL(path, self.registration.scope).toString();
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION)
      .then((cache) => {
        const assets = [self.registration.scope, ...STATIC_ASSETS.map(getAbsoluteUrl)];
        return cache.addAll(assets);
      })
      .catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.map((key) => {
            if (key !== CACHE_VERSION) {
              return caches.delete(key);
            }
            return Promise.resolve();
          })
        )
      )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return;
  }

  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(request)
        .then((networkResponse) => {
          if (
            !networkResponse ||
            networkResponse.status !== 200 ||
            networkResponse.type !== 'basic'
          ) {
            return networkResponse;
          }

          const responseToCache = networkResponse.clone();
          caches
            .open(CACHE_VERSION)
            .then((cache) => cache.put(request, responseToCache))
            .catch(() => {});

          return networkResponse;
        })
        .catch(() => caches.match(getAbsoluteUrl('./')));
    })
  );
});
