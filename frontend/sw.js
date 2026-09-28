// Trocar o número da versão sempre que quiser forçar todo mundo a baixar tudo de novo.
const CACHE_NAME = 'zerando-manaus-v2';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './styles.css',
  './script.js',
  './integracao.js',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  self.skipWaiting(); // a versão nova assume sem esperar fechar as abas
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((nomes) =>
        Promise.all(nomes.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Só cuida de arquivos do próprio site (GET). Chamadas à API passam direto.
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  // Rede primeiro: sempre a versão mais nova. O cache só serve de reserva offline.
  event.respondWith(
    fetch(req)
      .then((resp) => {
        if (resp.ok) {
          const copia = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copia));
        }
        return resp;
      })
      .catch(() => caches.match(req))
  );
});