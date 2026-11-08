// Service worker de Willo: guarda las pantallas para que la app abra rápido.
// Los datos (/api) siempre se piden al servidor, nunca se guardan.
const CACHE = "willo-v1";
const BASE = ["/demo", "/demo/apoyo", "/static/willo.css", "/static/pwa.js",
              "/static/icons/icon-192.png", "/static/icons/icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api")) return;
  // Primero la red (para ver siempre la última versión); si no hay conexión, lo guardado.
  e.respondWith(
    fetch(e.request)
      .then(r => { const copia = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); return r; })
      .catch(() => caches.match(e.request))
  );
});
