// Saída pelo Brasil: alguns sites de Assembleias só respondem a acessos de dentro do país.
// O pedido do coletor (GitHub, EUA) chega aqui e é repassado a um Durable Object criado na América do Sul,
// que faz o acesso a partir de lá. Só aceita sites da lista abaixo e só com a chave do projeto.
// Não contorna captcha nem bloqueio anti-robô: apenas busca páginas e dados públicos que respondem normalmente no Brasil.
const PERMITIDOS = [/(^|\.)almg\.gov\.br$/, /(^|\.)alepe\.pe\.gov\.br$/, /(^|\.)al\.rs\.gov\.br$/, /(^|\.)al\.es\.gov\.br$/,
  /(^|\.)al\.ma\.leg\.br$/, /(^|\.)al\.ap\.gov\.br$/, /(^|\.)al\.ap\.leg\.br$/, /(^|\.)cl\.df\.gov\.br$/, /(^|\.)cmc\.pr\.gov\.br$/, /(^|\.)assembleia\.pr\.leg\.br$/, /^www\.cloudflare\.com$/];
const UA = "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)";

async function busca(p) {
    try {
      const r = await fetch(p.u, { method: p.m || "GET", headers: { "user-agent": UA, ...(p.h || {}) }, body: p.b ?? undefined, redirect: "follow", signal: AbortSignal.timeout(90000) });
      const h = new Headers({ "content-type": r.headers.get("content-type") || "application/octet-stream", "x-status": String(r.status) });
      return new Response(r.body, { status: r.status, headers: h });
    } catch (e) {
      return new Response(String(e), { status: 599, headers: { "x-erro": "1" } });
    }
}

export class Saida {
  constructor(state, env) { this.state = state; }
  async fetch(req) { return busca(await req.json()); }
}

export default {
  async fetch(req, env) {
    if (!env.CHAVE || req.headers.get("x-chave") !== env.CHAVE) return new Response("proibido", { status: 403 });
    const u = new URL(req.url).searchParams.get("u");
    let alvo; try { alvo = new URL(u); } catch { return new Response("u inválido", { status: 400 }); }
    if (alvo.protocol !== "https:" && alvo.protocol !== "http:" || !PERMITIDOS.some((r) => r.test(alvo.hostname))) return new Response("site fora da lista", { status: 403 });
    const h = {}; for (const k of ["accept", "content-type"]) if (req.headers.get(k)) h[k] = req.headers.get(k);
    const corpo = req.method === "POST" ? await req.text() : null;
    const p = { u: alvo.href, m: req.method === "POST" ? "POST" : "GET", h, b: corpo };
    if (new URL(req.url).searchParams.get("modo") === "do") {  // alternativa: Durable Object com dica de região
      const stub = env.SAIDA.get(env.SAIDA.idFromName(new URL(req.url).searchParams.get("n") || "br1"), { locationHint: "sam" });
      return stub.fetch("https://do/", { method: "POST", body: JSON.stringify(p) });
    }
    return busca(p);
  },
};
