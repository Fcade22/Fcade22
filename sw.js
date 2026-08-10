// Service worker: la app funciona sin internet, pero cuando HAY internet
// siempre trae la version nueva (asi los cambios se ven al instante).
const CACHE = "membrete-sl-v4";
const ASSETS = [
  "./",
  "./index.html",
  "./pdf-lib.min.js",
  "./config.json",
  "./plantillas/membrete.pdf",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/apple-touch-icon.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  // El HTML y la config: primero internet (para ver cambios), cache como respaldo offline.
  const esDocumento =
    req.mode === "navigate" ||
    req.destination === "document" ||
    req.url.endsWith(".html") ||
    req.url.endsWith("config.json");

  if (esDocumento) {
    e.respondWith(
      fetch(req)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return resp;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match("./index.html")))
    );
    return;
  }

  // El resto (libreria PDF, iconos, membrete): primero cache (no cambian seguido).
  e.respondWith(
    caches.match(req).then((r) =>
      r ||
      fetch(req)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return resp;
        })
        .catch(() => undefined)
    )
  );
});
