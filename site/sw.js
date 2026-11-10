/* Fiscaliza Brasil como aplicativo: guarda as páginas e os dados já vistos para abrir rápido e funcionar sem internet.
   Tudo tenta a rede primeiro (para ninguém ver versão velha depois de uma atualização) e usa o guardado só sem internet. */
const V = "fb-v2";
self.addEventListener("install", (e) => { self.skipWaiting(); e.waitUntil(caches.open(V).then((c) => c.addAll(["/", "/fiscalize", "/ui.css", "/fundo.css", "/icon-192.png"]).catch(() => {}))); });
self.addEventListener("activate", (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", (e) => {
  const r = e.request; if (r.method !== "GET") return;
  const u = new URL(r.url); if (u.origin !== location.origin) return;
  if (u.pathname.startsWith("/api/") || u.pathname === "/painel" || u.pathname.startsWith("/painel")) return;
  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then((res) => { const cp = res.clone(); caches.open(V).then((c) => c.put(r, cp)); return res; }).catch(() => caches.match(r).then((m) => m || caches.match("/"))));
    return;
  }
  e.respondWith(caches.open(V).then((c) => fetch(r).then((res) => { if (res.ok) c.put(r, res.clone()); return res; }).catch(() => c.match(r))));
});
