/* Ficha (crachá) do político: cabeçalho, abas e o formulário "Reportar erro".
   Usa as funções e dados globais de fiscalize.html ($, M, esc, norm, title, brl, mil, BR, loadBR, loadUF, getJSON...). */
"use strict";
/* Virada de mandato: os governadores eleitos em 2026 assumem em 6/01/2027 (EC 111/2021) e deputados e senadores em 1º/02/2027. A partir dessas datas o site passa sozinho a tratá-los como em exercício. */
const POSSE = { gov: "2027-01-06", leg: "2027-02-01" };
function empossado(k) { return Date.now() >= Date.parse(POSSE[k] + "T00:00:00-03:00"); }
const __pb = document.createElement("style"); __pb.textContent = ".lai{margin-top:18px;padding-top:14px;border-top:1px solid rgba(127,127,127,.25)}.lai .chip{cursor:pointer}.pbox{display:grid;gap:8px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.75);border:1px solid rgba(11,11,12,.08)}.pbox b{font-family:var(--f-display)}.mbars{display:flex;align-items:flex-end;gap:3px;height:96px;padding:4px 0;border-bottom:1px solid rgba(11,11,12,.12)}.mbars i{flex:1;background:rgba(11,11,12,.25);border-radius:3px 3px 0 0;min-width:4px}.mbars i.top{background:#B3261E}"; document.head.append(__pb);
const SUBSIDIO = 46366.19; // Decreto Legislativo 172/2022, desde 01/02/2025 (deputados e senadores)
const DEP_GAB = 165806.07, DEP_MORADIA = 4253.00; // Câmara, transparência/gastos-parlamentares
const LINK_GASTOS_CAM = '<a href="https://www.camara.leg.br/transparencia/gastos-parlamentares" target="_blank" rel="noopener">Câmara · Gastos parlamentares</a>';
const LINK_CEAPS = '<a href="https://www12.senado.leg.br/transparencia/sen/" target="_blank" rel="noopener">Senado · Transparência (CEAPS)</a>';
const CC = {}; const SS = {}; const PAT = {}; let VCAM = null, VSEN = null;
const loadC = async (uf) => CC[uf] || (CC[uf] = await getJSON("data/c/" + uf + ".json"));
const loadS = async (uf) => SS[uf] || (SS[uf] = await getJSON("data/s/" + uf + ".json"));
const loadPat = async (uf) => PAT[uf] || (PAT[uf] = await getJSON("data/pat/" + uf + ".json").catch(() => ({})));
const loadVC = async () => VCAM || (VCAM = await getJSON("data/camara_votacoes.json"));
const loadVS = async () => VSEN || (VSEN = await getJSON("data/senado_votacoes.json"));
const CAMP = {}; const loadCamp = async (f) => CAMP[f] || (CAMP[f] = await getJSON("data/camp/" + f + ".json").then((x) => x.dep || {}).catch(() => ({})));
const VMA = {}; const loadVMa = async (uf) => VMA[uf] || (VMA[uf] = await getJSON("data/vm/" + uf + ".json").then((x) => x.anos || {}).catch(() => ({})));
// deputado federal ou senador eleito em 2022: acha o número do TSE pelo nome civil na lista de candidatos do estado
async function campFederal(uf, civil, cg) { const A = (await loadVMa(uf))["2022"]; if (!A || !A[cg]) return null; const n = norm(civil);
  const x = A[cg].find((c) => c[3] && norm(c[1]) === n); if (!x) return null; return (await loadCamp(uf))[x[4]] || null; }
const VV = {}; const loadV = async (uf) => VV[uf] || (VV[uf] = await getJSON("data/v/" + uf + ".json").catch(() => ({})));
const keyTSE = (civil, nasc) => String(civil || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toUpperCase().replace(/[^A-Z ]/g, "").trim() + "|" + (nasc || "");
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0) + "%";
const VOTO = { S: ["Sim", "ok"], N: ["Não", "no"], A: ["Abstenção", ""], O: ["Obstrução", "warn"], P: ["Presidiu", ""], V: ["Votou (secreta)", ""], R: ["Presidiu", ""], "?": ["Outro", ""] };
const bar = (v, max) => `<span class="hb"><i style="width:${max ? Math.max(2, (v / max) * 100) : 0}%"></i></span>`;

(function css() {
  const s = document.createElement("style");
  s.textContent = `.tabs2{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;padding:2px;margin:0 -2px}.tabs2::-webkit-scrollbar{display:none}
  .tabs2 button{flex:none;border:0;background:none;padding:9px 14px;border-radius:999px;font-weight:700;font-size:.9rem;color:var(--muted)}
  .tabs2 button[aria-selected="true"]{background:var(--ink);color:#fff}
  .hb{display:block;height:8px;border-radius:4px;background:rgba(11,11,12,.08);overflow:hidden}.hb i{display:block;height:100%;background:var(--ink);border-radius:4px}
  .tl{display:grid;gap:8px}.tl>div{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;align-items:center}.tl>div .hb{grid-column:1/-1}
  .tl b{font-variant-numeric:tabular-nums;font-family:var(--f-mono);font-size:.82rem}
  .it{padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.75);border:1px solid rgba(11,11,12,.08);display:grid;gap:5px;min-width:0}
  .it .hd{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;flex-wrap:wrap}
  .it .cd{font-family:var(--f-mono);font-size:.8rem;font-weight:600}
  .vt{font-size:.74rem;font-weight:800;padding:3px 10px;border-radius:999px;border:1.5px solid currentColor;white-space:nowrap}
  .vt.ok{color:var(--verde)}.vt.no{color:var(--verm)}.vt.warn{color:#8a6d00}.vt.n0{color:var(--muted)}
  .sel{display:flex;gap:8px;flex-wrap:wrap}.sel select,.sel input{padding:9px 12px;border-radius:999px;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.85);font:inherit;min-width:0}
  .sel input{flex:1 1 200px}.sel label{display:flex;gap:6px;align-items:center;white-space:nowrap;font-size:.9rem}
  .bars{display:flex;align-items:flex-end;gap:10px;height:170px;padding-top:8px}
  .bars>div{flex:1;display:grid;justify-items:center;gap:4px;align-content:end;height:100%;min-width:0}
  .bars i{display:block;width:100%;max-width:56px;background:var(--ink);border-radius:8px 8px 3px 3px}
  .bars b{font-family:var(--f-mono);font-size:.68rem;white-space:nowrap}.bars small{font-size:.74rem;color:var(--muted);text-align:center;line-height:1.2}
  .kw{display:flex;flex-wrap:wrap;gap:6px}
  dialog.rep{border:0;border-radius:24px;padding:0;max-width:min(480px,calc(100% - 32px));width:100%;background:transparent}
  dialog.rep::backdrop{background:rgba(11,11,12,.35);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}
  dialog.rep form{display:grid;gap:10px;padding:20px;border-radius:24px}
  dialog.rep textarea,dialog.rep input{width:100%;padding:12px;border-radius:14px;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.9);font:inherit}
  .lst{display:grid;gap:8px}`;
  document.head.appendChild(s);
})();

/* -------- reportar erro -------- */
let SBC = null;
function sbClient() { const C = window.FB_CFG || {}; if (!SBC && C.url && C.key && window.supabase) SBC = supabase.createClient(C.url, C.key, { auth: { persistSession: false } }); return SBC; }
function reportar(ctx) {
  let d = document.getElementById("repdlg");
  if (!d) { d = document.createElement("dialog"); d.id = "repdlg"; d.className = "rep"; document.body.appendChild(d); }
  d.innerHTML = `<form method="dialog" class="glass"><h2>Reportar erro</h2><p class="muted small" style="margin:0">Sobre: <b>${esc(ctx)}</b>. Diga o que está errado e, se puder, a fonte correta.</p>
    <textarea id="rt" rows="4" required placeholder="O que está errado?"></textarea><input id="rc" type="text" placeholder="Seu e-mail ou @ (opcional, para resposta)">
    <div class="err small" id="re" style="color:var(--verm);min-height:18px"></div>
    <div class="btns"><button class="btn" id="rs" value="send">Enviar</button><button class="btn o" value="cancel" formnovalidate>Cancelar</button></div></form>`;
  d.querySelector("form").onsubmit = async (e) => {
    if (e.submitter && e.submitter.value === "cancel") return;
    e.preventDefault(); const t = d.querySelector("#rt").value.trim(); if (!t) return;
    const sb = sbClient(); const b = d.querySelector("#rs"); b.disabled = true;
    try {
      if (!sb) throw new Error("Envio indisponível no momento.");
      const r = await sb.from("reportes").insert({ pagina: location.href.slice(0, 300), sobre: ctx.slice(0, 200), texto: t.slice(0, 2000), contato: d.querySelector("#rc").value.trim().slice(0, 200) });
      if (r.error) throw r.error;
      d.close(); toast2("Obrigado! Vamos conferir.");
    } catch (err) { d.querySelector("#re").textContent = "Não foi possível enviar: " + (err.message || err); b.disabled = false; }
  };
  d.showModal();
}
function toast2(m) { let t = document.getElementById("t2"); if (!t) { t = document.createElement("div"); t.id = "t2"; t.style.cssText = "position:fixed;left:50%;transform:translateX(-50%);bottom:calc(96px + env(safe-area-inset-bottom,0px));z-index:60;background:#0B0B0C;color:#fff;padding:10px 18px;border-radius:999px;font-weight:600;opacity:0;transition:opacity .25s"; document.body.appendChild(t); } t.textContent = m; t.style.opacity = 1; setTimeout(() => (t.style.opacity = 0), 2400); }

/* -------- seções -------- */
function secResumo(o, X, casa) {
  const k = [];
  if (X && X.sess && X.sess[1]) k.push(["Presença nas sessões", pct(X.sess[0], X.sess[1]), `presente em ${mil(X.sess[0])} de ${mil(X.sess[1])} dias com sessão deliberativa do Plenário desde que assumiu`]);
  if (X && X.pres && X.pres[1]) k.push(["Participação nas votações", pct(X.pres[0], X.pres[1]), `votou em ${mil(X.pres[0])} de ${mil(X.pres[1])} votações nominais do Plenário desde que assumiu`]);
  if (X && (X.fp || o.cpp)) { const a = X.fp ? (X.fp.match(/g/g) || []).length : o.cpp.a, c = X.fp ? (X.fp.match(/r/g) || []).length : o.cpp.c; if (a + c) k.push(["Votou com o partido", pct(a, a + c), `contra o partido ${mil(c)} ${c === 1 ? "vez" : "vezes"}, em ${mil(a + c)} votações com posição clara do partido`]); }
  if (casa === "C" && X && X.v && VCAM) { let a = 0, n = 0; VCAM.forEach((x, i) => { const g = x[8], v = X.v[i]; if ((g === "Sim" || g === "Não") && (v === "S" || v === "N")) { n++; if ((g === "Sim") === (v === "S")) a++; } }); if (n) k.push(["Votou com o governo", pct(a, n), `em ${mil(n)} votações em que o governo orientou Sim ou Não`]); }
  if (o.emAut) k.push(["Emendas pagas", brl(o.emAut.t), `para ${mil(o.emAut.n)} ${o.emAut.n === 1 ? "cidade" : "cidades"} desde 2023`]);
  if (X && X.au) { const c = X.au.c || {}; const nprop = ["PL", "PLP", "PEC", "PDL", "PRS"].reduce((a, t) => a + (c[t] || 0), 0); k.push(["Projetos apresentados", mil(nprop), "PL, PLP, PEC e PDL desde 2023 (autor ou coautor)"]); }
  if (X && X.cota) { const tot = Object.values(X.cota.a).reduce((a, t) => a + Object.values(t).reduce((x, y) => x + y, 0), 0); k.push(["Cota parlamentar gasta", brl(tot), "reembolsos de 2023 a 2026"]); }
  else if (casa) k.push(["Cota parlamentar gasta", "—", "sem gastos registrados no período"]);
  if (X && X.disc) k.push(["Discursos", mil(X.disc.n), "desde fevereiro de 2023"]);
  if (o.vc && o.vc.v) k.push(["Votos em " + o.ano, mil(o.vc.v[0]), (o.vc.v[1] != null ? fx1c(o.vc.v[1]) + (o.vc.v[2] === 0 ? "% dos votos nominais no estado" : "% dos votos válidos") : "")]);
  if (o.vc && o.vc.c) k.push(["Campanha", brl(o.vc.c[0]), "arrecadados · " + brl(o.vc.c[2]) + " gastos"]);
  const p = o.patList && o.patList.length ? o.patList[o.patList.length - 1] : null;
  if (p) k.push(["Patrimônio declarado", brl(p[6]), "à Justiça Eleitoral em " + p[0]]);
  return k;
}
function kvHTML(kv) { return `<div class="kv">${kv.map(([l, v, s]) => `<div><div class="l">${l}</div><div class="v">${String(v).replace(/([^<])\//g, "$1/<wbr>")}</div>${s ? `<div class="s">${s}</div>` : ""}</div>`).join("")}</div>`; }

let COTA_MEDIA = null;
const loadCotaMedia = async () => COTA_MEDIA || (COTA_MEDIA = await getJSON("data/cota_media.json").catch(() => ({})));
function secCusto(o, X, casa) {
  let h = `<div class="kv"><div><div class="l">Salário bruto</div><div class="v">${brl(SUBSIDIO)}<span class="s"> /mês</span></div><div class="s">${brl(SUBSIDIO / 30)} por dia · Decreto Legislativo 172/2022</div></div>`;
  if (casa === "C") h += `<div><div class="l">Verba de gabinete</div><div class="v">até ${brl(DEP_GAB)}<span class="s"> /mês</span></div><div class="s">para contratar até 25 secretários</div></div>
     <div><div class="l">Moradia</div><div class="v">${brl(DEP_MORADIA)}<span class="s"> /mês</span></div><div class="s">auxílio-moradia, ou apartamento funcional</div></div>`;
  h += `</div>`;
  if (X && X.cota) {
    const anos = Object.entries(X.cota.a).sort(); const tots = anos.map(([a, t]) => [a, Object.values(t).reduce((x, y) => x + y, 0)]); const mx = Math.max(...tots.map((t) => t[1]), 1);
    h += `<h3 style="margin-top:6px">Cota parlamentar por ano</h3><div class="bars">${tots.map(([a, v]) => `<div><b>${brl(v)}</b><i style="height:${Math.max(3, (v / mx) * 120)}px"></i><small>${a}</small></div>`).join("")}</div>`;
    const tip = {}; anos.forEach(([, t]) => Object.entries(t).forEach(([k, v]) => (tip[k] = (tip[k] || 0) + v)));
    const tl = Object.entries(tip).sort((a, b) => b[1] - a[1]).slice(0, 7); const m2 = tl.length ? tl[0][1] : 1;
    h += `<h3>Onde gastou (2023–2026)</h3><div class="tl">${tl.map(([k, v]) => `<div><span>${esc(k)}</span><b>${brl(v)}</b>${bar(v, m2)}</div>`).join("")}</div>`;
    const total = tots.reduce((a, t) => a + t[1], 0); const md = COTA_MEDIA && COTA_MEDIA[casa];
    if (md) { const r = total / md.mediana; const txt = r >= 1.15 ? `<b style="color:#B3261E">${Math.round((r - 1) * 100)}% acima</b> do gasto típico` : r <= 0.85 ? `<b style="color:#14703C">${Math.round((1 - r) * 100)}% abaixo</b> do gasto típico` : "perto do gasto típico";
      h += `<div class="pbox"><b>Gastou ${brl(total)} de cota desde 2023: ${txt} ${casa === "C" ? "de um deputado" : "de um senador"}</b><span class="small muted">Gasto típico (mediana) na ${casa === "C" ? "Câmara" : "no Senado"}: ${brl(md.mediana)}. ${md.p90 && total >= md.p90 ? "Está entre os 10% que mais gastaram." : ""} Quem assumiu no meio do mandato tende a ter gasto menor.</span></div>`; }
    if (X.cota.m) { const ms = Object.entries(X.cota.m).sort().slice(-24); const mm = Math.max(...ms.map((x) => x[1]), 1); const top = ms.slice().sort((a, b) => b[1] - a[1])[0];
      h += `<h3>Mês a mês (últimos ${ms.length} meses)</h3><div class="mbars">${ms.map(([k, v]) => `<i title="${k}: ${brl(v)}" style="height:${Math.max(2, (v / mm) * 90)}px"${v === top[1] ? ' class="top"' : ""}></i>`).join("")}</div><p class="small muted" style="margin:0">Maior gasto: ${brl(top[1])} em ${top[0].slice(5)}/${top[0].slice(0, 4)}.</p>`; }
    if (X.cota.f && X.cota.f.length && total) { const f0 = X.cota.f.filter((f) => f[0])[0]; const pf = f0 ? f0[1] / total : 0; if (pf >= 0.15) h += `<div class="note">${Math.round(pf * 100)}% de toda a cota foi paga a um só fornecedor: <b>${esc(title(f0[0]))}</b>.</div>`; }
    if (X.cota.f && X.cota.f.length) h += `<h3>Maiores fornecedores</h3><div class="tl">${X.cota.f.filter((f) => f[0]).slice(0, 6).map(([n, v]) => `<div><span>${esc(title(n))}</span><b>${brl(v)}</b>${bar(v, X.cota.f[0][1])}</div>`).join("")}</div>`;
  } else h += `<p class="muted">Sem gastos de cota registrados no período.</p>`;
  h += `<p class="src">Fontes: ${casa === "C" ? LINK_GASTOS_CAM : LINK_CEAPS}. Cota = reembolsos de despesas do mandato (passagens, escritório, divulgação, combustível etc.).</p>`;
  return h;
}

function secVotos(X, VL, casa, el, part) {
  const v = X.v || ""; const its = []; const pos = part && typeof posPartido === "function" ? posPartido(part, casa) : "";
  const cor = (i) => { if (X.fp) return X.fp[i] === "g" ? "g" : X.fp[i] === "r" ? "r" : ""; const c = v[i], p = pos[i]; return (c === "S" || c === "N") && (p === "S" || p === "N") ? (c === p ? "g" : "r") : ""; };
  for (let i = v.length - 1; i >= 0; i--) if (v[i] !== "-") its.push(i);
  if (!its.length) { el.innerHTML = '<p class="muted">Nenhum voto nominal registrado no período.</p>'; return; }
  const anos = [...new Set(its.map((i) => VL[i][1].slice(0, 4)))];
  const temas = casa === "C" ? [...new Set(its.flatMap((i) => VL[i][9] || []))].sort() : [];
  const cnt = {}; its.forEach((i) => (cnt[v[i]] = (cnt[v[i]] || 0) + 1));
  let pa = 0, pc = 0; its.forEach((i) => { const k = cor(i); if (k === "g") pa++; else if (k === "r") pc++; });
  el.innerHTML = `<div class="chips">${Object.entries(cnt).sort((a, b) => b[1] - a[1]).map(([c, n]) => `<span class="chip">${(VOTO[c] || [c])[0]} ${mil(n)}</span>`).join("")}</div>
    ${pa + pc ? `<div class="pbox"><b>Votou com o ${esc(part)} em <span style="color:#14703C">${Math.round((100 * pa) / (pa + pc))}%</span> das vezes</b><span class="meter"><span class="g" style="width:${(100 * pa) / (pa + pc)}%"></span><span class="r" style="width:${(100 * pc) / (pa + pc)}%"></span></span><span class="small muted"><span class="tagv g">● ${mil(pa)} com o partido</span> <span class="tagv r">● ${mil(pc)} contra o partido</span> · posição do partido = voto da maioria da bancada</span></div>` : ""}
    <div class="sel"><select id="fa" aria-label="Ano"><option value="">Todos os anos</option>${anos.map((a) => `<option>${a}</option>`).join("")}</select>
    ${temas.length ? `<select id="ft" aria-label="Tema"><option value="">Todos os temas</option>${temas.map((t) => `<option>${esc(t)}</option>`).join("")}</select>` : ""}
    <input id="fq" type="search" placeholder="Buscar pelo tema ou número do projeto" aria-label="Buscar"></div><div class="lst" id="vl"></div>`;
  const ptag = (i) => { const k = cor(i); return k === "g" ? '<span class="tagv g">● Com o partido</span>' : k === "r" ? '<span class="tagv r">● Contra o partido</span>' : ""; };
  let lim = 25;
  const draw = () => {
    const a = $("#fa").value, t = $("#ft") ? $("#ft").value : "", q = norm($("#fq").value);
    const f = its.filter((i) => { const x = VL[i]; if (a && !x[1].startsWith(a)) return false; if (t && !(x[9] || []).includes(t)) return false;
      if (q && !norm(casa === "C" ? x[5] + " " + x[6] + " " + x[7] : x[2] + " " + x[3] + " " + x[4]).includes(q)) return false; return true; });
    $("#vl").innerHTML = `<p class="muted small" style="margin:0">${mil(f.length)} votações</p>` + f.slice(0, lim).map((i) => {
      const x = VL[i], c = v[i], vv = VOTO[c] || [c, ""];
      if (casa === "C") return `<div class="it"><div class="hd"><span class="cd">${esc(x[5] || "Votação")} · ${new Date(x[1] + "T12:00").toLocaleDateString("pt-BR")}</span><span style="display:flex;gap:6px;align-items:center">${ptag(i)}<span class="vt ${vv[1] || "n0"}">${vv[0]}</span></span></div>
        <div>${esc(x[6] || x[7])}</div><div class="small muted">${x[2] === "1" ? "Aprovado" : x[2] === "0" ? "Rejeitado" : ""} · Sim ${x[3]} × Não ${x[4]}${x[8] ? " · Governo orientou " + esc(x[8]) : ""}</div>
        ${(x[9] || []).length ? `<div class="chips">${x[9].map((t) => `<span class="chip">${esc(t)}</span>`).join("")}</div>` : ""}</div>`;
      return `<div class="it"><div class="hd"><span class="cd">${esc(x[2])} · ${new Date(x[1] + "T12:00").toLocaleDateString("pt-BR")}</span><span style="display:flex;gap:6px;align-items:center">${ptag(i)}<span class="vt ${vv[1] || "n0"}">${vv[0]}</span></span></div>
        <div>${esc(x[3] || x[4])}</div><div class="small muted">${x[5] === "A" ? "Aprovado" : x[5] === "R" ? "Rejeitado" : ""}${x[6] === "S" ? " · votação secreta" : ` · Sim ${x[7]} × Não ${x[8]}`}</div></div>`;
    }).join("") + (f.length > lim ? `<button class="btn o more" id="vm">Ver mais</button>` : "");
    const m = $("#vm"); if (m) m.onclick = () => { lim += 40; draw(); };
  };
  ["#fa", "#ft", "#fq"].forEach((s) => { const e = $(s); if (e) e.oninput = () => { lim = 25; draw(); }; });
  draw();
}

function secProjetos(X, casa, el) {
  const c = (X.au && X.au.c) || {}; const L = (X.au && X.au.l) || [];
  const tipos = Object.entries(c).sort((a, b) => b[1] - a[1]);
  const NOMES = { PL: "Projetos de lei", PLP: "Leis complementares", PEC: "Emendas à Constituição", PDL: "Decretos legislativos", REQ: "Requerimentos", RIC: "Pedidos de informação", INC: "Indicações", EMC: "Emendas", RQS: "Requerimentos", PRS: "Resoluções" };
  const top = tipos.filter(([t]) => NOMES[t]).slice(0, 6);
  if (!L.length && !top.length) { el.innerHTML = '<p class="muted">Nenhuma proposição de autoria registrada desde 2023.</p>'; return; }
  const temas = casa === "C" ? [...new Set(L.flatMap((p) => p[8] || []))].sort() : [];
  el.innerHTML = `${kvHTML(top.map(([t, n]) => [NOMES[t] || t, mil(n), t]))}
    <div class="sel">${temas.length ? `<select id="pt" aria-label="Tema"><option value="">Todos os temas</option>${temas.map((t) => `<option>${esc(t)}</option>`).join("")}</select>` : ""}
     <label class="ck" style="display:flex;gap:6px;align-items:center;font-size:.9rem"><input type="checkbox" id="p1"> Só como autor principal</label>
     <input id="pq" type="search" placeholder="Buscar na ementa" aria-label="Buscar"></div><div class="lst" id="pl"></div>`;
  let lim = 20;
  const draw = () => {
    const t = $("#pt") ? $("#pt").value : "", q = norm($("#pq").value), only = $("#p1").checked;
    const f = L.filter((p) => casa === "C" ? (!t || (p[8] || []).includes(t)) && (!only || p[7]) && (!q || norm(p[5]).includes(q)) : (!only || /^Senador/.test(p[5] || "")) && (!q || norm(p[1]).includes(q)));
    $("#pl").innerHTML = `<p class="muted small" style="margin:0">${mil(f.length)} propostas (PL, PLP, PEC, PDL)</p>` + f.slice(0, lim).map((p) => casa === "C"
      ? `<div class="it"><div class="hd"><a class="cd" href="https://www.camara.leg.br/propostas-legislativas/${p[0]}" target="_blank" rel="noopener">${p[1]} ${p[2]}/${p[3]}</a><span class="small muted">${new Date(p[4] + "T12:00").toLocaleDateString("pt-BR")}${p[7] ? " · autor principal" : " · coautor"}</span></div><div>${esc(p[5])}</div><div class="small muted">${esc(p[6])}</div>${(p[8] || []).length ? `<div class="chips">${p[8].map((x) => `<span class="chip">${esc(x)}</span>`).join("")}</div>` : ""}</div>`
      : `<div class="it"><div class="hd"><span class="cd">${esc(p[0])}</span><span class="small muted">${p[2] ? new Date(p[2] + "T12:00").toLocaleDateString("pt-BR") : ""}</span></div><div>${esc(p[1])}</div><div class="small muted">${esc(p[3])}${p[4] === "Sim" ? " · tramitando" : ""}</div></div>`).join("") + (f.length > lim ? `<button class="btn o more" id="pm">Ver mais</button>` : "");
    const m = $("#pm"); if (m) m.onclick = () => { lim += 30; draw(); };
  };
  ["#pt", "#pq", "#p1"].forEach((s) => { const e = $(s); if (e) e.oninput = e.onchange = () => { lim = 20; draw(); }; });
  draw();
}

function secDisc(X) {
  const d = X.disc; if (!d || !d.n) return '<p class="muted">Nenhum discurso registrado desde 2023.</p>';
  const anos = Object.entries(d.ano).sort(); const mx = Math.max(...anos.map((a) => a[1]), 1);
  return `${kvHTML([["Discursos", mil(d.n), "desde fevereiro de 2023"], ...Object.entries(d.tipos).slice(0, 2).map(([t, n]) => [esc(t || "Outros"), mil(n), ""])])}
   <div class="bars" style="height:130px">${anos.map(([a, n]) => `<div><b>${n}</b><i style="height:${Math.max(3, (n / mx) * 90)}px"></i><small>${a}</small></div>`).join("")}</div>
   ${d.kw.length ? `<h3>Assuntos mais citados</h3><div class="kw">${d.kw.map(([k, n]) => `<span class="chip">${esc(k)} · ${n}</span>`).join("")}</div>` : ""}
   <h3>Últimos discursos</h3><div class="lst">${d.ult.map((u) => `<div class="it"><span class="cd">${new Date(u[0] + "T12:00").toLocaleDateString("pt-BR")} · ${esc(u[1])}</span><div>${esc(u[2] || "Sem resumo oficial.")}</div></div>`).join("")}</div>`;
}

function secPat(list) {
  if (!list || !list.length) return '<p class="muted">Sem histórico encontrado no TSE (2014 a 2026).</p>';
  const vs = list.filter((p) => p[6] > 0); const mx = Math.max(...list.map((p) => p[6]), 1);
  let h = vs.length ? `<div class="bars">${list.map((p) => `<div><b>${p[6] ? brl(p[6]) : "—"}</b><i style="height:${Math.max(3, (p[6] / mx) * 120)}px"></i><small>${p[0]}</small></div>`).join("")}</div>` : "";
  if (vs.length >= 2) { const a = vs[0], b = vs[vs.length - 1]; h += `<p class="small" style="margin:0">De ${a[0]} para ${b[0]}, o patrimônio declarado ${b[6] >= a[6] ? "aumentou" : "diminuiu"} ${Math.abs(Math.round((b[6] / a[6] - 1) * 100))}%, em valores da época, sem correção pela inflação.</p>`; }
  h += `<h3>Candidaturas</h3><div class="lst">${list.slice().reverse().map((p) => `<div class="it"><div class="hd"><span class="cd">${p[0]} · ${esc(p[1])}</span><span class="vt ${/ELEITO/.test(p[5]) && !/NÃO/.test(p[5]) ? "ok" : "n0"}">${esc(title(p[5] || "—"))}</span></div><div class="small muted">${esc(title(p[3]))} · ${esc(p[4])} · bens declarados: ${p[6] ? brl(p[6]) : "nenhum"}</div></div>`).join("")}</div>`;
  return h + `<p class="src">Fonte: ${FONTE_TSE}. Valores declarados pelo próprio candidato, sem correção.</p>`;
}

function secCamp(vc, t, cp) {
  let h = "";
  if (vc.v) h += kvHTML([["Votos recebidos", mil(vc.v[0]), (vc.v[1] != null ? fx1c(vc.v[1]) + (vc.v[2] === 0 ? "% dos votos nominais no estado" : "% dos votos válidos") : "") + (vc.v[2] === 2 ? " no 2º turno" : "")]].concat(vc.c && vc.v[0] ? [["Custo por voto", brl(vc.c[2] / vc.v[0]), "despesas contratadas ÷ votos"]] : []));
  if (vc.c) {
    const [rt, ro, dt, dd] = vc.c;
    h += kvHTML([["Arrecadou", brl(rt), "receitas declaradas da campanha"], ["Gastou", brl(dt), "despesas contratadas"]]);
    if (ro.length && rt) { const pub = ro.filter(([k]) => /partido|fundo|financiamento/i.test(k)).reduce((a, x) => a + x[1], 0), pro = ro.filter(([k]) => /pr[óo]prios/i.test(k)).reduce((a, x) => a + x[1], 0), out = Math.max(0, rt - pub - pro);
      const pc = (x) => Math.round((100 * x) / rt) + "%";
      h += `<div class="pbox"><b>De cada R$ 100 da campanha: R$ ${Math.round((100 * pub) / rt)} vieram do partido (em geral, dinheiro público do fundo eleitoral), R$ ${Math.round((100 * pro) / rt)} do próprio candidato e R$ ${Math.round((100 * out) / rt)} de doações e outras fontes.</b>
        <span class="meter" style="height:12px"><span style="width:${pc(pub)};background:#1F4FBF"></span><span style="width:${pc(pro)};background:#F2C200"></span><span style="width:${pc(out)};background:#1E9E55"></span></span>
        <span class="small muted"><b style="color:#1F4FBF">●</b> partido/fundo ${pc(pub)} · <b style="color:#B38B00">●</b> próprio ${pc(pro)} · <b style="color:#14703C">●</b> doações e outros ${pc(out)}</span></div>`; }
    if (ro.length) h += `<h3>De onde veio o dinheiro</h3><div class="tl">${ro.map(([k, v]) => `<div><span>${esc(k)}</span><b>${brl(v)}</b>${bar(v, ro[0][1])}</div>`).join("")}</div><p class="small muted" style="margin:0">"Recursos de partido político" inclui o fundo eleitoral e o fundo partidário repassados pelo partido, que são dinheiro público.</p>`;
    if (dd.length) h += `<h3>Onde gastou</h3><div class="tl">${dd.map(([k, v]) => `<div><span>${esc(k)}</span><b>${brl(v)}</b>${bar(v, dd[0][1])}</div>`).join("")}</div>`;
    if (cp && cp.d && cp.d.length) h += `<h3>Quem financiou <span class="muted small">(${cp.nd > cp.d.length ? `os ${cp.d.length} maiores de ${mil(cp.nd)} doadores` : `${mil(cp.nd)} ${cp.nd === 1 ? "doador" : "doadores"}`})</span></h3><div class="tl">${cp.d.map(([k, v]) => `<div><span>${esc(title(k))}</span><b>${brl(v)}</b>${bar(v, cp.d[0][1])}</div>`).join("")}</div><p class="small muted" style="margin:0">Inclui pessoas físicas, o partido (que repassa o fundo eleitoral) e o próprio candidato, como declarado ao TSE. Desde 2015, empresas não podem doar a campanhas.</p>`;
    if (cp && cp.f && cp.f.length) h += `<h3>Quem recebeu da campanha <span class="muted small">(${cp.nf > cp.f.length ? `os ${cp.f.length} maiores de ${mil(cp.nf)} fornecedores` : `${mil(cp.nf)} ${cp.nf === 1 ? "fornecedor" : "fornecedores"}`})</span></h3><div class="tl">${cp.f.map(([k, v]) => `<div><span>${esc(title(k))}</span><b>${brl(v)}</b>${bar(v, cp.f[0][1])}</div>`).join("")}</div>`;
  } else if (t === "m") h += '<p class="muted">Sem prestação de contas encontrada.</p>';
  return h + `<p class="src">Fonte: ${FONTE_TSE} (votação por município e zona; prestação de contas de candidatos). Valores declarados pela campanha.</p>`;
}
const fx1c = (v) => v.toLocaleString("pt-BR", { maximumFractionDigits: 1 });

/* "EMPRESÁRIA/EMPRESÁRIO" -> "Empresário(a)"; "VEREADORA/VEREADOR" -> "Vereador(a)" */
function ocupacao(s) {
  const t = title(s || "");
  return t.replace(/([A-Za-zÀ-ÿ]+)\/([A-Za-zÀ-ÿ]+)/g, (m, a, b) => {
    const fem = a.toLowerCase(), mas = b.toLowerCase();
    if (fem === mas.replace(/o$/, "a") || fem === mas + "a") return (a[0] === a[0].toUpperCase() ? b[0].toUpperCase() + b.slice(1) : b) + "(a)";
    return m;
  });
}

/* -------- ficha -------- */
async function cracha(parts) {
  setNav("quem"); await loadBR();
  const t = parts[0]; let o = {}, P = null, src = "", voltar = "", chips = [], rich = false, X = null, casa = null;
  if (t === "c") {
    const d = BR.dep.find((x) => String(x[0]) === parts[1]); if (!d) return notFound();
    o = { nome: d[1], foto: d[4], cargo: cargo("dep", d[10]), part: d[2], uf: d[3], civil: title(d[5]) }; voltar = "#/uf/" + d[3]; casa = "C";
    chips.push('<span class="chip ok">Em exercício</span>'); if (!d[7]) chips.push('<span class="chip warn">Assumiu como suplente</span>'); if (d[8]) chips.push('<span class="chip new">Reeleito em 2026</span>');
    X = (await loadC(d[3]))[String(d[0])] || null; o.patList = X && X.pat;
    { const G = await getJSON("data/gab/" + d[3] + ".json").catch(() => null); if (G && G.dep[String(d[0])]) { o.gab = G.dep[String(d[0])]; o.gabInfo = G; } }
    { const VG = await getJSON("data/gab/viagens.json").catch(() => null); if (VG && VG.dep[String(d[0])]) { o.viag = VG.dep[String(d[0])]; o.viagInfo = VG; } }
    o.id = d[0]; { const V = await getJSON("data/gab/verba.json").catch(() => null); if (V && V.dep[String(d[0])]) { o.verba = V.dep[String(d[0])]; o.verbaInfo = V; if (!o.gab) o.gab = []; } }
    o.emAut = ((await getJSON("data/emendas/aut_" + d[3] + ".json").catch(() => ({}))).dep || {})["C:" + d[0]] || null;
    src = FONTE_CAM + " · " + FONTE_TSE; o.mand = "Mandato 2023–2027"; o.link = "https://www.camara.leg.br/deputados/" + d[0]; o.linkN = "Página na Câmara";
  } else if (t === "s") {
    const s = BR.sen.find((x) => String(x[0]) === parts[1]); if (!s) return notFound();
    o = { nome: s[1], foto: s[5], cargo: "Senador(a)" + (s[6] !== "Titular" ? " · suplente em exercício" : ""), part: s[3], uf: s[4], civil: s[2] }; voltar = "#/uf/" + s[4]; casa = "S";
    chips.push('<span class="chip ok">Em exercício</span>'); if (s[9]) chips.push('<span class="chip new">Reeleito em 2026</span>');
    X = (await loadS(s[4]))[String(s[0])] || null; o.patList = X && X.pat;
    o.emAut = ((await getJSON("data/emendas/aut_" + s[4] + ".json").catch(() => ({}))).dep || {})["S:" + s[0]] || null;
    { const G = await getJSON("data/gab/senado.json").catch(() => null); if (G && G.dep[String(s[0])]) { o.gab = G.dep[String(s[0])]; o.gabInfo = G; o.gabSen = true; } }
    { const SD = await getJSON("data/gab/senado_diarias.json").catch(() => null); if (SD && SD.dep[String(s[0])]) { o.diar = SD.dep[String(s[0])]; o.diarInfo = SD; } }
    o.mand = s[7] === 2022 ? "Mandato 2023–2031" : "Mandato até 31/01/2027"; src = FONTE_SEN + " · " + FONTE_TSE; o.link = "https://www25.senado.leg.br/web/senadores/senador/-/perfil/" + s[0]; o.linkN = "Página no Senado";
  } else if (t === "w") {
    // vereador que exerceu mandato sem estar entre os eleitos de 2024 (em geral, suplente que assumiu), pela lista do SAPL da Câmara
    const uf = parts[1], ue = parts[2]; const C = await getJSON("data/cam/" + ue + ".json").catch(() => null); const e = C && C.dep[parts[3]]; if (!e) return notFound();
    const cid = (C.fonte.match(/Câmara Municipal de (.+?) \(/) || [])[1] || "";
    o = { nome: title(String(e.nome).replace(/^(VEREADOR[A]?|VER\.)\s+/i, "")), cargo: cargo("ver", "") + " · " + cid, part: e.partido || "—", uf, foto: e.foto || "", est: e, estInfo: C, civil: e.civil ? title(e.civil) : "" };
    o.mand = "Exerceu mandato na legislatura 2025–2028 sem constar entre os eleitos de 2024 (em geral, suplente que assumiu)"; voltar = `#/cidade/${uf}/${ue}`; src = C.fonte;
    chips.push('<span class="chip warn">Suplente que assumiu</span>');
  } else if (t === "x") {
    // deputado estadual que exerceu mandato sem estar entre os eleitos de 2022 no TSE (em geral, suplente que assumiu)
    const uf = parts[1]; const E = await getJSON("data/est/" + uf + ".json").catch(() => null); const e = E && E.dep[parts[2]]; if (!e) return notFound();
    o = { nome: title(String(e.nome).replace(/^(DEPUTAD[OA]|DEP\.)\s+/i, "")), cargo: cargo(uf === "DF" ? "dd" : "de", "") + " · " + uf, part: e.partido || "—", uf, foto: e.foto || "", est: e, estInfo: E, civil: e.civil ? title(e.civil) : "" };
    o.mand = "Exerceu mandato na legislatura 2023–2027 sem constar entre os eleitos de 2022 (em geral, suplente que assumiu)"; voltar = "#/uf/" + uf; src = E.fonte;
    chips.push('<span class="chip warn">Suplente que assumiu</span>');
  } else {
    const uf = parts[1]; const D = await loadUF(uf); voltar = "#/uf/" + uf; src = FONTE_TSE;
    if (t === "g") { P = (parts[3] === "26" ? BR.ufs[uf].gov26 : BR.ufs[uf].gov)[+parts[2]]; if (!P) return notFound(); const pp = pTSE(P);
      o = { nome: pp.nome, cargo: cargo(parts[2] === "0" ? "gov" : "vice", pp.g) + " · " + BR.ufs[uf].nome, part: pp.part, uf }; o.mand = parts[3] === "26" ? (empossado("gov") ? "Eleito em 2026 · mandato 2027–2030" : "Eleito em 2026 · posse em 6/01/2027") : "Eleito em 2022 · mandato 2023–2026" + (empossado("gov") ? " (encerrado)" : "");
      if (parts[3] === "26") chips.push(empossado("gov") ? '<span class="chip ok">Em exercício</span>' : '<span class="chip new">Eleito em 2026</span>'); else if (empossado("gov")) chips.push('<span class="chip">Mandato encerrado</span>'); }
    else if (t === "e" || t === "f" || t === "n") { const arr = t === "e" ? (parts[2] === "26" ? D.de26 : D.de22) : t === "f" ? D.df26 : D.se26; P = arr[+parts[3]]; if (!P) return notFound(); const pp = pTSE(P);
      const ck = t === "e" ? (uf === "DF" ? "dd" : "de") : t === "f" ? "dep" : "sen"; o = { nome: pp.nome, cargo: cargo(ck, pp.g) + " · " + uf, part: pp.part, uf };
      const pl = empossado("leg"); o.mand = parts[2] === "26" ? (pl ? "Eleito em 2026 · mandato 2027–" + (t === "n" ? "2035" : "2031") : "Eleito em 2026 · posse em 1º/02/2027") : "Eleito em 2022 · mandato 2023–2027" + (pl ? " (encerrado)" : "");
      if (parts[2] === "26") chips.push(pl ? '<span class="chip ok">Em exercício</span>' : '<span class="chip new">Eleito em 2026</span>'); else if (pl && !D.de26.some((q) => q[1] === P[1])) chips.push('<span class="chip">Mandato encerrado</span>');
      if (t === "e" && parts[2] === "22" && D.de26.some((q) => q[1] === P[1])) chips.push('<span class="chip new">Reeleito em 2026</span>');
      if (t === "e") { const E = await getJSON("data/est/" + uf + ".json").catch(() => null); if (E && parts[2] === (E.ano || "22") && E.dep[parts[3]]) { o.est = E.dep[parts[3]]; o.estInfo = E; } } }
    else if (t === "m") { const m = D.mun[parts[2]]; if (!m) return notFound(); P = parts[3] === "p" ? m[1] : parts[3] === "v" ? m[2] : m[3][+parts[3]]; if (!P) return notFound(); const pp = pTSE(P);
      o = { nome: pp.nome, cargo: cargo(parts[3] === "p" ? "pref" : parts[3] === "v" ? "vp" : "ver", pp.g) + " · " + title(m[0]), part: pp.part, uf }; o.mand = "Eleito em 2024 · mandato 2025–2028"; voltar = `#/cidade/${uf}/${parts[2]}`;
      if (parts[3] !== "p" && parts[3] !== "v") { const C = await getJSON("data/cam/" + parts[2] + ".json").catch(() => null); if (C && C.dep[parts[3]]) { o.est = C.dep[parts[3]]; o.estInfo = C; }
        const GM = await getJSON("data/gabm/" + parts[2] + ".json").catch(() => null); if (GM && GM.dep[parts[3]]) { o.gab = GM.dep[parts[3]]; o.gabInfo = GM; o.gabMun = true; } } }
    o.patList = (await loadPat(uf))[keyTSE(P[1], P[5])] || null;
    const ano = t === "m" ? 2024 : (parts[2] === "26" || parts[3] === "26") ? 2026 : 2022;
    o.foto = (o.est && o.est.foto) || ftse(P, ano, t === "m" ? parts[2] : uf); o.ano = ano;
    o.vc = (await loadV(uf))[P[10]] || null;
    o.cp = (await loadCamp((t === "m" ? "m" : "") + uf))[P[10]] || null;
    if (o.cp) { if (!o.vc) o.vc = { c: o.cp.c }; else if (!o.vc.c) o.vc.c = o.cp.c; }
    if ((t === "g" && parts[2] === "0") || (t === "m" && parts[3] === "p")) o.plano = planoURL(uf, ano, t === "m" ? parts[2] : uf, P[10]);
  }
  if ((t === "c" || (t === "s" && BR.sen.find((x) => String(x[0]) === parts[1])[7] === 2022))) {
    o.cp = await campFederal(o.uf, o.civil, t === "c" ? "F" : "S"); if (o.cp) { o.vc = { c: o.cp.c }; o.ano = 2022; }
  }
  if (t === "e" || t === "x") {
    const EE = await getJSON("data/emendas_est/" + o.uf + ".json").catch(() => null);
    if (EE && (t === "x" || parts[2] === (EE.ano || "22"))) { const key = t === "x" ? parts[2] : +parts[3]; const it = Object.values(EE.dep).find((v) => v[1] === key); if (it) { o.emEst = it; o.emEstInfo = EE; } }
  }
  const pp = P ? pTSE(P) : null; if (pp) o.civil = o.civil || pp.civil;
  // concordância: eleita / reeleita para mulheres
  const fem = (pp && pp.g === "F") || /^(Deputada|Senadora|Governadora|Vice-governadora|Prefeita|Vice-prefeita|Vereadora)/.test(o.cargo || "");
  if (fem) { o.mand = String(o.mand || "").replace(/\bEleito\b/, "Eleita"); chips = chips.map((c) => c.replace(/\bReeleito\b/, "Reeleita").replace(/\bEleito\b/, "Eleita")); }
  const age = pp ? idade(pp.nasc) : null;
  const kv = [];
  if (o.civil) kv.push(["Nome civil", esc(o.civil), ""]);
  kv.push(["Partido", esc(o.part) + (pp && pp.fed ? ` <span class="s">federação ${esc(pp.fed)}</span>` : ""), ""]);
  if (o.mand) kv.push(["Mandato", esc(o.mand), ""]);
  if (age) kv.push(["Idade", age + " anos", `nasceu em ${esc(pp.nasc)}`]);
  if (pp && pp.ocup) kv.push(["Ocupação declarada", esc(ocupacao(pp.ocup)), ""]);
  if (pp && pp.instr) kv.push(["Escolaridade", esc(title(pp.instr)), ""]);
  const tabs = [["resumo", "Resumo"]];
  if (casa) tabs.push(["custo", "Custo do mandato"], ["votos", "Votações"], ["proj", "Projetos"], ["disc", "Discursos"]);
  if (o.est) { tabs.push(["eproj", "Projetos"]); if (o.estInfo.temVotos) tabs.push(["evot", "Votações"]); }
  if (o.emEst) tabs.push(["eem", "Emendas"]);
  if (o.emAut) tabs.push(["emf", "Emendas"]);
  if (o.gab) tabs.push(["gab", "Gabinete"]);
  if (o.viag || o.diar) tabs.push(["via", "Viagens"]);
  if (o.vc) tabs.push(["camp", o.vc.v ? "Votos e campanha" : "Campanha"]);
  tabs.push(["pat", "Patrimônio"]);
  tabs.push(["card", "Card p/ Stories"]);
  const share = encodeURIComponent(o.nome + " (" + o.cargo + ") no Fiscaliza Brasil: " + location.origin + "/p/" + parts.map(encodeURIComponent).join("/"));
  const atual = new Date(BR.gerado + "T12:00").toLocaleDateString("pt-BR");
  M.innerHTML = `<section class="card glass"><a class="muted small" href="${voltar}">← Voltar</a>
    <div class="hero">${av(o.nome, o.foto, "lg")}<div style="display:grid;gap:6px"><span class="kick">${esc(o.cargo)}</span><h1>${esc(o.nome)}</h1><div class="chips"><span class="chip">${esc(o.part)}</span><span class="chip">${esc(o.uf)}</span>${chips.join("")}</div></div></div>
    <div class="btns">${o.link ? `<a class="btn o" href="${o.link}" target="_blank" rel="noopener">${o.linkN}</a>` : ""}<a class="btn o" href="https://wa.me/?text=${share}" target="_blank" rel="noopener">WhatsApp</a>${o.plano ? `<a class="btn o" href="${o.plano}" target="_blank" rel="noopener">Plano de governo (TSE)</a>` : ""}<button class="btn o" id="acf" type="button">☆ Acompanhar</button>${casa ? '<button class="btn o" id="cmpf" type="button">+ Comparar</button>' : ""}<button class="btn o" id="rep">Reportar erro</button></div></section>
   <section class="card glass" style="padding:8px"><div class="tabs2" role="tablist">${tabs.map(([k, l], i) => `<button role="tab" data-k="${k}" aria-selected="${i === 0}">${l}</button>`).join("")}</div></section>
   <section class="card glass" id="tb"></section>`;
  $("#rep").onclick = () => reportar(o.nome + " · " + o.cargo);
  if (casa && window.FBCmp) FBCmp.botao($("#cmpf"), { ref: parts.join("/"), nome: o.nome, cargo: o.cargo, foto: o.foto || "", part: o.part || "", casa, uf: o.uf || "", id: parts[1] || "" });
  if (window.FBAcomp) FBAcomp.botao($("#acf"), { tipo: "p", ref: parts.join("/"), nome: o.nome, cargo: o.cargo, foto: o.foto || "", part: o.part || "", casa: casa || "", uf: o.uf || "", id: parts[1] || "" });
  const tb = $("#tb");
  const show = async (k) => {
    document.querySelectorAll(".tabs2 button").forEach((b) => b.setAttribute("aria-selected", b.dataset.k === k));
    if (k === "resumo" && casa === "C") await loadVC().catch(() => null);
    if (k === "resumo" && casa && X && !X.fp && !o.cpp) o.cpp = await contaPartido(o, X, casa).catch(() => null);
    if (k === "resumo") { tb.innerHTML = `<h2>Resumo</h2>${kvHTML(secResumo(o, X, casa).concat(kv))}<p class="src">Fonte: ${src}. Atualizado em ${atual}.</p>` + lacunasHTML(o, parts); ligaLAI(tb); }
    else if (k === "gab") { tb.innerHTML = secGab(o); histGab(o, parts, tb); }
    else if (k === "via") tb.innerHTML = secViagens(o);
    else if (k === "custo") { await loadCotaMedia(); tb.innerHTML = `<h2>Quanto custa o mandato</h2>${secCusto(o, X, casa)}`; }
    else if (k === "votos") { tb.innerHTML = `<h2>Como votou</h2><p class="muted small" style="margin:0">Votações nominais do Plenário desde 2023. Toque no filtro para escolher ano${casa === "C" ? " e tema" : ""}.</p><div id="vv" style="display:grid;gap:10px"><p class="muted">Carregando…</p></div><p class="src">Fonte: ${casa === "C" ? FONTE_CAM : FONTE_SEN}.</p>`; await loadPart().catch(() => null); secVotos(X, casa === "C" ? await loadVC() : await loadVS(), casa, $("#vv"), o.part); }
    else if (k === "proj") { tb.innerHTML = `<h2>Projetos apresentados</h2><div id="pp" style="display:grid;gap:10px"></div><p class="src">Desde 2023. Fonte: ${casa === "C" ? FONTE_CAM : FONTE_SEN}.</p>`; secProjetos(X, casa, $("#pp")); }
    else if (k === "disc") tb.innerHTML = `<h2>Discursos</h2>${secDisc(X)}<p class="src">Fonte: ${casa === "C" ? FONTE_CAM : FONTE_SEN}. Resumos e assuntos são os oficiais da Casa.</p>`;
    else if (k === "camp") tb.innerHTML = `<h2>${o.vc.v ? "Votos e campanha" : "Campanha"} · ${o.ano}</h2>${secCamp(o.vc, t, o.cp)}`;
    else if (k === "eproj") tb.innerHTML = secEstProj(o);
    else if (k === "evot") tb.innerHTML = secEstVot(o);
    else if (k === "eem") tb.innerHTML = secEmEst(o);
    else if (k === "emf") tb.innerHTML = secEmFed(o);
    else if (k === "pat") tb.innerHTML = `<h2>Patrimônio declarado</h2>${secPat(o.patList)}`;
    else if (k === "card") { tb.innerHTML = `<h2>Card para Stories</h2><div id="stc"><p class="muted">Montando a imagem…</p></div>`; await cardStories($("#stc"), Object.assign({}, o, { cargo: String(o.cargo || "").split(" · ")[0] }), await statsCard(o, X, casa), await notaCard(o, X, casa)); }
  };
  document.querySelectorAll(".tabs2 button").forEach((b) => (b.onclick = () => show(b.dataset.k)));
  if (!X && casa) tb.insertAdjacentHTML("beforebegin", "");
  await show("resumo");
  window.scrollTo(0, 0);
}

/* números do card para Stories */
const brlc = (n) => n >= 1e6 ? "R$ " + (n / 1e6).toFixed(1).replace(".", ",") + " mi" : n >= 1e3 ? "R$ " + Math.round(n / 1e3) + " mil" : brl(n);
async function contaPartido(o, X, casa) { if (!X || !casa) return null; if (X.fp) return { a: (X.fp.match(/g/g) || []).length, c: (X.fp.match(/r/g) || []).length }; await loadPart().catch(() => null); const pos = posPartido(o.part, casa); const v = X.v || ""; let a = 0, c = 0;
  for (let i = 0; i < v.length; i++) { const x = v[i], p = pos[i]; if ((x === "S" || x === "N") && (p === "S" || p === "N")) { if (x === p) a++; else c++; } } return { a, c }; }
async function statsCard(o, X, casa) {
  const st = [];
  if (casa && X) {
    if (X.pres && X.pres[1]) st.push([Math.round((100 * X.pres[0]) / X.pres[1]) + "%", "Presença nas votações"]);
    const cp = await contaPartido(o, X, casa); if (cp && cp.a + cp.c) st.push([Math.round((100 * cp.a) / (cp.a + cp.c)) + "%", "Votou com o partido", "#14703C"]);
    const au = (X.au && X.au.c) || {}; st.push([["PL", "PLP", "PEC", "PDL", "PRS"].reduce((s, t) => s + (au[t] || 0), 0), "Projetos apresentados"]);
    if (X.cota) st.push([brlc(Object.values(X.cota.a).reduce((s, t) => s + Object.values(t).reduce((x, y) => x + y, 0), 0)), "Cota parlamentar gasta"]);
  }
  if (o.est) { const cs = o.estInfo && o.estInfo.casa ? "na Câmara" : "na Assembleia"; const pc = ["PLO", "PL", "PLC", "PEC", "PDL", "PRE", "PLL", "PLCM", "PLI", "PCOL"].reduce((x, k) => x + ((o.est.cont || {})[k] || 0), 0); st.push([mil(pc), "Projetos " + cs + " desde " + ((o.estInfo && o.estInfo.desde) || (o.estInfo && o.estInfo.casa ? "2025" : "2023"))]);
    const tv = Object.values(o.est.votos || {}).reduce((x, y) => x + y, 0); if (tv) st.push([mil(tv), "Votos registrados " + cs]); }
  if (st.length < 4 && o.vc && o.vc.v) st.push([mil(o.vc.v[0]), "Votos em " + o.ano]);
  if (st.length < 4 && o.vc && o.vc.c) st.push([brlc(o.vc.c[0]), "Arrecadou na campanha"]);
  const p = o.patList && o.patList.length ? o.patList[o.patList.length - 1] : null;
  if (st.length < 4 && p) st.push([brlc(p[6]), "Patrimônio declarado em " + p[0]]);
  if (st.length < 4 && o.vc && o.vc.c) st.push([brlc(o.vc.c[2]), "Gastou na campanha"]);
  if (st.length < 4 && o.vc && o.vc.v && o.vc.v[1] != null) st.push([String(o.vc.v[1]).replace(".", ",") + "%", o.vc.v[2] === 0 ? "dos votos nominais no estado" : "dos votos válidos"]);
  if (st.length < 4 && o.vc && o.vc.v && o.vc.v[3]) st.push([o.vc.v[3] + "º", "mais votado"]);
  return st.slice(0, 4);
}
async function notaCard(o, X, casa) { const cp = await contaPartido(o, X, casa); if (cp && cp.c) return `Votou contra o próprio partido ${mil(cp.c)} vezes desde 2023.`; return o.mand || ""; }

/* link para a página do candidato no DivulgaCandContas do TSE, onde fica o plano de governo registrado */
const REGIAO = { AC: "NORTE", AM: "NORTE", AP: "NORTE", PA: "NORTE", RO: "NORTE", RR: "NORTE", TO: "NORTE", AL: "NORDESTE", BA: "NORDESTE", CE: "NORDESTE", MA: "NORDESTE", PB: "NORDESTE", PE: "NORDESTE", PI: "NORDESTE", RN: "NORDESTE", SE: "NORDESTE", DF: "CENTROOESTE", GO: "CENTROOESTE", MS: "CENTROOESTE", MT: "CENTROOESTE", ES: "SUDESTE", MG: "SUDESTE", RJ: "SUDESTE", SP: "SUDESTE", PR: "SUL", RS: "SUL", SC: "SUL" };
function planoURL(uf, ano, ue, sq) { if (!sq || !ELEI[ano]) return ""; return `https://divulgacandcontas.tse.jus.br/divulga/#/candidato/${REGIAO[uf] || "BR"}/${uf}/${ELEI[ano]}/${sq}/${ano}/${ue}`; }

/* deputados estaduais: dados das Assembleias que publicam no SAPL */
const TIPOS_EST = { PLI: "Projetos de autoria própria", PCOL: "Projetos em coautoria", REQP: "Requerimentos à Prefeitura", PLO: "Projetos de lei", PL: "Projetos de lei", PLC: "Projetos de lei complementar", PEC: "Propostas de emenda à Constituição", PDL: "Projetos de decreto legislativo", PRE: "Projetos de resolução", PR: "Projetos de resolução", IND: "Indicações", REQ: "Requerimentos", MOC: "Moções", PINF: "Pedidos de informação" };
/* emendas do deputado estadual ao orçamento do estado (onde o governo publica com o nome do autor) */
function secEmEst(o) {
  const [, , emp, pago, cs] = o.emEst, I = o.emEstInfo; const mx = cs.length ? cs[0][1] : 1;
  return `<h2>Emendas ao orçamento do estado</h2>
   ${kvHTML([["Empenhado", brl(emp), "reservado no orçamento desde " + I.desde], ["Pago", brl(pago), emp ? Math.round((100 * pago) / emp) + "% do empenhado" : ""]])}
   <h3>Para onde foi</h3><div class="tl">${cs.map(([c, v]) => `<div><span>${esc(title(c))}</span><b>${brl(v)}</b>${bar(v, mx)}</div>`).join("")}</div>
   <p class="small muted" style="margin:0">A cidade é a informada pelo governo do estado para cada emenda. Quando o dinheiro vai para um órgão estadual, pode aparecer a capital ou "sem município".</p>
   <p class="src">Fonte: <a href="${esc(I.url)}" target="_blank" rel="noopener">${esc(I.fonte)}</a>. Atualizado em ${new Date(I.gerado + "T12:00").toLocaleDateString("pt-BR")}.</p>`;
}
/* Pedido de acesso à informação (LAI) pronto para o que o órgão não publica em formato aberto. */
const LAI_ITENS = {
  votos: "a lista de todas as votações realizadas em Plenário desde 1º/01/2023, com o voto nominal de cada parlamentar (sim, não, abstenção, obstrução ou ausência) em cada uma",
  projetos: "a lista das proposições apresentadas por cada parlamentar desde 1º/01/2023, com tipo, número, ementa, data de apresentação, autores e situação atual",
  gabinete: "a lista dos servidores lotados em cada gabinete, com nome, cargo, data de nomeação e remuneração bruta mensal, atualizada mês a mês",
};
const LAI_NOME = { votos: "Votos de cada um", projetos: "Projetos apresentados", gabinete: "Funcionários do gabinete e salários" };
function lacunasHTML(o, parts) {
  const t = parts[0], uf = o.uf || parts[1] || ""; let org = "", falta = [];
  const cid = (o.cargo || "").split(" · ").slice(-1)[0];
  if (t === "e") { org = "Assembleia Legislativa " + (typeof deUF === "function" && BR.ufs[uf] ? deUF(BR.ufs[uf].nome) : "do estado"); if (!o.est || o.estInfo.temVotos === false || !(o.est.vlist || []).length) falta.push("votos"); if (!o.est || !(o.est.props || []).length) falta.push("projetos"); falta.push("gabinete"); }
  else if (t === "m" && parts[3] !== "p" && parts[3] !== "v") { org = "Câmara Municipal de " + cid; if (!o.est || o.estInfo.temVotos === false || !(o.est.vlist || []).length) falta.push("votos"); if (!o.est || !(o.est.props || []).length) falta.push("projetos"); if (!o.gab) falta.push("gabinete"); }
  else if (t === "m") { org = "Prefeitura Municipal de " + cid; falta.push("gabinete"); }
  else if (t === "g") { org = "Governo do Estado " + (typeof deUF === "function" && BR.ufs[uf] ? deUF(BR.ufs[uf].nome) : ""); falta.push("gabinete"); }
  if (!falta.length || !org) return "";
  const busca = "https://www.google.com/search?q=" + encodeURIComponent("e-SIC " + org);
  const art = /^Governo/.test(org) ? "o" : "a";
  return `<section class="lai"><h3>O que ${art} ${esc(org)} não publica em formato aberto</h3>
    <p class="small muted" style="margin:0 0 8px">Pela Lei de Acesso à Informação (Lei 12.527/2011), qualquer pessoa pode pedir esses dados, sem precisar explicar o motivo. O órgão tem 20 dias para responder, prorrogáveis por mais 10.</p>
    <div class="chips">${falta.map((f) => `<button class="chip" data-lai="${f}" data-org="${esc(org)}" data-sic="${esc(busca)}">${LAI_NOME[f]}: pedir pela LAI</button>`).join("")}</div><div class="laibox"></div></section>`;
}
function ligaLAI(el) {
  el.querySelectorAll("[data-lai]").forEach((b) => b.onclick = () => {
    const f = b.dataset.lai, org = b.dataset.org, box = el.querySelector(".laibox");
    const txt = `${/^Governo/.test(org) ? "Ao" : "À"} ${org},\n\nCom base na Lei nº 12.527/2011 (Lei de Acesso à Informação), solicito ${LAI_ITENS[f]}.\n\nPeço que os dados sejam enviados em formato aberto e legível por máquina (planilha, CSV ou JSON), como prevê o art. 8º, § 3º, II e III da mesma lei, e que passem a ser publicados de forma permanente no portal da transparência, como determina o art. 8º.\n\nAtenciosamente,\n[seu nome]`;
    box.innerHTML = `<textarea class="laitxt" rows="10" style="width:100%;margin-top:10px;font:inherit;padding:12px;border-radius:14px;border:1px solid var(--line,#ddd);background:var(--bg,#fff);color:var(--ink,#0B0B0C)">${esc(txt)}</textarea>
      <div class="chips" style="margin-top:8px"><button class="btn" data-cp>Copiar o pedido</button><a class="btn o" href="${b.dataset.sic}" target="_blank" rel="noopener">Achar o e-SIC do órgão ↗</a></div>
      <p class="src">Mande pelo e-SIC (Serviço de Informação ao Cidadão) do órgão e guarde o número do protocolo. Sem resposta em 20 dias, cabe recurso à autoridade superior. Se receber os dados, mande para o Fiscaliza Brasil pelo botão "Reportar erro" que a gente coloca no site.</p>`;
    box.querySelector("[data-cp]").onclick = (ev) => { const ta = box.querySelector(".laitxt"); navigator.clipboard.writeText(ta.value).then(() => { ev.target.textContent = "Copiado"; }).catch(() => { ta.select(); }); };
  });
}
/* Secretário parlamentar: vencimento por nível (Câmara, tabela em vigor desde 18/02/2026, Lei 15.349/2026). Com a gratificação de representação (GRG), o valor dobra. */
const SP_VENC = [1710.83, 1906.12, 2101.45, 2296.72, 2492.06, 2687.34, 2882.65, 3077.95, 3273.26, 3468.54, 3663.85, 4054.45, 4445.03, 4835.65, 5226.24, 5616.84, 6202.74, 6788.64, 7374.54, 7960.44, 8546.34, 9327.56, 10108.74, 11544.1, 12979.45];
const SP_TAB = "https://www2.camara.leg.br/a-camara/estruturaadm/diretorias/diretoria-de-gestao-pessoas/estrutura-1/depes/secretariado-parlamentar/posse-de-sp-sem-vinculo/TABSP202601MAR202620260303.pdf/view";
function secGab(o) {
  const g = o.gab || [], dt = (x) => (x ? new Date(String(x).slice(0, 10) + "T12:00").toLocaleDateString("pt-BR") : "");
  if (o.gabMun) {
    const tot = g.reduce((a, r) => a + (r[3] || 0), 0), mx = Math.max(1, ...g.map((r) => r[3] || 0));
    return `<h2>Quem trabalha no gabinete <span class="muted small">(${g.length})</span></h2>
     <div class="kv"><div><div class="l">Remuneração somada</div><div class="v">${brl(tot)}</div><div class="s">por mês, valores brutos publicados</div></div><div><div class="l">Pessoas</div><div class="v">${mil(g.length)}</div><div class="s">servidores ativos lotados no gabinete</div></div></div>
     <div class="tl" style="margin-top:10px">${g.map((r) => `<div><span><b>${esc(r[0])}</b><br><span class="small muted">${esc(r[1])}${r[2] ? " · desde " + dt(r[2]) : ""}</span></span><b>${r[3] ? brl(r[3]) : ""}</b>${bar(r[3] || 0, mx)}</div>`).join("")}</div>
     <p class="src">${esc(o.gabInfo.obs || "")} Fonte: <a href="${o.gabInfo.url}" target="_blank" rel="noopener">${esc(o.gabInfo.fonte)}</a>. Atualizado em ${dt(o.gabInfo.gerado)}.</p>`;
  }
  if (o.gabSen) {
    const tot = g.reduce((a, r) => a + (r[3] || 0), 0), mx = Math.max(1, ...g.map((r) => r[3] || 0)), [ano, mes] = String(o.gabInfo.mes || "").split("-");
    return `<h2>Quem trabalha no gabinete <span class="muted small">(${g.length})</span></h2>
     <div class="kv"><div><div class="l">Folha do gabinete</div><div class="v">${brl(tot)}</div><div class="s">salários brutos em ${mes}/${ano}, folha normal</div></div><div><div class="l">Pessoas</div><div class="v">${mil(g.length)}</div><div class="s">no gabinete em Brasília e nos escritórios no estado</div></div></div>
     <div class="tl" style="margin-top:10px">${g.map((r) => `<div><span><b>${esc(r[0])}</b><br><span class="small muted">${esc(r[1])}${r[2] ? " · desde " + r[2] : ""}</span></span><b>${r[3] != null ? brl(r[3]) : '<span class="small muted">sem folha no mês</span>'}${r[4] != null ? `<br><span class="small muted">líquido ${brl(r[4])}</span>` : ""}</b>${bar(r[3] || 0, mx)}</div>`).join("")}</div>
     <p class="src">Salário bruto = remuneração básica, vantagens pessoais e função, sem auxílios e diárias. Líquido = depois de imposto e previdência. É o que o Senado publica, pelo nome, na folha normal de ${mes}/${ano}. Fonte: <a href="${o.gabInfo.url}" target="_blank" rel="noopener">${esc(o.gabInfo.fonte)}</a>. Atualizado em ${dt(o.gabInfo.gerado)}.</p>`;
  }
  let h = "";
  if (o.verba) {
    const anos = Object.keys(o.verba).sort().reverse(), a0 = anos[0], M = o.verba[a0], lim = o.verbaInfo.limite || 0, tot = M.reduce((a, m) => a + m[1], 0), med = M.length ? M.reduce((a, m) => a + (m[2] || 0), 0) / M.length : 0;
    const NM = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"], mx = Math.max(1, ...M.map((m) => m[1]));
    h += `<h2>Verba de gabinete</h2>
     <div class="kv"><div><div class="l">Gasto em ${a0}</div><div class="v">${brl(tot)}</div><div class="s">${M.length} ${M.length === 1 ? "mês" : "meses"} com salários pagos</div></div><div><div class="l">Uso do limite</div><div class="v">${med.toFixed(0)}%</div><div class="s">média por mês · limite atual ${brl(lim)} por mês</div></div></div>
     <div class="tl">${M.map((m) => `<div><span>${NM[m[0] - 1]}/${a0}</span><b>${brl(m[1])}${m[2] != null ? ` <span class="small muted">${String(m[2]).replace(".", ",")}%</span>` : ""}</b>${bar(m[1], mx)}</div>`).join("")}</div>
     ${anos.length > 1 ? `<p class="small muted" style="margin:6px 0 0">${anos.slice(1).map((a) => `${a}: ${brl(o.verba[a].reduce((x, m) => x + m[1], 0))}`).join(" · ")}</p>` : ""}
     <p class="src">A verba de gabinete paga os salários dos até 25 secretários parlamentares. A porcentagem é sobre o limite em vigor naquele mês. Fonte: <a href="https://www.camara.leg.br/deputados/${o.id || ""}" target="_blank" rel="noopener">página oficial do deputado na Câmara</a>. Atualizado em ${dt(o.verbaInfo.gerado)}.</p>`;
  }
  if (!g.length) return h;
  const nv = (c) => { const m = /\(SP(\d\d)([CSU])?\)/.exec(c || ""); return m ? +m[1] : 0; };
  const cs = {}; g.forEach((r) => (cs[r[1]] = (cs[r[1]] || 0) + 1));
  return h + `<h2>Quem trabalha no gabinete <span class="muted small">(${g.length})</span></h2><div class="chips">${Object.entries(cs).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([c, n]) => `<span class="chip">${esc(c)} · ${n}</span>`).join("")}</div>
    <div class="tl" style="margin-top:10px">${g.map((r) => { const n = nv(r[1]), v = n ? SP_VENC[n - 1] : 0; return `<div><span><b>${esc(r[0])}</b><br><span class="small muted">${esc(r[1])}${r[2] ? " · desde " + dt(r[2]) : ""}</span></span><b class="small">${v ? `${brl(v)} a ${brl(2 * v)}<br><span class="muted">faixa do nível SP${String(n).padStart(2, "0")}</span>` : '<span class="muted">cargo sem tabela de secretário</span>'}</b></div>`; }).join("")}</div>
    <p class="src">A Câmara não publica o salário com o nome de cada pessoa: o arquivo mensal de remuneração traz só um número no lugar do nome. Por isso mostramos a faixa oficial do nível de cada secretário parlamentar: o vencimento bruto, sem e com a gratificação de representação (que dobra o valor), pela <a href="${SP_TAB}" target="_blank" rel="noopener">tabela em vigor desde 18/02/2026</a> (Lei 15.349/2026), sem o auxílio-alimentação. Fonte do cadastro: <a href="${o.gabInfo ? o.gabInfo.url : "#"}" target="_blank" rel="noopener">${o.gabInfo ? esc(o.gabInfo.fonte) : "Câmara dos Deputados"}</a>${o.gabInfo ? ", atualizado em " + dt(o.gabInfo.gerado) : ""}.</p>`;
}
function secViagens(o) {
  const dt = (x) => new Date(String(x).slice(0, 10) + "T12:00").toLocaleDateString("pt-BR"); let h = "";
  if (o.viag) {
    const v = o.viag.v || [], tp = v.reduce((a, x) => a + x[4], 0), td = v.reduce((a, x) => a + x[5], 0);
    h += `<h2>Viagens em missão oficial</h2>
     ${v.length ? `<div class="kv"><div><div class="l">Viagens</div><div class="v">${mil(v.length)}</div><div class="s">registradas</div></div><div><div class="l">Custo</div><div class="v">${brl(tp + td)}</div><div class="s">${brl(tp)} em passagens e ${brl(td)} em diárias</div></div></div>
      <div class="tl">${v.map((x) => `<div><span><b>${esc(x[3] || "Destino não informado")}</b> <span class="small muted">${esc(x[1])}</span><br><span class="small muted">${esc(x[2])}</span></span><b>${brl(x[4] + x[5])}</b></div>`).join("")}</div>` : '<p class="muted">Nenhuma viagem em missão oficial registrada neste ano.</p>'}
     <h3>Moradia em Brasília</h3><div class="kv"><div><div class="l">Imóvel funcional</div><div class="v small">${esc(o.viag.imovel || "Sem informação")}</div></div><div><div class="l">Auxílio-moradia</div><div class="v small">${esc(o.viag.auxilio || "Sem informação")}</div></div></div>
     <p class="src">Missão oficial é a viagem a trabalho autorizada pela Câmara, paga com passagens e diárias (fora da cota parlamentar). A Câmara mostra as viagens do ano corrente; o Fiscaliza Brasil guarda as de cada coleta a partir de novembro de 2026. Fonte: <a href="https://www.camara.leg.br/deputados/${o.id}" target="_blank" rel="noopener">${esc(o.viagInfo.fonte)}</a>. Atualizado em ${dt(o.viagInfo.gerado)}.</p>`;
  }
  if (o.diar) {
    const ms = Object.entries(o.diar).sort().reverse(), tot = ms.reduce((a, x) => a + x[1], 0), mx = Math.max(1, ...ms.map((x) => x[1]));
    const NM = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
    h += `<h2>Diárias recebidas</h2><div class="kv"><div><div class="l">Total desde 2023</div><div class="v">${brl(tot)}</div><div class="s">em ${ms.length} ${ms.length === 1 ? "mês" : "meses"} com diárias</div></div></div>
     <div class="tl">${ms.slice(0, 24).map(([m, v]) => `<div><span>${NM[+m.slice(5) - 1]}/${m.slice(0, 4)}</span><b>${brl(v)}</b>${bar(v, mx)}</div>`).join("")}</div>
     <p class="src">Diária é o valor pago para cobrir hospedagem e alimentação em viagem a serviço. O Senado publica o valor por mês, mas não o destino. Fonte: ${esc(o.diarInfo.fonte)}. Atualizado em ${dt(o.diarInfo.gerado)}.</p>`;
  }
  return h;
}
async function histGab(o, parts, tb) {
  const t = parts[0], ch = t === "c" ? "c" + o.uf : t === "s" ? "senado" : t === "m" ? "m" + parts[2] : null, id = t === "m" ? parts[3] : parts[1];
  if (!ch || !o.gab) return;
  const Hh = await getJSON("data/gab/hist/" + ch + ".json").catch(() => null); if (!Hh) return;
  const ev = ((Hh.ev || {})[id] || []).slice().reverse(), dt = (x) => new Date(x + "T12:00").toLocaleDateString("pt-BR");
  const div = document.createElement("div");
  div.innerHTML = `<h3>Entradas e saídas</h3>${ev.length ? `<div class="tl">${ev.slice(0, 60).map((e) => `<div><span><b>${e[1] === "+" ? "Entrou" : "Saiu"}:</b> ${esc(e[2])}${e[3] ? ` <span class="small muted">${esc(e[3])}</span>` : ""}</span><b class="small muted">${dt(e[0])}</b></div>`).join("")}</div>` : `<p class="small muted">Nenhuma mudança desde ${dt(Hh.desde)}.</p>`}
    <p class="src">O Fiscaliza Brasil compara a lista do gabinete a cada coleta desde ${dt(Hh.desde)} e anota quem entrou e quem saiu na data em que percebeu a mudança.</p>`;
  tb.appendChild(div);
}
function secEmFed(o) {
  const e = o.emAut, mx = e.c.length ? e.c[0][2] : 1, mf = e.f.length ? e.f[0][1] : 1;
  return `<h2>Emendas enviadas <span class="muted small">(desde 2023)</span></h2>
   <div class="kv"><div><div class="l">Total pago</div><div class="v">${brl(e.t)}</div><div class="s">emendas individuais e de autoria identificada</div></div><div><div class="l">Cidades</div><div class="v">${mil(e.n)}</div><div class="s">receberam pelo menos uma</div></div></div>
   <h3>Para onde foi o dinheiro${e.n > e.c.length ? ` <span class="muted small">(as ${e.c.length} cidades que mais receberam)</span>` : ""}</h3>
   <div class="tl">${e.c.map(([uf, m, v, fv, ue]) => `<div><span>${ue ? `<a href="#/cidade/${esc(uf)}/${esc(ue)}"><b>${esc(title(m))}</b></a>` : `<b>${esc(title(m))}</b>`} <span class="small muted">${esc(uf)}</span>${fv && fv.length ? `<br><span class="small muted">${fv.map(([n, x]) => esc(title(n)) + " " + brl(x)).join(" · ")}</span>` : ""}</span><b>${brl(v)}</b>${bar(v, mx)}</div>`).join("")}</div>
   <h3>Quem mais recebeu</h3><div class="tl">${e.f.map(([n, v]) => `<div><span>${esc(title(n))}</span><b>${brl(v)}</b>${bar(v, mf)}</div>`).join("")}</div>
   <p class="src">A cidade é a do cadastro de quem recebeu: dinheiro repassado ao governo do estado aparece na capital, e pagamentos ao Banco do Brasil aparecem em Brasília. Valores pagos desde 2023. Fonte: Portal da Transparência (CGU), emendas parlamentares por favorecido.</p>`;
}
const HOMEN = /utilidade p[úu]blica|denomina|t[íi]tulo (honor[íi]fico|de cidad)|cidad[ãa](o|ã) honor[áa]ri|honra ao m[ée]rito|comenda|institui (o|a) (dia|semana|m[êe]s)|inclui no calend[áa]rio|calend[áa]rio oficial|data comemorativa|voto de (louvor|congratula|aplauso|pesar)|mo[çc][ãa]o de (louvor|congratula|aplauso|pesar)|patrim[ôo]nio cultural imaterial|capital (estadual|nacional) d/i;
function secEstProj(o) {
  const e = o.est, I = o.estInfo; const c = Object.entries(e.cont || {}).sort((a, b) => b[1] - a[1]);
  const casaN = I.casa ? "na " + I.casa : "na Assembleia", ano0 = I.desde || (I.casa ? "2025" : "2023");
  return `<h2>Projetos ${casaN}</h2>
   <div class="kv">${c.slice(0, 6).map(([k, n]) => `<div><div class="l">${esc(TIPOS_EST[k] || k)}</div><div class="v">${mil(n)}</div><div class="s">desde ${ano0}</div></div>`).join("") || `<div><div class="v">0</div><div class="s">nenhuma proposição registrada desde ${ano0}</div></div>`}</div>
   ${e.anos && Object.keys(e.anos).length > 1 ? `<h3>Por ano</h3><div class="kv">${Object.entries(e.anos).sort((a, b) => b[0] - a[0]).map(([a, c]) => `<div><div class="l">${esc(a)}</div><div class="v">${mil(Object.entries(c).filter(([k]) => k === "PLI" || k === "PCOL").reduce((x, [, y]) => x + y, 0))}</div><div class="s">projetos · ${mil((c.REQP || 0) + (c.REQ || 0))} requerimentos · ${mil(c.PINF || 0)} pedidos de informação</div></div>`).join("")}</div>` : ""}
   ${e.leis && e.leis.length ? (() => { const h = e.leis.filter((l) => l[3]), c = e.leis.filter((l) => !l[3]); const li = (L) => L.map((l) => `<div class="it"><div class="hd"><span class="cd">Lei ${esc(l[0])}/${esc(l[1])}${l[5] ? " · " + new Date(l[5] + "T12:00").toLocaleDateString("pt-BR") : ""}</span>${l[4] ? "" : '<span class="vt n0">Coautoria</span>'}</div><div>${esc(l[2])}</div></div>`).join("");
      return `<h3>Leis aprovadas <span class="muted small">(${mil(e.leis.length)} desde 2023)</span></h3><div class="kv"><div><div class="l">Leis de conteúdo</div><div class="v">${mil(c.length)}</div><div class="s">criam ou mudam regras</div></div><div><div class="l">Homenagens</div><div class="v">${mil(h.length)}</div><div class="s">utilidade pública, nomes, datas e títulos</div></div></div>
        ${c.length ? `<div class="lst">${li(c.slice(0, 30))}</div>` : ""}${h.length ? `<details style="margin-top:8px"><summary class="small">Ver as ${mil(h.length)} homenagens</summary><div class="lst">${li(h)}</div></details>` : ""}`; })() : ""}
   ${e.props.length ? (() => { const h = e.props.filter((p) => HOMEN.test(p[1])), c = e.props.filter((p) => !HOMEN.test(p[1])); const it = (L) => L.map((p) => `<div class="it"><div class="hd"><span class="cd">${esc(p[0])} · ${p[2] ? new Date(p[2] + "T12:00").toLocaleDateString("pt-BR") : ""}</span>${p[3] ? '<span class="vt n0">Em tramitação</span>' : ""}${p[4] === 0 ? '<span class="vt n0">Coautoria</span>' : ""}</div><div>${esc(p[1])}</div></div>`).join("");
      return `<h3>Projetos apresentados (mais recentes)</h3>${h.length ? `<p class="small muted" style="margin:0">${mil(c.length)} de conteúdo e ${mil(h.length)} de homenagem (utilidade pública, nomes de ruas e prédios, datas comemorativas e títulos), separados pela ementa.</p>` : ""}<div class="lst">${it(c)}</div>${h.length ? `<details style="margin-top:8px"><summary class="small">Ver os ${mil(h.length)} projetos de homenagem</summary><div class="lst">${it(h)}</div></details>` : ""}`; })() : ""}
   ${e.pres && Object.keys(e.pres).length ? `<h3>Presença nas sessões do plenário</h3><div class="kv">${Object.entries(e.pres).sort((a, b) => b[0] - a[0]).map(([a, f]) => { const tot = Object.values(f).reduce((x, y) => x + y, 0), pr = f["Presente"] || 0; return `<div><div class="l">${esc(a)}</div><div class="v">${tot ? Math.round((pr / tot) * 100) : 0}%</div><div class="s">${mil(pr)} de ${mil(tot)} registros</div></div>`; }).join("")}</div>` : ""}
   ${I.obs ? `<div class="note">${esc(I.obs)}</div>` : ""}${e.parcial ? '<div class="note">Lista parcial: ${I.casa ? "este vereador" : "este deputado"} tem muitas proposições e mostramos as mais recentes.</div>' : ""}
   <p class="src">Fonte: <a href="${esc(e.sapl)}" target="_blank" rel="noopener">${esc(I.fonte)}</a>. Inclui autoria e coautoria. Atualizado em ${new Date(I.gerado + "T12:00").toLocaleDateString("pt-BR")}.</p>`;
}
function secEstVot(o) {
  const e = o.est, I = o.estInfo; const v = e.votos || {}; const t = Object.values(v).reduce((a, b) => a + b, 0);
  return `<h2>Como votou ${I.casa ? "na " + I.casa : "na Assembleia"}</h2>
   <div class="chips">${[["S", "Sim"], ["N", "Não"], ["A", "Abstenção"], ["O", "Obstrução"]].filter(([k]) => v[k]).map(([k, n]) => `<span class="chip">${n} ${mil(v[k])}</span>`).join("")}<span class="chip">Total ${mil(t)}</span></div>
   ${e.vlist.length ? `<div class="lst">${e.vlist.map((x) => `<div class="it"><div class="hd"><span class="cd">${esc(x[0] || "Votação")} · ${x[3] ? new Date(x[3] + "T12:00").toLocaleDateString("pt-BR") : ""}</span><span class="vt ${x[2] === "S" ? "ok" : x[2] === "N" ? "no" : "n0"}">${x[2] === "S" ? "Sim" : x[2] === "N" ? "Não" : x[2] === "A" ? "Abstenção" : esc(x[2])}</span></div><div>${esc(x[1])}</div>${x[4] != null ? `<div class="small muted">Sim ${x[4]} × Não ${x[5]}</div>` : ""}</div>`).join("")}</div>` : '<p class="muted">Nenhum voto nominal registrado desde 2023.</p>'}
   <p class="src">Votos nominais registrados ${I.casa ? "pela " + I.casa : "pela Assembleia"} no SAPL. Fonte: <a href="${esc(e.sapl)}" target="_blank" rel="noopener">${esc(I.fonte)}</a>.</p>`;
}
