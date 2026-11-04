/* Fiscaliza Brasil como aplicativo: guarda as páginas e os dados já vistos para abrir rápido e funcionar sem internet.
   Páginas: tenta a rede primeiro. Arquivos e dados: entrega o guardado na hora e atualiza em segundo plano. */
const V = "fb-v1";
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
  e.respondWith(caches.open(V).then(async (c) => {
    const hit = await c.match(r);
    const net = fetch(r).then((res) => { if (res.ok) c.put(r, res.clone()); return res; }).catch(() => hit);
    return hit || net;
  }));
});
