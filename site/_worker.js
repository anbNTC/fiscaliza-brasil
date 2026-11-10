/* Cloudflare Pages (modo avançado): serve o site e a rota /api/noticias do ACONTECE AGORA.
   As manchetes vêm dos feeds RSS públicos de cada veículo. Mostramos só título, horário, veículo e link
   para a matéria original (sem copiar texto nem imagem). Cache de 5 minutos. */
const FONTES = [
  // [id, nome, grupo, [urls em ordem de preferência], filtrar só política?]
  ["camara", "Agência Câmara", "Agências oficiais", ["https://www.camara.leg.br/noticias/rss/ultimas-noticias", "https://www.camara.leg.br/noticias/rss/dinamico/ULTIMAS-NOTICIAS"], false],
  ["senado", "Agência Senado", "Agências oficiais", ["https://www12.senado.leg.br/noticias/feed/todasnoticias/RSS", "https://www12.senado.leg.br/noticias/feed/ultimasnoticias/RSS"], false],
  ["abr", "Agência Brasil", "Agências oficiais", ["https://agenciabrasil.ebc.com.br/rss/politica/feed.xml"], false],
  ["g1", "g1", "Grandes portais", ["https://g1.globo.com/rss/g1/politica/"], false],
  ["folha", "Folha de S.Paulo", "Grandes portais", ["https://feeds.folha.uol.com.br/poder/rss091.xml"], false],
  ["estadao", "Estadão", "Grandes portais", ["https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/politica/"], false],
  ["uol", "UOL", "Grandes portais", ["https://rss.uol.com.br/feed/noticias.xml"], true],
  ["cnn", "CNN Brasil", "Grandes portais", ["https://www.cnnbrasil.com.br/politica/feed/"], false],
  ["poder360", "Poder360", "Grandes portais", ["https://www.poder360.com.br/feed/"], true],
  ["metropoles", "Metrópoles", "Grandes portais", ["https://www.metropoles.com/brasil/politica-brasil/feed", "https://www.metropoles.com/feed"], true],
  ["gazeta", "Gazeta do Povo", "Mais à direita", ["https://www.gazetadopovo.com.br/feed/rss/republica.xml"], false],
  ["oeste", "Revista Oeste", "Mais à direita", ["https://revistaoeste.com/politica/feed/", "https://revistaoeste.com/feed/"], true],
  ["jovempan", "Jovem Pan", "Mais à direita", ["https://jovempan.com.br/noticias/politica/feed", "https://jovempan.com.br/feed"], true],
  ["carta", "CartaCapital", "Mais à esquerda", ["https://www.cartacapital.com.br/politica/feed/"], false],
  ["bdf", "Brasil de Fato", "Mais à esquerda", ["https://www.brasildefato.com.br/rss2.xml", "https://www.brasildefato.com.br/rss"], true],
  ["cfoco", "Congresso em Foco", "Mais à esquerda", ["https://www.congressoemfoco.com.br/feed/", "https://congressoemfoco.com.br/feed/"], false],
];
const POL = /pol[ií]tic|congress|c[âa]mara|senad|stf|supremo|governo|minist|elei[çc]|deputad|presiden|lula|planalto|partid/i;

const ent = (s) => String(s || "")
  .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1").replace(/<[^>]+>/g, "")
  .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n)).replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCharCode(parseInt(n, 16)))
  .replace(/&quot;/g, '"').replace(/&apos;|&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&")
  .replace(/\s+/g, " ").trim();
const tag = (blk, t) => { const m = blk.match(new RegExp(`<${t}(?:\\s[^>]*)?>([\\s\\S]*?)</${t}>`, "i")); return m ? ent(m[1]) : ""; };

export function parseFeed(xml, fonte) {
  const [id, , , , filtrar] = fonte; const out = [];
  const blocos = xml.match(/<item[\s>][\s\S]*?<\/item>/gi) || xml.match(/<entry[\s>][\s\S]*?<\/entry>/gi) || [];
  for (const b of blocos.slice(0, 40)) {
    const t = tag(b, "title");
    let l = tag(b, "link");
    if (!l) { const m = b.match(/<link[^>]*href="([^"]+)"/i); l = m ? m[1] : ""; }
    const d = new Date(tag(b, "pubDate") || tag(b, "dc:date") || tag(b, "published") || tag(b, "updated"));
    if (!t || !/^https?:\/\//.test(l) || isNaN(d)) continue;
    if (filtrar && !POL.test(t + " " + l + " " + tag(b, "category"))) continue;
    out.push({ t: t.slice(0, 220), l, d: d.toISOString(), s: id });
  }
  return out;
}


/* ---- "Em alta": agrupa manchetes do mesmo assunto em veículos diferentes ---- */
const STOP = new Set("a o os as de da do das dos e em no na nos nas um uma para por com sem que se ao aos sobre apos após contra entre mais menos diz afirma disse quer vai pode deve ser sao são foi tem ter como ja já ate até seu sua seus suas nao não sim ele ela eles elas isso esse essa este esta pelo pela pelos pelas novo nova hoje veja entenda".split(" "));
const POLEM = /pol[êe]mic|machis|mis[óo]gin|racis|homof[óo]b|transf[óo]b|xenof|ofens|insult|xing|ataca|ataque|amea[çc]|agress|viol[êe]nci|escând|escand|bate-boca|discuss[ãa]o|confus[ãa]o|briga|repercut|critica|crítica|repúdio|repudi|indign|absurd|preconceit|ódio|odio|fake news|mentir|desinforma/i;
const norm = (s) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const toks = (t) => new Set(norm(t).replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter((w) => w.length >= 4 && !STOP.has(w)));
function emAlta(itens) {
  const agora = Date.now(); const rec = itens.map((it, i) => ({ i, it, k: toks(it.t) })).filter((x) => agora - Date.parse(x.it.d) < 36 * 36e5);
  const grupos = [];
  for (const x of rec) {
    let melhor = null, sc = 0;
    for (const g of grupos) { let inter = 0; for (const w of x.k) if (g.k.has(w)) inter++; const j = inter / Math.min(x.k.size || 1, g.base || 1); if (inter >= 3 && j > sc) { sc = j; melhor = g; } }
    if (melhor && sc >= 0.45) { melhor.m.push(x); } else grupos.push({ k: x.k, base: x.k.size, m: [x] });
  }
  return grupos.map((g) => {
    const fontes = new Set(g.m.map((x) => x.it.s)); const ult = Math.max(...g.m.map((x) => Date.parse(x.it.d)));
    const polem = g.m.some((x) => POLEM.test(x.it.t)); const h = (agora - ult) / 36e5;
    return { ids: g.m.map((x) => x.i), n: fontes.size, polem, ult: new Date(ult).toISOString(), score: fontes.size * 2 + (polem ? 4 : 0) + (h < 6 ? 2 : h < 12 ? 1 : 0) };
  }).filter((g) => g.n >= 2 || g.polem).sort((a, b) => b.score - a.score || b.ult.localeCompare(a.ult)).slice(0, 12);
}
/* assuntos do momento: nomes próprios repetidos em vários veículos nas últimas 12 horas */
function assuntos(itens) {
  const agora = Date.now(); const c = new Map();
  for (const it of itens) {
    if (agora - Date.parse(it.d) > 12 * 36e5) continue;
    const vistos = new Set();
    const nomes = it.t.match(/\b(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'-]+|STF|PEC|CPI|PL|PT|TSE|PF|INSS|IOF)(?:\s+(?:de |da |do |dos |das )?[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ'-]+)*/g) || [];
    for (let n of nomes) {
      n = n.trim(); if (n.length < 3 || STOP.has(norm(n))) continue;
      const k = norm(n); if (vistos.has(k)) continue; vistos.add(k);
      const e = c.get(k) || { n, s: new Set() }; e.s.add(it.s); c.set(k, e);
    }
  }
  return [...c.values()].filter((e) => e.s.size >= 3 && !/^(O|A|Os|As|Em|No|Na|Para|Com|Por|Após|Apos|Sobre|Veja|Entenda|Câmara|Senado|Governo|Brasil|Congresso|Planalto|Justiça|Deputado|Deputada|Senador|Senadora|Presidente)$/.test(e.n)).sort((a, b) => b.s.size - a.s.size).slice(0, 10).map((e) => [e.n, e.s.size]);
}

/* Alguns veículos publicam o feed em ISO-8859-1/Windows-1252 (ex.: UOL). Detecta pelo cabeçalho ou pela declaração XML. */
const CP1252 = { 128: 8364, 130: 8218, 131: 402, 132: 8222, 133: 8230, 134: 8224, 135: 8225, 136: 710, 137: 8240, 138: 352, 139: 8249, 140: 338, 142: 381, 145: 8216, 146: 8217, 147: 8220, 148: 8221, 149: 8226, 150: 8211, 151: 8212, 152: 732, 153: 8482, 154: 353, 155: 8250, 156: 339, 158: 382, 159: 376 };
function decodifica(buf, ctype) {
  const bytes = new Uint8Array(buf);
  const head = new TextDecoder("utf-8").decode(bytes.slice(0, 300));
  let cs = ((ctype.match(/charset=([\w-]+)/i) || [])[1] || (head.match(/encoding=["']([\w-]+)["']/i) || [])[1] || "utf-8").toLowerCase();
  if (!/^(iso-8859-1|latin1|windows-1252|cp1252|iso8859-1)$/.test(cs)) {
    const txt = new TextDecoder("utf-8").decode(bytes);
    if (!txt.includes("\uFFFD")) return txt;   // UTF-8 válido
  }
  let out = "";                                  // ISO-8859-1 / Windows-1252
  for (let i = 0; i < bytes.length; i += 8192) {
    const parte = bytes.subarray(i, i + 8192); let s2 = "";
    for (const b of parte) s2 += String.fromCharCode(CP1252[b] || b);
    out += s2;
  }
  return out;
}

async function busca(fonte) {
  for (const url of fonte[3]) {
    try {
      const r = await fetch(url, { headers: { "user-agent": "FiscalizaBrasil/1.0 (agregador de manchetes com link para a fonte)", accept: "application/rss+xml, application/xml, text/xml, */*" },
        cf: { cacheTtl: 240, cacheEverything: true }, signal: AbortSignal.timeout(4000) });
      if (!r.ok) continue;
      const itens = parseFeed(decodifica(await r.arrayBuffer(), r.headers.get("content-type") || ""), fonte);
      if (itens.length) return { ok: true, itens };
    } catch (e) { /* tenta a próxima url */ }
  }
  return { ok: false, itens: [] };
}

async function monta() {
  const res = await Promise.all(FONTES.map(busca));
  const visto = new Set(); const itens = [];
  res.forEach((r) => r.itens.forEach((i) => { const k = i.l.split("?")[0]; if (!visto.has(k)) { visto.add(k); itens.push(i); } }));
  const agora = Date.now();
  const lista = itens.filter((i) => agora - Date.parse(i.d) < 3 * 864e5 && Date.parse(i.d) < agora + 36e5).sort((a, b) => b.d.localeCompare(a.d)).slice(0, 300);
  lista.forEach((i) => { if (POLEM.test(i.t)) i.p = 1; });
  return JSON.stringify({ gerado: new Date().toISOString(), fontes: FONTES.map((f, i) => ({ id: f[0], nome: f[1], grupo: f[2], ok: res[i].ok })), itens: lista, alta: emAlta(lista), assuntos: assuntos(lista) });
}
const FRESCO = 4 * 6e4;          // até 4 min: entrega direto
const GUARDA = 6 * 36e5;         // guarda até 6 h para entregar na hora enquanto atualiza
async function noticias(request, ctx) {
  const cache = caches.default; const chave = new Request(new URL("/api/noticias?v=3", request.url).toString());
  const salvar = async () => { const body = await monta(); await cache.put(chave, new Response(body, { headers: { "content-type": "application/json; charset=utf-8", "cache-control": `public, max-age=${GUARDA / 1000}`, "x-gerado": String(Date.now()) } })); return body; };
  const resp = (body, idade) => new Response(body, { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=60", "x-idade": String(Math.round(idade / 1000)), "access-control-allow-origin": "*" } });
  const hit = await cache.match(chave);
  if (hit) {
    const idade = Date.now() - Number(hit.headers.get("x-gerado") || 0);
    if (idade > FRESCO) ctx.waitUntil(salvar());   // entrega a versão guardada e atualiza em segundo plano
    return resp(await hit.text(), idade);
  }
  return resp(await salvar(), 0);
}

/* ---------- Em alta no Brasil (Google Trends, gratuito) ---------- */
const POLIT = /pol[íi]tic|govern|presiden|lula|bolsonaro|tarc[íi]sio|haddad|alckmin|moraes|stf|supremo|tse|congresso|senad|c[âa]mara|deputad|vereador|prefeit|governador|ministr|elei[çc]|candidat|partido|\bpt\b|\bpl\b|psol|mdb|psd|uni[ãa]o brasil|republicanos|pec\b|projeto de lei|reforma|imposto|tribut|or[çc]amento|emenda|cpi|pol[íi]cia federal|\bpf\b|opera[çc][ãa]o|corrup|impeachment|anistia|itamaraty|planalto|minist[ée]rio|tarifa|trump/i;
async function montaTend() {
  const r = await fetch("https://trends.google.com/trending/rss?geo=BR", { headers: { "user-agent": "FiscalizaBrasil/1.0", accept: "application/rss+xml, */*" }, signal: AbortSignal.timeout(5000) });
  if (!r.ok) throw new Error("trends " + r.status);
  const xml = await r.text(); const itens = [];
  for (const m of xml.matchAll(/<item>([\s\S]*?)<\/item>/g)) {
    const b = m[1]; const t = tag(b, "title"); if (!t) continue;
    const n = [...b.matchAll(/<ht:news_item>([\s\S]*?)<\/ht:news_item>/g)].map((x) => ({ t: tag(x[1], "ht:news_item_title"), u: tag(x[1], "ht:news_item_url"), s: tag(x[1], "ht:news_item_source") })).filter((x) => x.t && /^https?:/.test(x.u)).slice(0, 3);
    const d = Date.parse(tag(b, "pubDate")); const tr = tag(b, "ht:approx_traffic");
    itens.push({ t, tr, d: isNaN(d) ? null : new Date(d).toISOString(), n, pol: POLIT.test([t, ...n.map((x) => x.t)].join(" ")) ? 1 : 0 });
  }
  const vol = (x) => parseInt((x.tr || "0").replace(/\D/g, "")) || 0;
  itens.sort((a, b) => vol(b) - vol(a));
  return JSON.stringify({ gerado: new Date().toISOString(), fonte: "Google Trends · Brasil", itens: itens.slice(0, 30) });
}
async function tendencias(request, ctx) {
  const cache = caches.default; const chave = new Request(new URL("/api/tendencias?v=1", request.url).toString());
  const salvar = async () => { const body = await montaTend(); await cache.put(chave, new Response(body, { headers: { "content-type": "application/json; charset=utf-8", "cache-control": `public, max-age=${GUARDA / 1000}`, "x-gerado": String(Date.now()) } })); return body; };
  const resp = (body) => new Response(body, { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=120" } });
  const hit = await cache.match(chave);
  if (hit) { if (Date.now() - Number(hit.headers.get("x-gerado") || 0) > 10 * 6e4) ctx.waitUntil(salvar().catch(() => {})); return resp(await hit.text()); }
  try { return resp(await salvar()); } catch (e) { return new Response(JSON.stringify({ erro: String(e), itens: [] }), { status: 502, headers: { "content-type": "application/json" } }); }
}

/* ---------- fotos: busca nos sites oficiais uma vez e guarda no cache do Cloudflare ---------- */
const FOTO_HOSTS = /^(divulgacandcontas\.tse\.jus\.br|www\.camara\.leg\.br|camara\.leg\.br|www\.senado\.leg\.br|senado\.leg\.br|legis\.senado\.leg\.br|portal\.stf\.jus\.br|www\.stf\.jus\.br|ww2\.al\.rs\.gov\.br|www3\.al\.es\.gov\.br|storage2\.assembleia\.pr\.leg\.br|www\.assembleia\.pr\.leg\.br|www\.cmc\.pr\.gov\.br)$/;
// SAPL das Câmaras e Assembleias (sapl.<cidade>.<uf>.leg.br e variações): muitos só respondem por http
const SAPL_HOSTS = /^sapl\.([a-z0-9-]+\.){1,3}(leg|gov)\.br$/;
async function foto(request, ctx) {
  const u = new URL(request.url).searchParams.get("u") || "";
  let alvo; try { alvo = new URL(u); } catch (e) { return new Response("url inválida", { status: 400 }); }
  if (!((alvo.protocol === "https:" && (FOTO_HOSTS.test(alvo.hostname) || SAPL_HOSTS.test(alvo.hostname))) || (alvo.protocol === "http:" && SAPL_HOSTS.test(alvo.hostname)))) return new Response("origem não permitida", { status: 403 });
  const cache = caches.default; const chave = new Request("https://img.fiscaliza/" + encodeURIComponent(alvo.toString()));
  const hit = await cache.match(chave); if (hit) return hit;
  // 1º tenta direto no site oficial; se ele bloquear o servidor, tenta pelo wsrv.nl (serviço público de imagens)
  const tenta = async (alvoUrl, via) => {
    try {
      const r = await fetch(alvoUrl, { headers: { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", accept: "image/avif,image/webp,image/*,*/*;q=0.8", "accept-language": "pt-BR,pt;q=0.9" }, cf: { cacheTtl: 2592000, cacheEverything: true }, signal: AbortSignal.timeout(8000) });
      if (!r.ok) return { erro: via + " " + r.status };
      const buf = new Uint8Array(await r.arrayBuffer()); let tipo = r.headers.get("content-type") || "";
      const b = buf; const sniff = b[0] === 0xFF && b[1] === 0xD8 ? "image/jpeg" : b[0] === 0x89 && b[1] === 0x50 ? "image/png" : b[0] === 0x47 && b[1] === 0x49 ? "image/gif" : b[8] === 0x57 && b[9] === 0x45 ? "image/webp" : "";
      if (!tipo.startsWith("image/")) tipo = sniff;
      if (!tipo || buf.length < 200) return { erro: via + " não é imagem (" + (r.headers.get("content-type") || "?") + ", " + buf.length + " bytes)" };
      return { buf, tipo, via };
    } catch (e) { return { erro: via + " " + (e && e.name || "falhou") }; }
  };
  const U = alvo.toString(), erros = [];
  const rotas = [
    [U, "direto"],
    ["https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?container=focus&refresh=2592000&url=" + encodeURIComponent(U), "google"],
    ["https://i0.wp.com/" + U.replace(/^https?:\/\//, "") + "?ssl=1", "wp"],
    ["https://wsrv.nl/?url=" + encodeURIComponent(U) + "&n=-1", "wsrv"],
  ];
  let ok = {};
  for (const [r, via] of rotas) { ok = await tenta(r, via); if (ok.buf) break; erros.push(ok.erro); }
  if (!ok.buf) { return new Response("sem foto: " + erros.join(" | "), { status: 404, headers: { "cache-control": "public, max-age=600", "content-type": "text/plain; charset=utf-8" } }); }
  const res = new Response(ok.buf, { headers: { "content-type": ok.tipo, "cache-control": "public, max-age=2592000, immutable", "access-control-allow-origin": "*", "x-foto-via": ok.via } });
  ctx.waitUntil(cache.put(chave, res.clone()));
  return res;
}

/* ---------- endereço próprio por político e por partido (/p/c/123, /partido/PL), com prévia de link ---------- */
const ELEI = { 2022: 2040602022, 2024: 2045202024, 2026: 20322002026 };
const tit = (x) => String(x || "").toLowerCase().replace(/(^|[\s'-])([a-zà-ú])/g, (m, a, b) => a + b.toUpperCase()).replace(/\b(Da|De|Do|Das|Dos|E)\b/g, (m) => m.toLowerCase());
const CARGOS = { dep: ["Deputado federal", "Deputada federal"], sen: ["Senador", "Senadora"], gov: ["Governador", "Governadora"], vice: ["Vice-governador", "Vice-governadora"], de: ["Deputado estadual", "Deputada estadual"], dd: ["Deputado distrital", "Deputada distrital"], pref: ["Prefeito", "Prefeita"], vp: ["Vice-prefeito", "Vice-prefeita"], ver: ["Vereador", "Vereadora"] };
const cg = (k, g) => CARGOS[k][g === "F" ? 1 : 0];
async function json(env, origin, path) { const r = await env.ASSETS.fetch(new Request(origin + path)); return r.ok ? r.json() : null; }
async function quem(env, origin, parts) {
  const BR = await json(env, origin, "/data/br.json"); if (!BR) return null;
  const t = parts[0];
  if (t === "c") { const d = BR.dep.find((x) => String(x[0]) === parts[1]); return d && { nome: d[1], cargo: cg("dep", d[10]) + " (" + d[2] + "-" + d[3] + ")", foto: d[4] }; }
  if (t === "s") { const x = BR.sen.find((y) => String(y[0]) === parts[1]); return x && { nome: x[1], cargo: "Senador(a) (" + x[3] + "-" + x[4] + ")", foto: x[5] }; }
  const uf = parts[1]; if (!/^[A-Z]{2}$/.test(uf || "")) return null;
  const D = await json(env, origin, "/data/uf/" + uf + ".json"); if (!D) return null;
  const foto = (P, ano, ue) => P && P[10] ? `https://divulgacandcontas.tse.jus.br/divulga/rest/arquivo/img/${ELEI[ano]}/${P[10]}/${ue}` : "";
  let P = null, cargo = "", ano = 2022, ue = uf;
  if (t === "g") { P = (parts[3] === "26" ? BR.ufs[uf].gov26 : BR.ufs[uf].gov || [])[+parts[2]]; cargo = cg(parts[2] === "0" ? "gov" : "vice", P && P[4]) + " (" + (P ? P[2] : "") + "-" + uf + ")" + (parts[3] === "26" ? ", eleito em 2026" : ""); ano = parts[3] === "26" ? 2026 : 2022; }
  else if (t === "e" || t === "f" || t === "n") { const arr = t === "e" ? (parts[2] === "26" ? D.de26 : D.de22) : t === "f" ? D.df26 : D.se26; P = arr && arr[+parts[3]]; ano = parts[2] === "26" || t !== "e" ? 2026 : 2022;
    cargo = (t === "e" ? cg(uf === "DF" ? "dd" : "de", P && P[4]) : t === "f" ? cg("dep", P && P[4]) : cg("sen", P && P[4])) + " (" + (P ? P[2] : "") + "-" + uf + ")" + (ano === 2026 ? ", eleito em 2026" : ""); }
  else if (t === "m") { const m = D.mun && D.mun[parts[2]]; if (!m) return null; P = parts[3] === "p" ? m[1] : parts[3] === "v" ? m[2] : m[3][+parts[3]]; ano = 2024; ue = parts[2];
    cargo = cg(parts[3] === "p" ? "pref" : parts[3] === "v" ? "vp" : "ver", P && P[4]) + " de " + tit(m[0]) + " (" + (P ? P[2] : "") + ")"; }
  if (!P) return null;
  return { nome: tit(P[0]), cargo, foto: foto(P, ano, ue) };
}
async function paginaPropria(request, env, url) {
  const origin = url.origin; let rota, titulo, desc, img = origin + "/og.png", quadrada = true;
  if (url.pathname.startsWith("/partido/")) {
    const sig = decodeURIComponent(url.pathname.split("/")[2] || "").toUpperCase();
    const PT = await json(env, origin, "/data/partidos.json"); const p = PT && PT.partidos.find((x) => x.s.toUpperCase() === sig);
    if (!p) return env.ASSETS.fetch(new Request(origin + "/fiscalize"));
    rota = "#/partidos/" + encodeURIComponent(p.s); titulo = p.nome + " (" + p.s + " " + p.n + ") · Fiscaliza Brasil";
    const st = PT.stat[p.s]; desc = p.desc + (st && st.coes != null ? ` Bancada vota junto em ${String(st.coes).replace(".", ",")}% das vezes.` : "");
  } else {
    const parts = url.pathname.split("/").slice(2).filter(Boolean).map(decodeURIComponent);
    const q = await quem(env, origin, parts).catch(() => null);
    if (!q) return env.ASSETS.fetch(new Request(origin + "/fiscalize"));
    rota = "#/p/" + parts.join("/"); titulo = q.nome + " · Fiscaliza Brasil";
    desc = q.cargo + ". Como vota, presença, projetos, gastos e patrimônio, com dados oficiais.";
    if (q.foto) { img = origin + "/img?u=" + encodeURIComponent(q.foto); quadrada = false; }
  }
  const res = await env.ASSETS.fetch(new Request(origin + "/fiscalize"));
  const set = (sel, at, v) => ({ element: (el) => el.setAttribute(at, v) });
  return new HTMLRewriter()
    .on("head", { element: (el) => el.prepend(`<script>history.replaceState(null,"","/fiscalize${rota.replace(/"/g, "")}")</script><link rel="canonical" href="${origin}${url.pathname}">`, { html: true }) })
    .on("title", { element: (el) => el.setInnerContent(titulo) })
    .on('meta[name="description"]', set(0, "content", desc))
    .on('meta[property="og:title"]', set(0, "content", titulo))
    .on('meta[property="og:description"]', set(0, "content", desc))
    .on('meta[property="og:url"]', set(0, "content", origin + url.pathname))
    .on('meta[property="og:image"]', set(0, "content", img))
    .on('meta[property="og:image:width"]', { element: (el) => { if (!quadrada) el.remove(); } })
    .on('meta[property="og:image:height"]', { element: (el) => { if (!quadrada) el.remove(); } })
    .transform(new Response(res.body, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=600" } }));
}

/* ---------- endereço próprio para cada votação (/votacao/C/1127/PR): prévia no WhatsApp com o tema e o placar ---------- */
async function paginaVotacao(request, env, url) {
  const origin = url.origin; const [, , casa, i, uf0] = url.pathname.split("/"); const C = casa !== "S"; const uf = /^[A-Z]{2}$/.test(uf0 || "") ? uf0 : "";
  const VL = await json(env, origin, C ? "/data/camara_votacoes.json" : "/data/senado_votacoes.json"); const x = VL && VL[+i];
  if (!x) return env.ASSETS.fetch(new Request(origin + "/fiscalize"));
  const tit0 = (C ? x[5] : x[2]) || "Votação", em = String((C ? (x[6] || x[7]) : (x[3] || x[4])) || "").replace(/\s+/g, " ").trim();
  const apr = C ? x[2] === "1" : x[5] === "A", rej = C ? x[2] === "0" : x[5] === "R", sim = C ? x[3] : x[7], nao = C ? x[4] : x[8];
  const dt = String(x[1]).split("-").reverse().join("/");
  const titulo = `${tit0}: como votou cada ${C ? "deputado" : "senador"}${uf ? " de " + uf : ""} · Fiscaliza Brasil`;
  const oq = String((C ? x[7] : x[4]) || "").replace(/\s+/g, " ").trim();
  const desc = `${C ? "Câmara" : "Senado"}, ${dt}. ${oq ? oq.slice(0, 140) + (oq.length > 140 ? "…" : "") + " " : ""}${apr ? "Aprovado" : rej ? "Rejeitado" : "Resultado"}${!C && x[6] === "S" ? " em votação secreta" : ` por ${sim} a ${nao}`}. Tema: ${em.slice(0, 140)}${em.length > 140 ? "…" : ""}`;
  const rota = "#/votacao/" + (C ? "C" : "S") + "/" + (+i) + (uf ? "/" + uf : "");
  const res = await env.ASSETS.fetch(new Request(origin + "/fiscalize")); const esc2 = (t) => String(t).replace(/"/g, "&quot;");
  const set = (at, v) => ({ element: (el) => el.setAttribute(at, v) });
  return new HTMLRewriter()
    .on("head", { element: (el) => el.prepend(`<script>history.replaceState(null,"","/fiscalize${rota}")</script><link rel="canonical" href="${origin}${url.pathname}">`, { html: true }) })
    .on("title", { element: (el) => el.setInnerContent(titulo) })
    .on('meta[name="description"]', set("content", esc2(desc)))
    .on('meta[property="og:title"]', set("content", esc2(titulo)))
    .on('meta[property="og:description"]', set("content", esc2(desc)))
    .on('meta[property="og:url"]', set("content", origin + url.pathname))
    .on('meta[property="og:image"]', set("content", origin + "/og.png"))
    .transform(new Response(res.body, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=3600" } }));
}

/* ---------- endereço próprio para estado e cidade (/uf/PR, /cidade/PR/75353), para aparecer no Google ---------- */
async function paginaLugar(request, env, url) {
  const origin = url.origin; const parts = url.pathname.split("/").filter(Boolean).map(decodeURIComponent);
  const uf = (parts[1] || "").toUpperCase(); if (!/^[A-Z]{2}$/.test(uf)) return env.ASSETS.fetch(new Request(origin + "/fiscalize"));
  const BR = await json(env, origin, "/data/br.json"); const U = BR && BR.ufs[uf]; if (!U) return env.ASSETS.fetch(new Request(origin + "/fiscalize"));
  let rota, titulo, desc;
  if (parts[0] === "uf") { rota = "#/uf/" + uf; titulo = U.nome + ": deputados, senadores e governador · Fiscaliza Brasil";
    desc = `Quem representa ${U.nome}: deputados federais e estaduais, senadores e governador. Como votam, presença, projetos, emendas, gastos e patrimônio, com dados oficiais.`; }
  else { const D = await json(env, origin, "/data/uf/" + uf + ".json"); const m = D && D.mun && D.mun[parts[2]]; if (!m) return env.ASSETS.fetch(new Request(origin + "/fiscalize"));
    const nome = tit(m[0]); rota = "#/cidade/" + uf + "/" + parts[2]; titulo = `${nome} (${uf}): prefeito, vereadores e deputados · Fiscaliza Brasil`;
    desc = `${nome} (${uf}): prefeito${m[1] ? " " + tit(m[1][0]) : ""}, os ${m[3].length} vereadores, os deputados e senadores mais votados na cidade e as emendas parlamentares que chegaram, com dados oficiais.`; }
  const res = await env.ASSETS.fetch(new Request(origin + "/fiscalize"));
  const set = (at, v) => ({ element: (el) => el.setAttribute(at, v) });
  return new HTMLRewriter()
    .on("head", { element: (el) => el.prepend(`<script>history.replaceState(null,"","/fiscalize${rota.replace(/"/g, "")}")</script><link rel="canonical" href="${origin}${url.pathname}">`, { html: true }) })
    .on("title", { element: (el) => el.setInnerContent(titulo) })
    .on('meta[name="description"]', set("content", desc))
    .on('meta[property="og:title"]', set("content", titulo))
    .on('meta[property="og:description"]', set("content", desc))
    .on('meta[property="og:url"]', set("content", origin + url.pathname))
    .on('meta[property="og:image"]', set("content", origin + "/og.png"))
    .transform(new Response(res.body, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=3600" } }));
}

/* ---------- sonda: testa, a partir do centro de dados do Cloudflare mais próximo de quem abre, se as Assembleias respondem (lista fixa, sem parâmetros) ---------- */
const SONDA_BR = [
  "https://dadosabertos.almg.gov.br/ws/deputados/em_exercicio?formato=json",
  "https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?tp=10&formato=json&ano=2026",
  "https://dadosabertos.alepe.pe.gov.br/", "https://www.alepe.pe.gov.br/",
  "https://www.al.rs.gov.br/", "https://ww4.al.rs.gov.br/", "https://www.al.es.gov.br/", "https://www3.al.es.gov.br/",
  "https://www.al.ma.leg.br/", "https://sapl.al.ma.leg.br/api/parlamentares/parlamentar/?page_size=1",
  "https://www.al.ap.gov.br/", "https://sapl.al.ap.leg.br/api/parlamentares/parlamentar/?page_size=1", "https://www.cl.df.gov.br/",
];
async function sondaBR(request) {
  const R = await Promise.all(SONDA_BR.map(async (u) => {
    const t0 = Date.now();
    try { const r = await fetch(u, { headers: { "user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0)" }, signal: AbortSignal.timeout(12000) }); const tx = await r.text();
      return { u, st: r.status, ms: Date.now() - t0, tipo: r.headers.get("content-type"), ini: tx.slice(0, 160) }; }
    catch (e) { return { u, erro: String(e).slice(0, 120), ms: Date.now() - t0 }; }
  }));
  return new Response(JSON.stringify({ local: request.cf && request.cf.colo, pais: request.cf && request.cf.country, R }, null, 1), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    // a antiga página "Paraná em detalhe" virou parte das fichas nacionais
    if (/^\/parana(\.html)?\/?$/.test(url.pathname)) return Response.redirect(url.origin + "/fiscalize#/uf/PR", 301);
    if (url.pathname === "/api/noticias") return noticias(request, ctx);
    if (url.pathname === "/api/tendencias") return tendencias(request, ctx);
    if (url.pathname === "/img") return foto(request, ctx);
    if (url.pathname === "/api/sonda-br") return sondaBR(request);
    if (url.pathname.startsWith("/p/") || url.pathname.startsWith("/partido/")) return paginaPropria(request, env, url);
    if (/^\/(uf|cidade)\//.test(url.pathname)) return paginaLugar(request, env, url);
    if (/^\/votacao\/[CS]\/\d+/.test(url.pathname)) return paginaVotacao(request, env, url);
    const res = await env.ASSETS.fetch(request);
    if (!(res.headers.get("content-type") || "").includes("text/html")) return res;
    // prévia de links (WhatsApp, Instagram etc.): o endereço da imagem e da página precisa ser completo
    const abs = (el, at) => { const v = el.getAttribute(at); if (v && v.startsWith("/")) el.setAttribute(at, url.origin + v); };
    return new HTMLRewriter()
      .on('meta[property="og:image"]', { element: (el) => abs(el, "content") })
      .on('meta[property="og:url"]', { element: (el) => abs(el, "content") })
      .transform(res);
  },
};
