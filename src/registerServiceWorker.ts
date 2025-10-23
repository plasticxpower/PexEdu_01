const BASE_URL = import.meta.env.BASE_URL ?? '/';
const SERVICE_WORKER_URL = `${BASE_URL}${BASE_URL.endsWith('/') ? '' : '/'}sw.js`;

export function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) {
    return;
  }

  if (import.meta.env.DEV) {
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      registrations.forEach((registration) => registration.unregister().catch(() => {}));
    });
    return;
  }

  window.addEventListener('load', () => {
    navigator.serviceWorker.register(SERVICE_WORKER_URL).catch(() => {
      // Intentionally swallow errors; SW is an enhancement.
    });
  });
}
