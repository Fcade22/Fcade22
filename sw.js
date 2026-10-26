// Service worker: la app funciona sin internet, pero cuando HAY internet
// siempre trae la version nueva (asi los cambios se ven al instante).
const CACHE = "membrete-sl-v5";
// Lo pesado del catalogo (molde PDF, fuentes, fontkit) va en un cache aparte que NO se borra en
// cada version nueva: bajarlo de nuevo cuesta ~5 MB. Cuando el molde cambia, cambia su nombre
// (plantilla-<fecha>.pdf) y la app borra el viejo. Mismo nombre que CACHE_CATALOGO en index.html.
const CACHE_CATALOGO = "sl-catalogo-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./pdf-lib.min.js",
  "./config.json",
  "./plantillas/membrete.pdf",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/apple-touch-icon.png",
  "./catalogo/productos.json",
  "./catalogo/mayorista.enc.json"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      // "reload": que no tome copias viejas del cache HTTP del navegador.
      .then((c) => c.addAll(ASSETS.map((u) => new Request(u, { cache: "reload" }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE && k !== CACHE_CATALOGO).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function guardarEn(nombre, req, resp) {
  if (!resp || !resp.ok) return;
  const copy = resp.clone();
  caches.open(nombre).then((c) => c.put(req, copy)).catch(() => {});
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  // Lo de otros sitios (los precios de skinleather.store) va directo: nunca de una copia guardada.
  if (new URL(req.url).origin !== self.location.origin) return;

  // El HTML y los .json (config, lista de articulos, lista mayorista): primero internet (para ver
  // cambios), cache como respaldo offline.
  const esDocumento =
    req.mode === "navigate" ||
    req.destination === "document" ||
    req.url.endsWith(".html") ||
    req.url.endsWith(".json");

  if (esDocumento) {
    e.respondWith(
      fetch(req)
        .then((resp) => { guardarEn(CACHE, req, resp); return resp; })
        .catch(() => caches.match(req).then((r) => r || caches.match("./index.html")))
    );
    return;
  }

  // El resto (libreria PDF, iconos, membrete, molde del catalogo): primero cache (no cambian seguido).
  const nombre = req.url.includes("/catalogo/") ? CACHE_CATALOGO : CACHE;
  e.respondWith(
    caches.match(req).then((r) =>
      r ||
      fetch(req)
        .then((resp) => { guardarEn(nombre, req, resp); return resp; })
        .catch(() => undefined)
    )
  );
});
