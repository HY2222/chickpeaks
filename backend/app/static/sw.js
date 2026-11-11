// Service worker de Willo: guarda las pantallas para que la app abra rápido.
// Los datos (/api) siempre se piden al servidor, nunca se guardan.
const CACHE = "willo-v11";
const BASE = ["/demo/banco", "/demo", "/demo/apoyo", "/static/icons/favicon-32.png", "/static/willo.css?v=7", "/static/pwa.js",
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
    fetch(e.request, {cache: "no-cache"})  // pregunta siempre al servidor: nunca una pantalla vieja de la caché del navegador
      .then(r => {
        if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); }  // un error no se guarda
        return r;
      })
      .catch(() => caches.match(e.request))
  );
});
