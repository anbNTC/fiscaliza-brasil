/* Telas extras do Fiscalize: Congresso (calendário do Plenário), Impostômetro e "Mais".
   Usa os globais de fiscalize.html ($, M, esc, mil, getJSON, setNav, BR, loadBR, title). */
"use strict";
let CONG = null, IMP = null;
const MESN = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const bi = (v) => v >= 1e12 ? "R$ " + (v / 1e12).toLocaleString("pt-BR", { maximumFractionDigits: 2 }) + " trilhão" + (v >= 2e12 ? "ões".slice(0, 0) : "") : "R$ " + (v / 1e9).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " bilhões";
const tri = (v) => v >= 1e12 ? "R$ " + (v / 1e12).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + (v >= 2e12 ? " trilhões" : " trilhão") : bi(v);
const FONTE_RFB = '<a href="https://www.gov.br/receitafederal/dados" target="_blank" rel="noopener">Receita Federal · Dados Abertos (arrecadação por estado)</a>';

(function css() {
  const s = document.createElement("style");
  s.textContent = `.cal{align-content:start;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:4px;text-align:center}
  .cal .h{font-size:.68rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;padding:4px 0}
  .cal button{aspect-ratio:1;border:1px solid transparent;border-radius:12px;background:rgba(255,255,255,.55);font-weight:700;font-variant-numeric:tabular-nums;display:grid;place-items:center;align-content:center;gap:2px;padding:0;font-size:.9rem}
  .cal button:disabled{background:none;color:rgba(11,11,12,.3);cursor:default}
  .cal button[aria-pressed="true"]{background:var(--ink);color:#fff}
  .cal button .dt{display:flex;gap:3px;height:6px}.cal button .dt i{width:6px;height:6px;border-radius:50%}
  .cal .c{background:var(--verde)}.cal .s{background:var(--azul)}
  .mnav{display:flex;align-items:center;justify-content:space-between;gap:8px}
  .mnav button{width:40px;height:40px;border-radius:50%;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.7);font-size:1.1rem}
  .leg{display:flex;gap:14px;font-size:.82rem;color:var(--muted)}.leg i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}
  .sess{display:grid;gap:10px;align-content:start;padding:14px;border-radius:18px;background:rgba(255,255,255,.75);border:1px solid rgba(11,11,12,.08)}
  .sess .tg{display:inline-flex;align-items:center;justify-content:center;align-self:start;justify-self:start;font-family:var(--f-mono);font-size:.7rem;font-weight:600;letter-spacing:.1em;line-height:1;text-transform:uppercase;padding:6px 10px 6px calc(10px + .1em);border-radius:999px;color:#fff}
  .it2{display:grid;gap:2px;padding:8px 0;border-top:1px solid rgba(11,11,12,.08)}
  .it2 .cd{font-family:var(--f-mono);font-size:.8rem;font-weight:600}
  .imp-big{font-family:var(--f-display);font-weight:700;font-size:clamp(2rem,9vw,3.2rem);line-height:1;letter-spacing:-.02em}
  .yrs{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none}.yrs::-webkit-scrollbar{display:none}
  .yrs button{flex:none;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.7);border-radius:999px;padding:6px 12px;font-weight:700;font-size:.85rem}
  .yrs button[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
  .ufmap svg{width:100%;height:auto;display:block}.ufmap path{stroke:#FBFBF7;stroke-width:12;cursor:pointer}.ufmap path:hover{stroke:var(--ink);stroke-width:18}
  .scale{display:flex;align-items:center;gap:8px;font-size:.75rem;color:var(--muted)}.scale i{flex:1;height:8px;border-radius:4px;background:linear-gradient(90deg,#F3EFE6,#C05A2B)}
  .menu{display:grid;gap:10px}.row2{align-items:start}.row2>.card{align-content:start}@media (min-width:700px){.row2>.card:has(#cal){position:sticky;top:76px}}.mhd{display:grid;gap:inherit;justify-items:start;padding-left:calc(18px + 1px)}.cal>*{min-width:0}.menu a{display:grid;grid-template-columns:44px 1fr auto;gap:14px;align-items:center;padding:16px;border-radius:20px;text-decoration:none;background:rgba(255,255,255,.75);border:1px solid rgba(11,11,12,.08)}
  .menu a:hover{border-color:var(--ink)}.menu i{font-style:normal;width:44px;height:44px;border-radius:13px;background:var(--ink);color:#fff;display:grid;place-items:center;font-size:1.2rem}
  .menu b{font-family:var(--f-display);display:block}.menu small{color:var(--muted)}
  .menu a.soon{opacity:.55;pointer-events:none}`;
  document.head.appendChild(s);
})();

/* ---------------- Congresso ---------------- */
async function congresso(dia) {
  setNav("congresso");
  CONG = CONG || await getJSON("data/congresso.json");
  const VC = await getJSON("data/camara_votacoes.json"), VS = await getJSON("data/senado_votacoes.json");
  const byDay = {};
  CONG.cam.forEach((e) => (byDay[e[1].slice(0, 10)] = byDay[e[1].slice(0, 10)] || { c: [], s: [] }).c.push(e));
  CONG.sen.forEach((e) => (byDay[e[1]] = byDay[e[1]] || { c: [], s: [] }).s.push(e));
  const vcDay = {}; VC.forEach((v) => (vcDay[v[1]] = vcDay[v[1]] || []).push(v));
  const vsDay = {}; VS.forEach((v) => (vsDay[v[1]] = vsDay[v[1]] || []).push(v));
  const dias = Object.keys(byDay).sort();
  const hoje = new Date().toISOString().slice(0, 10);
  const real = dias.filter((d) => d <= hoje && (byDay[d].c.length || byDay[d].s.some((s) => /DELIBERATIVA/.test(s[3]))));
  let sel = dia && byDay[dia] ? dia : real[real.length - 1] || dias[dias.length - 1];
  let ym = sel.slice(0, 7);
  const prox = dias.filter((d) => d > hoje).slice(0, 4);
  M.innerHTML = `<section class="card glass"><span class="kick">Pauta do Congresso</span><h1>O que a Câmara e o Senado votaram</h1><span class="fx"></span>
    <p class="muted" style="margin:0">Sessões do Plenário, a pauta de cada dia e o resultado das votações nominais. Toque num dia marcado.</p>
    <div class="btns"><a class="btn o" href="#/semana">Resumo da semana</a><a class="btn o" href="#/votacoes">Votações que importam</a></div>
    ${prox.length ? `<div class="note">Próximas sessões: ${prox.map((d) => `<a href="#/congresso/${d}">${new Date(d + "T12:00").toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })}</a>`).join(" · ")}</div>` : ""}</section>
   <div class="row2"><section class="card glass"><div class="mnav"><button id="mp" aria-label="Mês anterior">‹</button><h2 id="mt"></h2><button id="mn" aria-label="Próximo mês">›</button></div>
     <div class="cal" id="cal"></div><div class="leg"><span><i style="background:var(--verde)"></i>Câmara</span><span><i style="background:var(--azul)"></i>Senado</span></div></section>
    <section class="card glass" id="dia"></section></div>
   <p class="src">Fontes: ${FONTE_CAM} · ${FONTE_SEN}. Atualizado em ${new Date(CONG.gerado + "T12:00").toLocaleDateString("pt-BR")}.</p>`;
  const drawCal = () => {
    const [y, m] = ym.split("-").map(Number); const first = new Date(y, m - 1, 1).getDay(), n = new Date(y, m, 0).getDate();
    $("#mt").textContent = MESN[m - 1] + " de " + y;
    let h = ["D", "S", "T", "Q", "Q", "S", "S"].map((d) => `<div class="h">${d}</div>`).join("") + "<div></div>".repeat(first);
    for (let d = 1; d <= n; d++) { const k = `${ym}-${String(d).padStart(2, "0")}`, b = byDay[k];
      h += `<button ${b ? "" : "disabled"} data-d="${k}" aria-pressed="${k === sel}">${d}<span class="dt">${b && b.c.length ? '<i class="c"></i>' : ""}${b && b.s.length ? '<i class="s"></i>' : ""}</span></button>`; }
    $("#cal").innerHTML = h;
    document.querySelectorAll("#cal button[data-d]").forEach((b) => (b.onclick = () => { sel = b.dataset.d; drawCal(); drawDia(); history.replaceState(null, "", "#/congresso/" + sel); }));
  };
  const drawDia = () => {
    const b = byDay[sel] || { c: [], s: [] }; const vc = vcDay[sel] || [], vs = vsDay[sel] || [];
    let h = `<span class="kick">${new Date(sel + "T12:00").toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" })}</span>`;
    b.c.forEach((e) => {
      h += `<div class="sess"><span class="tg" style="background:var(--verde)">Câmara</span><b>${esc(e[5])}</b><span class="small muted">${e[1].slice(11, 16)}${e[2] ? "–" + e[2].slice(11, 16) : ""} · ${esc(e[3])}${e[6] ? ` · <a href="${esc(e[6])}" target="_blank" rel="noopener">pauta oficial</a>` : ""}</span>
        ${(e[7] || []).length ? `<div>${e[7].slice(0, 12).map((x) => `<div class="it2"><span class="cd">${esc(x[2] || x[1])}</span><span>${esc(x[3] || x[1])}</span>${x[5] ? `<span class="small muted">Relator: ${esc(x[5])}</span>` : ""}</div>`).join("")}${e[7].length > 12 ? `<p class="small muted">e mais ${e[7].length - 12} itens</p>` : ""}</div>` : ""}</div>`;
    });
    if (vc.length) h += `<div class="sess"><span class="tg" style="background:var(--verde)">Câmara · votações nominais</span>${vc.map((v) => `<div class="it2"><span class="cd">${esc(v[5] || "Votação")} · ${v[2] === "1" ? "aprovado" : v[2] === "0" ? "rejeitado" : ""} · Sim ${v[3]} × Não ${v[4]}</span><span>${esc(v[7] || v[6])}</span>${v[8] ? `<span class="small muted">Governo orientou ${esc(v[8])}</span>` : ""}</div>`).join("")}</div>`;
    b.s.forEach((e) => {
      h += `<div class="sess"><span class="tg" style="background:var(--azul)">${e[6] === "CN" ? "Congresso" : "Senado"}</span><b>${esc(title(e[4] ? e[4] + " · " : ""))}${esc(title(e[3]))}</b><span class="small muted">${esc(e[2])} · ${esc(e[5])}</span>
        ${(e[7] || []).length ? `<div>${e[7].slice(0, 12).map((x) => `<div class="it2"><span class="cd">${esc(x[1].replace(/ 0+(\d)/, " $1"))}</span><span>${esc(x[2])}</span></div>`).join("")}</div>` : ""}</div>`;
    });
    if (vs.length) h += `<div class="sess"><span class="tg" style="background:var(--azul)">Senado · votações nominais</span>${vs.map((v) => `<div class="it2"><span class="cd">${esc(v[2])} · ${v[5] === "A" ? "aprovado" : v[5] === "R" ? "rejeitado" : esc(v[5])}${v[6] === "S" ? " · secreta" : ` · Sim ${v[7]} × Não ${v[8]}`}</span><span>${esc(v[3] || v[4])}</span></div>`).join("")}</div>`;
    if (!b.c.length && !b.s.length) h += '<p class="muted">Sem sessão neste dia.</p>';
    $("#dia").innerHTML = h;
  };
  $("#mp").onclick = () => { const [y, m] = ym.split("-").map(Number); const d = new Date(y, m - 2, 1); ym = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0"); drawCal(); };
  $("#mn").onclick = () => { const [y, m] = ym.split("-").map(Number); const d = new Date(y, m, 1); ym = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0"); drawCal(); };
  drawCal(); drawDia();
}

/* ---------------- Impostômetro ---------------- */
async function impostometro(ano) {
  setNav("mais"); await loadBR();
  IMP = IMP || await getJSON("data/impostometro.json");
  const anos = Object.keys(IMP.anos).map(Number).sort((a, b) => b - a);
  let a = anos.includes(+ano) ? +ano : anos[0];
  const ultM = +IMP.ult.slice(5, 7), ultA = +IMP.ult.slice(0, 4);
  const G = IMP.grupos;
  M.innerHTML = `<section class="card glass"><span class="kick">Impostômetro</span><h1>Quanto o governo federal arrecadou</h1><span class="fx"></span>
     <div class="yrs" id="yrs">${anos.map((y) => `<button data-y="${y}" aria-pressed="${y === a}">${y}</button>`).join("")}</div><div id="imp" style="display:grid;gap:14px"></div></section>
   <div class="row2"><section class="card glass ufmap"><h2>Por estado</h2><div id="map"></div><div class="scale"><span>menos</span><i></i><span>mais</span></div><p class="small muted" style="margin:0">Toque num estado para ver quanto saiu de lá e de quais tributos.</p></section>
    <section class="card glass"><h2 id="ufh">Estados que mais arrecadaram</h2><div class="tl" id="uft"></div></section></div>
   <section class="card glass"><h2>De onde vem o dinheiro</h2><div class="tl" id="grp"></div></section>
   <p class="src">Fonte: ${FONTE_RFB}. Valores nominais, sem correção pela inflação. Inclui tributos federais administrados pela Receita (não inclui ICMS, IPVA, ISS e IPTU, que são estaduais e municipais). O estado é onde o tributo foi recolhido, que nem sempre é onde a renda foi gerada.</p>`;
  const tot = (uf) => uf ? IMP.anos[a].uf[uf][0] : Object.values(IMP.anos[a].uf).reduce((x, v) => x + v[0], 0);
  const grp = (uf) => G.map((g, i) => [g[0], g[1], uf ? IMP.anos[a].uf[uf][i + 1] : Object.values(IMP.anos[a].uf).reduce((x, v) => x + v[i + 1], 0)]).sort((x, y) => y[2] - x[2]);
  let ufSel = null;
  const draw = () => {
    document.querySelectorAll("#yrs button").forEach((b) => b.setAttribute("aria-pressed", +b.dataset.y === a));
    const T = tot(ufSel), parcial = a === ultA && ultM < 12;
    const prev = IMP.anos[a - 1]; const Tp = prev ? (ufSel ? (prev.uf[ufSel] || [0])[0] : Object.values(prev.uf).reduce((x, v) => x + v[0], 0)) : 0;
    $("#imp").innerHTML = `<div><div class="imp-big">${tri(T)}</div><p class="muted" style="margin:6px 0 0">arrecadados ${ufSel ? "por contribuintes registrados em " + esc(BR.ufs[ufSel].nome) : "pelo governo federal"} em ${a}${parcial ? `, de janeiro a ${MESN[ultM - 1]} (último mês publicado)` : ""}.</p>
      ${!parcial && Tp ? `<p class="small" style="margin:6px 0 0">${T >= Tp ? "Alta" : "Queda"} de ${Math.abs(Math.round((T / Tp - 1) * 1000) / 10).toLocaleString("pt-BR")}% sobre ${a - 1}, em valores da época.</p>` : ""}
      ${a === 2025 ? `<div class="note" style="margin-top:10px">Em 2025, de fevereiro a novembro, os dados da Receita registram no Distrito Federal parte da contribuição previdenciária e do IR retido de salários de todo o país. Por isso, neste ano, o DF aparece muito acima do normal e os demais estados abaixo. O total do Brasil não muda.</div>` : ""}
      ${ufSel ? `<button class="btn o" id="all" style="margin-top:10px">← Ver o Brasil</button>` : ""}</div>`;
    if (ufSel) $("#all").onclick = () => { ufSel = null; draw(); };
    const ufs = Object.entries(IMP.anos[a].uf).map(([u, v]) => [u, v[0]]).sort((x, y) => y[1] - x[1]); const mx = ufs[0][1];
    const all = Object.values(BR.ufs).map((u) => u.bb); const bb = [Math.min(...all.map((b) => b[0])), Math.min(...all.map((b) => b[1])), Math.max(...all.map((b) => b[2])), Math.max(...all.map((b) => b[3]))];
    const col = (v) => { const t = Math.pow(v / mx, 0.35); const c0 = [243, 239, 230], c1 = [192, 90, 43]; return `rgb(${c0.map((c, i) => Math.round(c + (c1[i] - c) * t)).join(",")})`; };
    $("#map").innerHTML = `<svg viewBox="${bb[0] - 30} ${bb[1] - 30} ${bb[2] - bb[0] + 60} ${bb[3] - bb[1] + 60}" role="img" aria-label="Arrecadação por estado">${ufs.map(([u, v]) => `<path d="${BR.ufs[u].p}" fill="${col(v)}" data-u="${u}"${ufSel === u ? ' style="stroke:#0B0B0C;stroke-width:22"' : ""}><title>${esc(BR.ufs[u].nome)}: ${bi(v)}</title></path>`).join("")}</svg>`;
    document.querySelectorAll("#map path").forEach((p) => (p.onclick = () => { ufSel = p.dataset.u; draw(); window.scrollTo({ top: 0, behavior: "smooth" }); }));
    $("#ufh").textContent = "Estados que mais arrecadaram";
    $("#uft").innerHTML = ufs.slice(0, 10).map(([u, v]) => `<div style="cursor:pointer" data-u="${u}"><span>${esc(BR.ufs[u].nome)} <span class="muted small">${Math.round((v / tot()) * 1000) / 10}%</span></span><b>${bi(v)}</b>${bar(v, mx)}</div>`).join("") + `<button class="btn o" id="mu">Ver os 27 estados</button>`;
    const wire = () => document.querySelectorAll("#uft [data-u]").forEach((d) => (d.onclick = () => { ufSel = d.dataset.u; draw(); window.scrollTo({ top: 0, behavior: "smooth" }); }));
    wire(); $("#mu").onclick = () => { $("#uft").innerHTML = ufs.map(([u, v]) => `<div style="cursor:pointer" data-u="${u}"><span>${esc(BR.ufs[u].nome)}</span><b>${bi(v)}</b>${bar(v, mx)}</div>`).join(""); wire(); };
    const gs = grp(ufSel); const gm = gs[0][2];
    $("#grp").innerHTML = gs.filter((g) => g[2] > 0).map(([n, d, v]) => `<div><span><b style="font-family:var(--f-display);font-size:.95rem">${esc(n)}</b> <span class="muted small">${Math.round((v / T) * 100)}% · ${esc(d)}</span></span><b>${bi(v)}</b>${bar(v, gm)}</div>`).join("");
  };
  document.querySelectorAll("#yrs button").forEach((b) => (b.onclick = () => { a = +b.dataset.y; draw(); history.replaceState(null, "", "#/impostometro/" + a); }));
  draw();
}

/* ---------------- Mais ---------------- */
async function mais() {
  setNav("mais");
  M.innerHTML = `<section class="card glass"><div class="mhd"><span class="kick">Mais</span><h1>Outras ferramentas</h1><span class="fx"></span></div>
   <nav class="menu"><a href="#/semana"><i>7</i><span><b>Resumo da semana</b><small>O que o Congresso votou na semana, quem faltou e quem votou contra o partido.</small></span><span>→</span></a>
    <a href="#/votacoes"><i>!</i><span><b>Votações que importam</b><small>As votações mais disputadas do ano e como cada partido votou.</small></span><span>→</span></a>
    <a href="#/acompanho"><i>★</i><span><b>Acompanhando</b><small>Os políticos e partidos que você escolheu acompanhar, num lugar só.</small></span><span>→</span></a>
    <a href="#/partidos"><i>⚑</i><span><b>Partidos</b><small>O que cada partido diz defender e como a bancada vota de verdade.</small></span><span>→</span></a>
    <a href="#/agora"><i>●</i><span><b>Acontece agora</b><small>As manchetes de política dos principais veículos do país, atualizadas ao vivo.</small></span><span>→</span></a>
    <a href="#/doadores"><i>$</i><span><b>Quem financiou quem</b><small>Busque uma empresa, pessoa ou partido e veja quais eleitos receberam doações dele na campanha.</small></span><span>→</span></a>
    <a href="#/impostometro"><i>R$</i><span><b>Impostômetro</b><small>Quanto o governo federal arrecada a cada ano, por estado e por tipo de tributo.</small></span><span>→</span></a>
    <a href="#/congresso"><i>⚖</i><span><b>Pauta do Congresso</b><small>O calendário do Plenário da Câmara e do Senado e o resultado de cada votação.</small></span><span>→</span></a>
    <a href="distrital.html"><i>◎</i><span><b>Voto distrital</b><small>Como ficariam a Câmara e as Assembleias com o voto distrital misto no Brasil.</small></span><span>→</span></a>
    <a href="#/dicionario"><i>Aa</i><span><b>Dicionário político</b><small>Os termos da política explicados em palavras simples, com a fonte oficial.</small></span><span>→</span></a>
    <a href="#/governos"><i>↗</i><span><b>Governos lado a lado</b><small>Inflação, PIB, juros, dólar, desemprego e dívida pública, governo a governo.</small></span><span>→</span></a>
    <a href="#/stf"><i>§</i><span><b>Agenda do STF</b><small>A pauta de julgamentos do Supremo, processo a processo, e os seus 11 ministros.</small></span><span>→</span></a><a href="#/comparar"><i>⇄</i><span><b>Comparar</b><small>Coloque de 2 a 4 deputados ou senadores lado a lado.</small></span><span>→</span></a><a href="#" onclick="instalarApp();return false"><i>⬇</i><span><b>Instalar o app</b><small>Coloque o Fiscaliza Brasil na tela do celular, como um aplicativo.</small></span><span>→</span></a><a href="#/metodologia"><i>?</i><span><b>Como calculamos</b><small>De onde vem e como é feito cada número do Fiscaliza Brasil.</small></span><span>→</span></a><a href="#/privacidade"><i>🔒</i><span><b>Privacidade</b><small>Quais dados guardamos, por quê, e como pedir para apagar.</small></span><span>→</span></a><a href="#/colabore"><i>♥</i><span><b>Colabore</b><small>Doe pelo Pix ou mande ideias e correções para manter o portal no ar.</small></span><span>→</span></a></nav></section>`;
}

/* ---------------- Quem financiou quem (doadores de campanha, TSE) ---------------- */
async function doadores(q0) {
  setNav("mais"); q0 = q0 ? decodeURIComponent(q0) : "";
  const nd = (s) => String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().replace(/[^A-Z0-9 ]/g, " ").replace(/\s+/g, " ").trim();
  M.innerHTML = `<section class="card glass"><span class="kick">Campanhas</span><h1>Quem financiou quem</h1><span class="fx"></span>
     <p class="muted" style="margin:0">Digite o nome de uma empresa, pessoa ou partido e veja quais eleitos receberam doações dele na campanha (eleições de 2022, 2024 e 2026). Toque num político para abrir a ficha.</p>
     <form id="dq" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px"><input id="dqi" type="search" value="${esc(q0)}" placeholder="Ex.: nome da empresa ou do doador" style="flex:1;min-width:200px;border:1px solid rgba(11,11,12,.18);border-radius:999px;padding:11px 16px;font:inherit;background:rgba(255,255,255,.85)"><button class="btn" type="submit">Buscar</button></form>
     <p class="src">Fonte: TSE · prestação de contas dos candidatos (receitas). Entram as doações de R$ 1.000 ou mais para os eleitos que estão no site. O TSE publica o nome do doador; o CPF e o CNPJ não são mostrados aqui. Os valores de 2026 mudam até a prestação de contas final.</p></section>
   <div id="dr"></div>`;
  $("#dq").onsubmit = (e) => { e.preventDefault(); const v = $("#dqi").value.trim(); if (v.length >= 3) location.hash = "#/doadores/" + encodeURIComponent(v); };
  if (q0.trim().length < 3) return;
  const qq = nd(q0); const k = (qq.replace(/ /g, "") + "__").slice(0, 2);
  $("#dr").innerHTML = '<section class="card glass"><p class="muted">Buscando…</p></section>';
  const anos = ["2026", "2024", "2022"]; const res = await Promise.all(anos.map((a) => getJSON(`data/doa/${a}/${k}.json`).catch(() => [])));
  const pal = qq.split(" ").filter((w) => w.length >= 2);
  const achou = [];
  res.forEach((L, i) => (L || []).forEach((d) => { const n = nd(d[0]); if (n === qq || pal.every((w) => n.includes(w))) achou.push({ ano: anos[i], d }); }));
  achou.sort((a, b) => (nd(b.d[0]) === qq) - (nd(a.d[0]) === qq) || b.d[1] - a.d[1]);
  if (!achou.length) { $("#dr").innerHTML = `<section class="card glass"><p class="muted" style="margin:0">Nenhuma doação de R$ 1.000 ou mais de "<b>${esc(q0)}</b>" para os eleitos que estão no site. Confira a grafia: a busca usa o nome como o TSE publica (começando pela primeira palavra do nome).</p></section>`; return; }
  $("#dr").innerHTML = achou.slice(0, 30).map(({ ano, d }) => `<section class="card glass"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:baseline"><h2 style="margin:0">${esc(title(d[0]))}</h2><span class="chip">Eleição de ${ano}</span></div>
     <div class="kv"><div><div class="l">Doou</div><div class="v">${brl(d[1])}</div><div class="s">soma das doações de R$ 1.000 ou mais</div></div><div><div class="l">Eleitos que receberam</div><div class="v">${mil(d[2])}</div><div class="s">${d[2] > d[3].length ? `mostrando os ${d[3].length} maiores` : "todos aqui"}</div></div></div>
     <div class="tl">${d[3].map((p) => `<div><span><a href="${p[3]}"><b>${esc(p[0])}</b></a><br><span class="small muted">${esc(p[1])} · ${esc(p[2])}</span></span><b>${brl(p[4])}</b>${bar(p[4], d[3][0][4])}</div>`).join("")}</div></section>`).join("")
    + (achou.length > 30 ? `<p class="muted small">Mostrando 30 de ${achou.length} doadores com esse nome. Escreva o nome mais completo para filtrar.</p>` : "");
}

/* ---------------- Governos lado a lado ---------------- */
let GOV = null, STFD = null;
const fx1 = (v, d = 1) => v == null ? "—" : v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
const mesAno = (m) => m ? MESN[+m.slice(5, 7) - 1].slice(0, 3) + "/" + m.slice(0, 4) : "";
const IND = {
  ipca: ["Inflação (IPCA)", "% no ano", "Quanto os preços subiram em cada ano."],
  pib: ["Crescimento do PIB", "% no ano", "Variação real da economia em cada ano."],
  selic: ["Juros (Selic)", "% ao ano, em dezembro", "Taxa básica de juros definida pelo Banco Central."],
  dolar: ["Dólar", "R$, média de dezembro", "Cotação média do dólar comercial (venda)."],
  desemp: ["Desemprego", "% em dezembro", "Taxa de desocupação do IBGE (a série começa em 2012)."],
  divida: ["Dívida pública", "% do PIB, em dezembro", "Dívida bruta do governo geral (a série começa em 2006)."]
};
const GCOR = { PSDB: "#1F4FBF", PT: "#B3261E", MDB: "#2E7D5B", PL: "#0B0B0C" };
async function governos(ind) {
  setNav("mais"); GOV = GOV || await getJSON("data/governos.json");
  let k = IND[ind] ? ind : "ipca";
  const govOf = (y) => GOV.gov.find((g) => g.ini.slice(0, 4) <= y && y <= g.fim.slice(0, 4) && !(y === "2016" && g.id === "Dilma 2")) || null;
  M.innerHTML = `<section class="card glass"><span class="kick">Governos lado a lado</span><h1>A economia em cada governo</h1><span class="fx"></span>
     <p class="muted" style="margin:0">Indicadores oficiais do Banco Central e do IBGE, de 1995 a hoje, divididos por mandato presidencial. Sem nota nem ranking: os números também dependem da economia mundial, de crises e de decisões do Congresso e do Banco Central, que é autônomo desde 2021.</p>
     <div class="yrs" id="ind">${Object.entries(IND).map(([c, v]) => `<button data-k="${c}" aria-pressed="${c === k}">${v[0]}</button>`).join("")}</div></section>
   <section class="card glass"><h2 id="ih"></h2><p class="muted small" id="id" style="margin:0"></p><div id="ich" style="overflow-x:auto"></div>
     <div class="chips">${[...new Set(GOV.gov.map((g) => g.part))].map((p) => `<span class="chip"><i style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${GCOR[p]};margin-right:5px"></i>${p}</span>`).join("")}</div></section>
   <section class="card glass"><h2>Mandato a mandato</h2><div class="people" style="grid-template-columns:repeat(auto-fill,minmax(240px,1fr))" id="gcards"></div>
     <p class="src">Fontes: <a href="https://www3.bcb.gov.br/sgspub" target="_blank" rel="noopener">Banco Central · SGS</a> (IPCA/IBGE 433, Selic 4189, dólar 3698, PIB 7326, desemprego PNAD 24369, dívida bruta 13762, salário mínimo 1619). Inflação média = IPCA acumulado no mandato, por ano. PIB médio = anos completos do mandato (2016 conta para Temer). Ganho real do salário mínimo = descontada a inflação do período. Dados até ${mesAno(GOV.ult.ipca)} (IPCA).</p></section>`;
  const draw = () => {
    document.querySelectorAll("#ind button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.k === k));
    const [n, u, d] = IND[k]; $("#ih").textContent = n; $("#id").textContent = d + " Unidade: " + u + ".";
    const s = Object.entries(GOV.serie[k]).filter(([y]) => y >= "1995"); const vs = s.map((x) => x[1]); const mx = Math.max(...vs, 0), mn = Math.min(...vs, 0);
    const H = 180, z = mx === mn ? H : (mx / (mx - mn)) * H;
    $("#ich").innerHTML = `<div style="display:flex;align-items:flex-end;gap:3px;height:${H + 16}px;min-width:${s.length * 22}px;position:relative;padding-top:16px;margin-bottom:44px">${s.map(([y, v]) => { const g = govOf(y); const h = Math.abs(v) / (mx - mn || 1) * H;
      return `<div title="${y}: ${fx1(v, k === "dolar" ? 2 : 1)}" style="flex:1;min-width:16px;height:${H}px;position:relative"><i style="position:absolute;left:0;right:0;${v >= 0 ? `bottom:${H - z}px` : `top:${z}px`};height:${Math.max(2, h)}px;background:${g ? GCOR[g.part] : "#999"};border-radius:3px;opacity:.85"></i>
        <small style="position:absolute;bottom:-34px;left:50%;transform:translateX(-50%) rotate(-60deg);transform-origin:center;font-size:.62rem;color:var(--muted)">${y}</small></div>`; }).join("")}
      <span style="position:absolute;left:0;right:0;top:${16 + H - (H - z)}px;border-top:1px dashed rgba(11,11,12,.25)"></span></div>`;
  };
  $("#gcards").innerHTML = GOV.gov.map((g) => `<div class="pc" style="gap:6px"><span class="chip" style="background:${GCOR[g.part]};color:#fff">${esc(g.part)}</span><b style="font-size:1.1rem">${esc(g.id)}</b><small>${esc(g.pres)} · ${mesAno(g.ini)} a ${g.fim >= "2026-12" ? "hoje" : mesAno(g.fim)}</small>
     <div class="tl" style="width:100%;font-size:.86rem">
      <div><span>Inflação média</span><b>${fx1(g.ipca_ano)}% ao ano</b></div>
      <div><span>PIB médio</span><b>${g.pib_medio == null ? "—" : fx1(g.pib_medio) + "% ao ano"}</b></div>
      <div><span>Selic</span><b>${fx1(g.selic[0], 2)}% → ${fx1(g.selic[1], 2)}%</b></div>
      <div><span>Dólar</span><b>R$ ${fx1(g.dolar[0], 2)} → ${fx1(g.dolar[1], 2)}</b></div>
      <div><span>Desemprego</span><b>${g.desemp[0] == null ? "—" : fx1(g.desemp[0]) + "% → " + fx1(g.desemp[1]) + "%"}</b></div>
      <div><span>Dívida bruta</span><b>${g.divida[0] == null ? "—" : fx1(g.divida[0]) + "% → " + fx1(g.divida[1]) + "% do PIB"}</b></div>
      <div><span>Salário mínimo (ganho real)</span><b>${g.salmin_real == null ? "—" : (g.salmin_real > 0 ? "+" : "") + fx1(g.salmin_real) + "%"}</b></div></div>
     <small style="font-size:.72rem">Início = último dado antes da posse; fim = ${g.fim >= "2026-12" ? "último dado publicado" : "último mês do mandato"}.</small></div>`).join("");
  document.querySelectorAll("#ind button").forEach((b) => (b.onclick = () => { k = b.dataset.k; draw(); history.replaceState(null, "", "#/governos/" + k); }));
  draw();
}

/* ---------------- Agenda do STF ---------------- */
async function stf() {
  setNav("mais"); STFD = STFD || await getJSON("data/stf.json");
  const dias = Object.keys(STFD.dias).sort((a, b) => a.split("/").reverse().join("").localeCompare(b.split("/").reverse().join("")));
  const virtTot = STFD.virt.reduce((a, v) => a + v[2], 0);
  const yrs = (d) => { const [y, m, dd] = d.split("-").map(Number); const n = new Date(); let a = n.getFullYear() - y; if (n < new Date(n.getFullYear(), m - 1, dd)) a--; return a; };
  M.innerHTML = `<section class="card glass"><span class="kick">Agenda do STF</span><h1>O que o Supremo está julgando</h1><span class="fx"></span>
     ${kvHTML([["Sessões presenciais na pauta", mil(dias.length), "dias com pauta publicada"], ["Processos no Plenário Virtual", mil(virtTot), `em ${STFD.virt.length} sessões virtuais de 2026`], ["Ministros", "10 de 11", "1 cadeira vaga"]])}</section>
   <section class="card glass"><h2>Pauta das sessões presenciais</h2><div class="yrs" id="sd">${dias.map((d, i) => `<button data-d="${d}">${d.slice(0, 5)}</button>`).join("")}</div><div id="sp" class="lst"></div></section>
   <section class="card glass"><h2>Os 11 ministros</h2><div class="people">${STFD.min.map((m) => `<div class="pc">${av(m[0], "https://www.stf.jus.br/arquivo/cms/bibliotecaConsultaProdutoBibliotecaPastaMinistro/imagem/" + m[5])}<b>${esc(m[0])}</b><small>${m[1] ? `<b style="font-size:.8rem">${esc(m[1])}</b><br>` : ""}No STF desde ${m[2].slice(0, 4)} · indicado por ${esc(m[3])}<br>Aposentadoria obrigatória em ${m[4]}</small></div>`).join("")}
     <div class="pc"><span class="av">?</span><b>Cadeira vaga</b><small>Aberta com a aposentadoria de Luís Roberto Barroso, em outubro de 2025. A indicação é do presidente e depende de aprovação do Senado.</small></div></div>
     <p class="src">Fonte: <a href="https://portal.stf.jus.br/textos/verTexto.asp?servico=bibliotecaConsultaProdutoBibliotecaPastaMinistro&pagina=ComposicaoAtual" target="_blank" rel="noopener">STF · Composição atual</a>. Aposentadoria obrigatória aos 75 anos.</p></section>
   <p class="src">Pauta: <a href="https://portal.stf.jus.br/pauta/pesquisarCalendario.asp" target="_blank" rel="noopener">STF · Pauta de julgamentos</a>. O STF publica a pauta presencial só para as semanas próximas. Atualizado em ${new Date(STFD.gerado + "T12:00").toLocaleDateString("pt-BR")}.</p>`;
  const drawD = (d) => {
    document.querySelectorAll("#sd button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.d === d));
    const cs = STFD.dias[d] || [];
    $("#sp").innerHTML = cs.flatMap((c) => c[1].map((s) => `<div class="sess"><span class="tg" style="background:var(--ink)">${esc(c[0])}</span><b>${s[2]}ª sessão ${s[1] === "E" ? "extraordinária" : "ordinária"} · ${esc(s[0])}</b>
      ${s[3].map((i) => `<div class="it2"><a class="cd" href="https://portal.stf.jus.br/processos/listarProcessos.asp?classe=${encodeURIComponent(i[1])}&numeroProcesso=${i[2]}" target="_blank" rel="noopener">${esc(i[0] ? title(i[0]) + " · " : "")}${esc(i[1])} ${esc(i[2])}</a><span>${esc(i[8])}</span>
        <span class="small muted">Relator: ${esc(title(i[3]))}${i[4] ? " · pedido de vista: " + esc(title(i[4])) : ""}${i[5] ? " · destaque: " + esc(title(i[5])) : ""}${i[6] === "S" ? " · repercussão geral" : ""}</span></div>`).join("") || '<p class="muted small">Sem processos listados.</p>'}</div>`)).join("") || '<p class="muted">Sem sessão neste dia.</p>';
  };
  document.querySelectorAll("#sd button").forEach((b) => (b.onclick = () => drawD(b.dataset.d)));
  const comItens = dias.filter((d) => (STFD.dias[d] || []).some((c) => c[1].some((x) => x[3].length)));
  const ini = comItens.length ? comItens[comItens.length - 1] : dias[dias.length - 1];
  if (ini) drawD(ini);
}

/* ---------------- Acontece agora ---------------- */
let AG_T = null;
const haQuanto = (iso) => { const m = Math.round((Date.now() - Date.parse(iso)) / 6e4); if (m < 1) return "agora"; if (m < 60) return `há ${m} min`; const h = Math.floor(m / 60); if (h < 24) return `há ${h} h`; return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" }) + " " + new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }); };
const normT = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
/* Político citado na manchete vira link para a ficha (deputados federais e senadores em exercício).
   Casa o nome de urna completo; o sobrenome sozinho só quando é raro (7+ letras, um só parlamentar com ele) e não é nome de outra pessoa conhecida. */
let POL_IDX = null;
const semAc = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "");
const POL_FORA = new Set("bolsonaro lula moraes mendes barroso fachin dino zanin toffoli fux nunes mendonca gomes neves calheiros silva santos oliveira souza ferreira pereira costa lima alves ribeiro rodrigues martins barbosa carvalho almeida araujo vermelho junior filho neto sobrinho brasil paulo maria pastor delegado delegada coronel general capitao sargento professor professora doutor doutora tenente cabo soldado bispo irmao padre missionario policial federal reforma governo".split(" "));
function politicosNaManchete(t) {
  if (typeof BR === "undefined" || !BR || !BR.dep) return [];
  if (!POL_IDX) {
    const L = [...BR.dep.map((d) => ({ n: d[1], h: "#/p/c/" + d[0], c: "Dep." })), ...BR.sen.map((x) => ({ n: x[1], h: "#/p/s/" + x[0], c: "Sen." }))];
    const sob = {}; L.forEach((p) => { const w = semAc(p.n).split(/\s+/).pop(); sob[w] = (sob[w] || 0) + 1; });
    POL_IDX = L.map((p) => { const w = semAc(p.n).split(/\s+/); const pad = [];
      if (w.length >= 2) pad.push(w.join("\\s+"));
      const ult = w[w.length - 1]; if (ult.length >= 7 && sob[ult] === 1 && !POL_FORA.has(ult.toLowerCase())) pad.push(ult);
      return pad.length ? { ...p, re: new RegExp("(^|[^\\p{L}])(" + pad.join("|") + ")(?![\\p{L}])", "u") } : null; }).filter(Boolean);
  }
  const tt = semAc(t); const out = [];
  for (const p of POL_IDX) if (p.re.test(tt) && !out.some((o) => o.h === p.h)) { out.push(p); if (out.length >= 3) break; }
  return out;
}
/* card para Stories com o resumo do dia (1080x1920) */
async function cardResumo(el, T) {
  const W = 1080, H = 1920, cv = document.createElement("canvas"); cv.width = W; cv.height = H; const g = cv.getContext("2d");
  try { await Promise.all(["800 80px 'Bricolage Grotesque'", "700 40px 'Familjen Grotesk'", "600 30px 'JetBrains Mono'"].map((f) => document.fonts.load(f))); } catch (e) {}
  const F = (w, s, fam) => `${w} ${s}px ${fam === "m" ? "'JetBrains Mono',monospace" : fam === "d" ? "'Familjen Grotesk',sans-serif" : "'Bricolage Grotesque','Familjen Grotesk',sans-serif"}`;
  const linhas = (txt, max) => { const ws = String(txt).split(" "); const L = []; let cur = ""; ws.forEach((w) => { const n = cur ? cur + " " + w : w; if (g.measureText(n).width > max && cur) { L.push(cur); cur = w; } else cur = n; }); if (cur) L.push(cur); return L; };
  g.fillStyle = "#FBFBF7"; g.fillRect(0, 0, W, H);
  [[0, 0, "rgba(0,156,59,.22)"], [W, 560, "rgba(255,214,0,.30)"], [300, H, "rgba(30,100,235,.20)"]].forEach(([x, y, c]) => { const gr = g.createRadialGradient(x, y, 0, x, y, 1000); gr.addColorStop(0, c); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, W, H); });
  const logo = await new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = "/icon-192.png"; });
  if (logo) g.drawImage(logo, 80, 96, 76, 76);
  g.fillStyle = "#0B0B0C"; g.font = F(800, 46); g.textBaseline = "middle"; g.fillText("FISCALIZA BRASIL", 176, 136);
  g.textBaseline = "top"; g.fillStyle = "#D93025"; g.font = F(600, 30, "m"); g.fillText("RESUMO DO DIA · " + new Date().toLocaleDateString("pt-BR"), 80, 240);
  g.fillStyle = "#0B0B0C"; g.font = F(800, 92); g.fillText("O que está", 80, 290); g.fillText("em todo lugar", 80, 385);
  let y = 530;
  T.slice(0, 5).forEach((x, k) => {
    g.fillStyle = "#D93025"; g.font = F(800, 72); g.fillText(String(k + 1), 80, y - 6);
    g.fillStyle = "#0B0B0C"; g.font = F(700, 40, "d"); const L = linhas(x.t, W - 260).slice(0, 3); L.forEach((l, j) => g.fillText(l, 170, y + j * 48));
    g.fillStyle = "#5E6066"; g.font = F(600, 24, "m"); g.fillText(`${x.n} VEÍCULOS${x.cego ? " · PONTO CEGO" : ""}`, 170, y + L.length * 48 + 8);
    y += L.length * 48 + 70;
  });
  g.fillStyle = "rgba(11,11,12,.15)"; g.fillRect(80, H - 250, W - 160, 2);
  g.textAlign = "center"; g.fillStyle = "#0B0B0C"; g.font = F(800, 60); g.fillText("SIGA: @oabraaonery", W / 2, H - 225);
  g.fillStyle = "#5E6066"; g.font = F(600, 28, "m"); g.fillText("VAMOS FISCALIZAR TUDO · fiscalizaja.com.br", W / 2, H - 135); g.textAlign = "left";
  const nome = "fiscaliza-resumo-" + new Date().toISOString().slice(0, 10) + ".png";
  el.innerHTML = `<div class="btns" style="justify-content:center"><button class="btn" id="rs-dl" type="button">Baixar imagem</button><button class="btn o" id="rs-sh" type="button" hidden>Compartilhar</button></div><p class="muted small" style="margin:0;text-align:center">Imagem em 1080 × 1920, no tamanho dos Stories.</p>`;
  el.prepend(cv);
  const blob = await new Promise((ok) => cv.toBlob(ok, "image/png"));
  $("#rs-dl").onclick = () => { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = nome; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); };
  const fl = new File([blob], nome, { type: "image/png" });
  if (navigator.canShare && navigator.canShare({ files: [fl] })) { $("#rs-sh").hidden = false; $("#rs-sh").onclick = () => navigator.share({ files: [fl], title: "Resumo do dia" }).catch(() => {}); }
}
async function agora() {
  setNav("mais"); clearInterval(AG_T);
  let filtro = "todos", termo = null, data = null, lim = 40, cliques = [], cegos = new Set();
  await loadBR().catch(() => {});
  const chipsPol = (t) => { const L = politicosNaManchete(t); return L.length ? `<div class="pch">${L.map((p) => `<a href="${p.h}" title="Ver a ficha no Fiscaliza">📋 ${esc(p.n)}</a>`).join("")}</div>` : ""; };
  document.body.classList.add("wide");
  M.innerHTML = `<div class="ag"><section class="card glass ag-a"><span class="kick" style="display:flex;align-items:center;gap:8px"><i class="live"></i>Ao vivo</span><h1>Acontece agora</h1><span class="fx"></span>
     <p class="muted" style="margin:0">As manchetes de política dos principais veículos do país, atualizadas a cada poucos minutos. Toque numa manchete para ler a matéria no site do veículo.</p>
     <div id="ag-tr"></div><p class="src" id="ag-st" style="margin:0"></p></section>
   <section class="card glass ag-v" id="ag-vivo"><h2 style="display:flex;align-items:center;gap:8px"><i class="live"></i>Ao vivo no Congresso</h2><p class="muted small" style="margin:0">O que está acontecendo agora e a agenda de hoje na Câmara e no Senado: Plenário, comissões e CPIs.</p><div id="cg-l"><p class="muted small">Carregando…</p></div><p class="src" id="cg-st" style="margin:0"></p></section>
   <section class="card glass ag-r" id="ag-res"><h2>Resumo do dia em 1 minuto</h2><p class="muted small" style="margin:0">Os 5 assuntos que mais veículos estão cobrindo agora.</p><ol class="rs" id="rs-l"><li class="muted small">Carregando…</li></ol><div class="btns"><button class="btn" id="rs-card" type="button">Gerar card para Stories</button></div><div id="rs-cv"></div></section>
   <section class="card glass ag-b" id="ag-alta-c"><h2 style="display:flex;align-items:center;gap:8px">Em alta agora</h2><p class="muted small" style="margin:0">Assuntos cobertos por vários veículos ao mesmo tempo, os mais clicados aqui e as manchetes que os próprios veículos chamam de polêmica.</p><div class="lst" id="ag-alta"><p class="muted">Carregando…</p></div></section>
   <section class="card glass ag-e" id="ag-uf"><div style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap"><h2 style="margin:0" id="uf-h">Notícias do seu estado</h2><select id="uf-sel" aria-label="Estado"></select></div><p class="muted small" style="margin:0">Política do estado escolhido: g1 local, jornais do estado e a Assembleia Legislativa (onde ela publica notícias em RSS).</p><div class="lst" id="uf-l"><p class="muted small">Carregando…</p></div><p class="src" id="uf-st" style="margin:0"></p></section>
   <section class="card glass ag-w" id="ag-vid"><div style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap"><h2 style="margin:0">Vídeos e podcasts agora</h2><div class="yrs" id="vd-f"></div></div><p class="muted small" style="margin:0">Os vídeos de política mais recentes dos canais de TV e jornais no YouTube (de todos os lados) e os últimos episódios dos podcasts de política.</p><div id="vd-l"><p class="muted small">Carregando…</p></div><p class="src" id="vd-st" style="margin:0"></p></section>
   <aside class="ag-s">
     <section class="card glass sd" id="ag-ff"><div class="sdh"><span class="xlogo" style="background:#0E8A4B" aria-hidden="true">✓</span><div><h2 style="margin:0">Feito pelo Fiscaliza</h2><p class="muted small" style="margin:0">Notícias que só os nossos dados mostram</p></div></div><div class="lst" id="ff-l"><p class="muted small">Carregando…</p></div></section>
     <section class="card glass sd" id="ag-av"><div class="sdh"><span class="xlogo" style="background:#F7C21B;color:#0B0B0C" aria-hidden="true">🔔</span><div><h2 style="margin:0">Avise-me quando</h2><p class="muted small" style="margin:0">Receba no alerta diário por e-mail as manchetes sobre um tema ou político</p></div></div><div id="av-b"></div></section>
     <section class="card glass sd"><div class="sdh"><span class="xlogo" aria-hidden="true">𝕏</span><div><h2 style="margin:0">No X agora</h2><p class="muted small" style="margin:0" id="x-sub">Posts de jornalistas e veículos de todos os lados</p></div></div><div id="x-box"><p class="muted small">Carregando…</p></div></section>
     <section class="card glass sd"><div class="sdh"><span class="xlogo up" aria-hidden="true">↗</span><div><h2 style="margin:0">Em alta no Brasil</h2><p class="muted small" style="margin:0">O que as pessoas mais estão buscando agora</p></div></div><div class="yrs" id="tn-f"></div><ol class="tn" id="tn-l"><li class="muted small">Carregando…</li></ol><p class="src" id="tn-st" style="margin:0"></p></section>
     <section class="card glass sd"><div class="sdh"><span class="xlogo" style="background:#1185FE" aria-hidden="true">🦋</span><div><h2 style="margin:0">No Bluesky agora</h2><p class="muted small" style="margin:0">Posts de veículos e checadores</p></div></div><div class="lst" id="bs-l"><p class="muted small">Carregando…</p></div><p class="src" id="bs-st" style="margin:0"></p></section>
   </aside>
   <section class="card glass ag-c"><h2>Mais recentes</h2><div class="yrs" id="ag-f"></div><div class="lst" id="ag-l"></div></section>
   </div>
   <p class="src">As manchetes, os links e os horários vêm dos feeds públicos (RSS) de cada veículo, que é o dono do conteúdo. "Em alta" é calculado pela quantidade de veículos que publicaram o mesmo assunto e pelos cliques no Fiscaliza Brasil. O selo "Polêmica" aparece quando a própria manchete usa termos como polêmica, machista, racista, ataque, ameaça ou ofensa; ele não é uma opinião do Fiscaliza Brasil.</p>
   <style>body.wide main{max-width:1320px}
   .ag{display:grid;gap:16px;grid-template-columns:minmax(0,1fr);grid-template-areas:"a" "v" "r" "b" "e" "s" "w" "c"}.ag-a{grid-area:a}.ag-b{grid-area:b}.ag-c{grid-area:c}.ag-v{grid-area:v}.ag-r{grid-area:r}.ag-e{grid-area:e}.ag-w{grid-area:w}.ag-s{grid-area:s;display:grid;gap:16px;align-content:start;min-width:0}
   @media (min-width:1000px){.ag{grid-template-columns:minmax(0,1fr) 380px;grid-template-areas:"a s" "v s" "r s" "b s" "e s" "w s" "c s";align-items:start}.ag-s{position:sticky;top:76px;max-height:calc(100svh - 92px);overflow:auto;scrollbar-width:thin;border-radius:24px}}
   .sd{gap:12px}.sdh{display:flex;gap:12px;align-items:center}.xlogo{flex:none;display:grid;place-items:center;width:42px;height:42px;border-radius:13px;background:#0B0B0C;color:#fff;font-size:1.25rem;font-weight:700}.xlogo.up{background:var(--azul,#1F4FBF)}
   #x-box{display:grid;gap:10px}#x-box iframe{border-radius:16px!important}.xfb{display:grid;gap:8px;padding:14px;border-radius:16px;background:rgba(255,255,255,.78);border:1px solid rgba(11,11,12,.08)}
   .tn{list-style:none;margin:0;padding:0;display:grid;gap:8px;counter-reset:tn}.tn li.it3{counter-increment:tn;display:grid;grid-template-columns:28px minmax(0,1fr);gap:4px 10px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.78);border:1px solid rgba(11,11,12,.08)}
   .tn li.it3::before{content:counter(tn);grid-row:span 3;font-family:var(--f-display);font-weight:700;font-size:1.15rem;color:#D93025;line-height:1.2}
   .tn .tt{font-family:var(--f-display);font-weight:700;font-size:1rem;line-height:1.25;overflow-wrap:anywhere}.tn .meta{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:.78rem;color:var(--muted)}.tn .meta a{color:var(--ink);font-weight:700}
   .tn .nn{font-size:.85rem;line-height:1.35;color:inherit;text-decoration:none;overflow-wrap:anywhere}.tn .nn b{font-family:var(--f-mono);font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
   @keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.live{width:9px;height:9px;border-radius:50%;background:#D93025;display:inline-block;animation:pulse 1.6s infinite}
   .nw{display:grid;gap:5px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.78);border:1px solid rgba(11,11,12,.08);text-decoration:none;color:inherit}.nw:hover{border-color:var(--ink)}
   .nw .src2{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;font-size:.76rem;color:var(--muted);font-weight:700}.nw .src2 b{color:var(--ink);font-family:var(--f-mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase}
   .nw .ti{font-family:var(--f-display);font-weight:700;font-size:1.02rem;line-height:1.25}
   .hot{display:grid;gap:8px;padding:14px;border-radius:18px;background:linear-gradient(135deg,rgba(255,255,255,.9),rgba(255,240,230,.85));border:1px solid rgba(217,48,37,.25)}
   .hot .ti{font-family:var(--f-display);font-weight:700;font-size:1.12rem;line-height:1.22;text-decoration:none;color:inherit}
   .tg2{display:inline-flex;align-items:center;gap:5px;font-family:var(--f-mono);font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:4px 10px;border-radius:999px;color:#fff;background:#D93025}
   .tg2.pol{background:#0B0B0C}.tg2.clk{background:var(--azul)}.rk{font-family:var(--f-display);font-weight:700;font-size:1.4rem;color:#D93025;line-height:1}
   .cob{display:none;gap:6px}.cob.on{display:grid}.cob a{font-size:.88rem;text-decoration:none;color:inherit;padding:6px 0;border-top:1px solid rgba(11,11,12,.08)}.cob a b{font-family:var(--f-mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;margin-right:6px}
   .tg2.cego{background:#6B3FA0}.pch{display:flex;flex-wrap:wrap;gap:6px}.pch a{font-size:.74rem;font-weight:700;text-decoration:none;color:var(--ink);background:rgba(31,79,191,.08);border:1px solid rgba(31,79,191,.25);border-radius:999px;padding:3px 10px}.pch a:hover{background:rgba(31,79,191,.16)}
   .nw a.ti{color:inherit;text-decoration:none}.nw a.ti:hover{text-decoration:underline}
   .cg{display:grid;gap:8px;margin:0;padding:0;list-style:none}.cg li{display:grid;grid-template-columns:56px minmax(0,1fr);gap:2px 12px;padding:10px 12px;border-radius:14px;background:rgba(255,255,255,.78);border:1px solid rgba(11,11,12,.08)}
   .cg li.on{border-color:rgba(217,48,37,.45);background:linear-gradient(135deg,rgba(255,255,255,.92),rgba(255,236,232,.9))}.cg .hr{font-family:var(--f-mono);font-weight:700;font-size:.9rem;grid-row:span 2}.cg .hr small{display:block;color:#D93025;font-size:.62rem;letter-spacing:.06em}
   .cg .ds{font-size:.88rem;line-height:1.3;overflow-wrap:anywhere}.cg .mt{font-size:.75rem;color:var(--muted);display:flex;gap:4px 10px;flex-wrap:wrap}.cg .mt a{color:var(--ink);font-weight:700}.cg li.x{opacity:.55}.cg[hidden]{display:none}
   .rs{margin:0;padding:0;list-style:none;display:grid;gap:8px;counter-reset:rs}.rs li{counter-increment:rs;display:grid;grid-template-columns:30px minmax(0,1fr);gap:2px 10px;align-items:start}.rs li::before{content:counter(rs);font-family:var(--f-display);font-weight:800;font-size:1.3rem;color:#D93025;grid-row:span 2;line-height:1.1}
   .rs a{font-family:var(--f-display);font-weight:700;line-height:1.25;color:inherit;text-decoration:none}.rs small{color:var(--muted)}#rs-cv canvas{width:100%;max-width:320px;height:auto;border-radius:18px;display:block;margin:6px auto;box-shadow:0 10px 30px rgba(0,0,0,.15)}
   .vds{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(220px,260px);gap:12px;overflow-x:auto;padding-bottom:6px;scroll-snap-type:x mandatory}.vd{scroll-snap-align:start;display:grid;gap:6px;text-decoration:none;color:inherit}.vd img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:14px;background:#ddd}
   .vd b{font-family:var(--f-mono);font-size:.68rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}.vd span{font-family:var(--f-display);font-weight:700;font-size:.92rem;line-height:1.25;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
   .bs{display:grid;gap:4px;padding:10px 12px;border-radius:14px;background:rgba(255,255,255,.78);border:1px solid rgba(11,11,12,.08);text-decoration:none;color:inherit;font-size:.86rem;line-height:1.35}.bs b{font-size:.74rem}.bs span{overflow-wrap:anywhere;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden}
   .avf{display:flex;gap:8px;flex-wrap:wrap}.avf input{flex:1;min-width:150px;border:1px solid rgba(11,11,12,.18);border-radius:999px;padding:9px 14px;font:inherit;background:rgba(255,255,255,.85)}.avc{display:flex;flex-wrap:wrap;gap:6px}.avc button{border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.8);border-radius:999px;padding:5px 11px;font-size:.8rem;font-weight:700}.avc button.on{background:var(--ink);color:#fff}
   #uf-sel{border:1px solid rgba(11,11,12,.18);border-radius:999px;padding:7px 12px;font:inherit;font-weight:700;background:rgba(255,255,255,.85)}
   .trend{display:flex;gap:6px;flex-wrap:wrap}.trend button{border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.75);border-radius:999px;padding:6px 12px;font-weight:700;font-size:.85rem}.trend button[aria-pressed="true"]{background:var(--ink);color:#fff}.trend small{color:var(--muted);font-weight:600;margin-left:4px}</style>`;
  const fontes = () => Object.fromEntries(data.fontes.map((f) => [f.id, f]));
  const clique = (it) => { try { const sb = sbClient(); if (sb) sb.rpc("noticia_clique", { p_url: it.l, p_titulo: it.t, p_fonte: it.s }).then(() => {}, () => {}); } catch (e) {} };
  const linkHTML = (it, cls) => `<a class="${cls}" href="${esc(it.l)}" target="_blank" rel="noopener" data-u="${esc(it.l)}">`;
  const wireClicks = (root) => root.querySelectorAll("a[data-u]").forEach((a) => (a.onclick = () => { const it = data.itens.find((x) => x.l === a.dataset.u); if (it) clique(it); }));
  const drawAlta = () => {
    const F = fontes(); const box = $("#ag-alta"); const cards = [];
    const ck = {}; cliques.forEach((c) => (ck[c.url] = (ck[c.url] || 0) + c.cliques));
    const grupos = (data.alta || []).map((g) => { const its = g.ids.map((i) => data.itens[i]).filter(Boolean); const c = its.reduce((a, it) => a + (ck[it.l] || 0), 0); return { ...g, its, c, sc: g.score + Math.min(6, c / 5) }; }).sort((a, b) => b.sc - a.sc);
    const usados = new Set(grupos.flatMap((g) => g.its.map((i) => i.l)));
    const maisClic = cliques.filter((c) => !usados.has(c.url)).sort((a, b) => b.cliques - a.cliques).slice(0, 3);
    grupos.slice(0, 8).forEach((g, k) => {
      const pri = g.its.slice().sort((a, b) => (F[b.s] && F[b.s].grupo === "Agências oficiais") - (F[a.s] && F[a.s].grupo === "Agências oficiais") || a.d.localeCompare(b.d))[0];
      cards.push(`<div class="hot"><div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span class="rk">${k + 1}</span>${g.n >= 2 ? `<span class="tg2">🔥 Em alta · ${g.n} veículos</span>` : ""}${g.polem ? `<span class="tg2 pol">⚠ Polêmica</span>` : ""}${g.cego ? `<span class="tg2 cego" title="Só veículos de um dos lados publicaram este assunto">👁 Ponto cego · só ${g.cego === "e" ? "a direita" : "a esquerda"} está cobrindo</span>` : ""}${g.c ? `<span class="tg2 clk">${mil(g.c)} cliques</span>` : ""}<span class="small muted">${haQuanto(g.ult)}</span></div>
        ${linkHTML(pri, "ti")}${esc(pri.t)}</a>${chipsPol(g.its.map((x) => x.t).join(" · "))}<span class="small muted">${esc((F[pri.s] || {}).nome || pri.s)}${g.its.length > 1 ? ` e mais ${g.its.length - 1}` : ""}</span>
        ${g.its.length > 1 ? `<button class="btn o" style="justify-self:start;padding:8px 14px" data-cob="${k}">Ver cobertura (${g.its.length})</button><div class="cob" id="cob${k}">${g.its.map((it) => `${linkHTML(it, "")}<b>${esc((F[it.s] || {}).nome || it.s)}</b>${esc(it.t)}</a>`).join("")}</div>` : ""}</div>`);
    });
    maisClic.forEach((c) => cards.push(`<div class="hot"><div style="display:flex;gap:10px;align-items:center"><span class="tg2 clk">Mais clicada · ${mil(c.cliques)}</span></div><a class="ti" href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.titulo || c.url)}</a><span class="small muted">${esc((F[c.fonte] || {}).nome || c.fonte || "")}</span></div>`));
    box.innerHTML = cards.join("") || '<p class="muted">Nenhum assunto em alta agora.</p>';
    box.querySelectorAll("[data-cob]").forEach((b) => (b.onclick = () => { const c = $("#cob" + b.dataset.cob); c.classList.toggle("on"); b.textContent = c.classList.contains("on") ? "Fechar cobertura" : `Ver cobertura (${c.children.length})`; }));
    wireClicks(box);
  };
  const drawLista = () => {
    const F = fontes(); const grupos = [...new Set(data.fontes.map((f) => f.grupo))];
    $("#ag-f").innerHTML = [["todos", "Todos"], ["pol", "⚠ Polêmicas"], ["cego", "👁 Ponto cego"], ...grupos.map((g) => ["g:" + g, g]), ...data.fontes.filter((f) => f.ok).map((f) => ["s:" + f.id, f.nome])].map(([k, n]) => `<button data-k="${esc(k)}" aria-pressed="${k === filtro}">${esc(n)}</button>`).join("");
    document.querySelectorAll("#ag-f button").forEach((b) => (b.onclick = () => { filtro = b.dataset.k; lim = 40; drawLista(); }));
    const f = data.itens.filter((i) => (filtro === "todos" || (filtro === "pol" ? i.p : filtro === "cego" ? cegos.has(i.l) : filtro.startsWith("s:") ? i.s === filtro.slice(2) : (F[i.s] || {}).grupo === filtro.slice(2))) && (!termo || normT(i.t).includes(normT(termo))));
    $("#ag-l").innerHTML = (termo ? `<div class="note">Mostrando manchetes sobre <b>${esc(termo)}</b>. <a href="#" id="ag-x">Limpar</a></div>` : "") + f.slice(0, lim).map((i) => `<div class="nw"><span class="src2"><b>${esc((F[i.s] || {}).nome || i.s)}</b><span>${haQuanto(i.d)}</span>${i.p ? '<span class="tg2 pol" style="padding:2px 8px">⚠ Polêmica</span>' : ""}${cegos.has(i.l) ? '<span class="tg2 cego" style="padding:2px 8px">👁 Ponto cego</span>' : ""}</span>${linkHTML(i, "ti")}${esc(i.t)}</a>${chipsPol(i.t)}</div>`).join("") || '<p class="muted">Nenhuma manchete.</p>';
    if (termo) $("#ag-x").onclick = (e) => { e.preventDefault(); termo = null; drawTr(); drawLista(); };
    if (f.length > lim) { $("#ag-l").insertAdjacentHTML("beforeend", '<button class="btn o more" id="ag-m">Ver mais</button>'); $("#ag-m").onclick = () => { lim += 40; drawLista(); }; }
    wireClicks($("#ag-l"));
  };
  const drawTr = () => {
    const a = data.assuntos || [];
    $("#ag-tr").innerHTML = a.length ? `<div class="kick" style="margin:4px 0 6px">Assuntos do momento</div><div class="trend">${a.map(([n, c]) => `<button data-t="${esc(n)}" aria-pressed="${n === termo}">${esc(n)}<small>${c}</small></button>`).join("")}</div>` : "";
    document.querySelectorAll("#ag-tr button").forEach((b) => (b.onclick = () => { termo = termo === b.dataset.t ? null : b.dataset.t; drawTr(); drawLista(); $("#ag-l").scrollIntoView({ behavior: "smooth", block: "start" }); }));
  };
  const draw = () => { cegos = new Set((data.alta || []).filter((g) => g.cego).flatMap((g) => g.ids.map((i) => (data.itens[i] || {}).l)));
    drawTr(); drawAlta(); drawLista(); drawResumo(); drawAvise();
    const off = data.fontes.filter((x) => !x.ok).map((x) => x.nome);
    $("#ag-st").textContent = `Atualizado às ${new Date(data.gerado).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })} · ${data.fontes.filter((x) => x.ok).length} veículos` + (off.length ? ` · fora do ar agora: ${off.join(", ")}` : ""); };
  try { const g = JSON.parse(localStorage.getItem("fb_noticias") || "null"); if (g && g.itens) { data = g; draw(); } } catch (err) {}
  const load = async () => {
    try {
      const r = await fetch("/api/noticias", { cache: "no-store" }); if (!r.ok) throw new Error(r.status); data = await r.json();
      if (data.parcial && (load.n = (load.n || 0) + 1) < 6) setTimeout(load, 4000);
      try { localStorage.setItem("fb_noticias", JSON.stringify(data)); } catch (err) {}
      try { const sb = sbClient(); if (sb) { const ontem = new Date(Date.now() - 864e5).toISOString().slice(0, 10); const q = await sb.from("noticias_cliques").select("url,titulo,fonte,cliques").gte("dia", ontem).order("cliques", { ascending: false }).limit(50); if (!q.error) cliques = q.data || []; } } catch (e) {}
      draw();
    } catch (e) { if (!data) { $("#ag-alta").innerHTML = '<div class="note">As manchetes ao vivo funcionam no site publicado (elas vêm de um servidor do Fiscaliza Brasil no Cloudflare). Nesta página de teste elas não carregam.</div>'; $("#ag-l").innerHTML = ""; } }
  };

  /* lateral: lista do X (configurada no painel) */
  const xLista = async () => {
    const box = $("#x-box"); let url = null;
    try { url = localStorage.getItem("fb_xlista"); } catch (e) {}
    try { const sb = sbClient(); if (sb) { const q = await sb.from("site_config").select("valor").eq("chave", "x_lista").maybeSingle(); if (!q.error) { url = (q.data && q.data.valor) || null; try { url ? localStorage.setItem("fb_xlista", url) : localStorage.removeItem("fb_xlista"); } catch (e) {} } } } catch (e) {}
    if (!url) { box.innerHTML = '<div class="xfb"><b>A lista do X ainda não foi escolhida.</b><span class="small muted">No painel, abra "Lateral do X" e cole o endereço de uma lista pública do X.</span></div>'; return; }
    const abrir = `<a class="btn o" style="justify-self:start;padding:9px 16px;text-decoration:none" href="${esc(url)}" target="_blank" rel="noopener">Abrir a lista no X</a>`;
    box.innerHTML = `<a class="twitter-timeline" data-height="640" data-dnt="true" data-lang="pt" data-chrome="noheader nofooter transparent noborders" href="${esc(url)}">Carregando posts do X…</a>${abrir}`;
    // o X só "desenha" a lista quando consegue mostrar posts; o iframe pode existir vazio (lista exige login, bloqueio do navegador)
    let ok = false;
    const liga = () => { try { twttr.events.bind("rendered", (ev) => { if (box.contains(ev.target)) { const f = box.querySelector("iframe"); ok = !!(f && (f.offsetHeight > 120 || parseInt(f.style.height) > 120)); } }); } catch (e) {} };
    if (window.twttr && twttr.widgets) { liga(); twttr.widgets.load(box); }
    else if (!document.getElementById("x-wjs")) { window.twttr = window.twttr || { _e: [], ready(f) { this._e.push(f); } }; twttr.ready(liga); const sc = document.createElement("script"); sc.id = "x-wjs"; sc.async = true; sc.src = "https://platform.twitter.com/widgets.js"; document.head.append(sc); }
    setTimeout(() => { const f = box.querySelector("iframe"); if (f && (f.offsetHeight > 120 || parseInt(f.style.height) > 120)) ok = true; if ($("#x-box") && !ok) $("#x-box").innerHTML = `<div class="xfb"><b>O X não mostrou os posts aqui.</b><span class="small muted">Às vezes o X só exibe listas para quem está logado nele, ou o navegador bloqueia o conteúdo do X. Pela lista você vê tudo direto no X.</span>${abrir}</div>`; }, 9000);
  };
  /* lateral: em alta no Brasil (Google Trends) */
  let tFiltro = "pol", tData = null;
  const drawTend = () => {
    const its = (tData.itens || []).filter((x) => tFiltro === "tudo" || x.pol);
    $("#tn-f").innerHTML = [["pol", "Política"], ["tudo", "Tudo"]].map(([k, n]) => `<button data-k="${k}" aria-pressed="${k === tFiltro}">${n}</button>`).join("");
    $("#tn-f").querySelectorAll("button").forEach((b) => (b.onclick = () => { tFiltro = b.dataset.k; drawTend(); }));
    $("#tn-l").innerHTML = its.length ? its.slice(0, 15).map((x) => `<li class="it3"><span class="tt">${esc(x.t)}</span><span class="meta">${x.tr ? `<span>${esc(x.tr)} buscas</span>` : ""}<a href="https://x.com/search?q=${encodeURIComponent(x.t)}&f=live" target="_blank" rel="noopener">Ver no X</a><a href="#" data-q="${esc(x.t)}">Manchetes aqui</a></span>${x.n && x.n[0] ? `<a class="nn" href="${esc(x.n[0].u)}" target="_blank" rel="noopener"><b>${esc(x.n[0].s)}</b> · ${esc(x.n[0].t)}</a>` : ""}</li>`).join("")
      : `<li class="muted small">${tFiltro === "pol" ? 'Nenhum assunto de política entre os mais buscados agora. Toque em "Tudo" para ver todos.' : "Nada por aqui agora."}</li>`;
    $("#tn-l").querySelectorAll("[data-q]").forEach((a) => (a.onclick = (e) => { e.preventDefault(); termo = a.dataset.q; drawTr(); drawLista(); $("#ag-l").scrollIntoView({ behavior: "smooth", block: "start" }); }));
    $("#tn-st").textContent = `Fonte: ${tData.fonte || "Google Trends"}` + (tData.gerado ? ` · atualizado às ${new Date(tData.gerado).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}` : "");
  };
  const loadTend = async () => {
    try { const r = await fetch("/api/tendencias", { cache: "no-store" }); if (!r.ok) throw new Error(r.status); tData = await r.json(); drawTend(); }
    catch (e) { if (!tData) $("#tn-l").innerHTML = '<li class="muted small">Os assuntos em alta funcionam no site publicado (vêm do servidor do Fiscaliza Brasil no Cloudflare).</li>'; }
  };

  /* resumo do dia: os 5 assuntos com mais veículos; botão gera o card para Stories */
  const topo5 = () => { const F = fontes(); return (data.alta || []).map((g) => ({ ...g, its: g.ids.map((i) => data.itens[i]).filter(Boolean) })).filter((g) => g.its.length && g.n >= 2).sort((a, b) => b.n - a.n || b.score - a.score).slice(0, 5)
    .map((g) => { const pri = g.its.slice().sort((a, b) => ((F[b.s] || {}).grupo === "Agências oficiais") - ((F[a.s] || {}).grupo === "Agências oficiais") || a.d.localeCompare(b.d))[0]; return { t: pri.t, l: pri.l, n: g.n, s: (F[pri.s] || {}).nome || pri.s, cego: g.cego }; }); };
  const drawResumo = () => {
    const T = topo5();
    $("#rs-l").innerHTML = T.length ? T.map((x) => `<li><a href="${esc(x.l)}" target="_blank" rel="noopener">${esc(x.t)}</a><small>${x.n} veículos · primeiro a dar: ${esc(x.s)}${x.cego ? " · 👁 ponto cego" : ""}</small></li>`).join("") : '<li class="muted small">Ainda não há assuntos cobertos por vários veículos hoje.</li>';
    $("#rs-card").hidden = !T.length; $("#rs-card").onclick = () => cardResumo($("#rs-cv"), T);
  };
  /* avise-me: temas guardados em Acompanhando (tipo "tema"); vão no alerta diário por e-mail */
  const drawAvise = () => {
    const box = $("#av-b"); if (!box || !window.FBAcomp) return;
    const meus = FBAcomp.ler().itens.filter((i) => i.tipo === "tema");
    const sug = (data && data.assuntos || []).map(([n]) => n).filter((n) => !meus.some((m) => normT(m.ref) === normT(n))).slice(0, 6);
    box.innerHTML = `<form class="avf" id="av-f"><input id="av-i" maxlength="60" placeholder="Ex.: reforma tributária, Nikolas Ferreira" aria-label="Tema ou político"><button class="btn" type="submit">Avisar</button></form>
      ${meus.length ? `<div class="kick" style="margin:10px 0 4px">Você será avisado sobre</div><div class="avc">${meus.map((m) => `<button class="on" data-del="${esc(m.ref)}" title="Parar de avisar">${esc(m.ref)} ✕</button>`).join("")}</div>` : ""}
      ${sug.length ? `<div class="kick" style="margin:10px 0 4px">Assuntos do momento</div><div class="avc">${sug.map((n) => `<button data-add="${esc(n)}">+ ${esc(n)}</button>`).join("")}</div>` : ""}
      <p class="muted small" style="margin:8px 0 0">O aviso chega no <a href="#/acompanho">alerta diário</a>: entre com o seu e-mail na página Acompanhando e marque "alerta diário". Os temas ficam guardados junto com os políticos que você acompanha.</p>`;
    const add = (t) => { t = String(t || "").trim().replace(/\s+/g, " ").slice(0, 60); if (t.length < 3) return; if (!FBAcomp.tem("tema", t)) FBAcomp.alternar({ tipo: "tema", ref: t, nome: t }); if (typeof toast2 === "function") toast2(`Pronto: vamos avisar sobre "${t}".`); drawAvise(); };
    $("#av-f").onsubmit = (e) => { e.preventDefault(); add($("#av-i").value); };
    box.querySelectorAll("[data-add]").forEach((b) => (b.onclick = () => add(b.dataset.add)));
    box.querySelectorAll("[data-del]").forEach((b) => (b.onclick = () => { FBAcomp.alternar({ tipo: "tema", ref: b.dataset.del }); drawAvise(); }));
  };
  /* ao vivo no Congresso */
  const loadCongresso = async () => {
    try {
      const r = await fetch("/api/congresso", { cache: "no-store" }); if (!r.ok) throw new Error(r.status); const j = await r.json();
      const ev = j.ev || []; const vivo = ev.filter((e) => e.sit === "andamento" || e.sit === "suspensa"); const prox = ev.filter((e) => e.sit === "agendada"); const fim = ev.filter((e) => e.sit === "encerrada" || e.sit === "cancelada");
      const li = (e) => `<li class="${e.sit === "andamento" ? "on" : e.sit === "cancelada" ? "x" : ""}"><span class="hr">${esc(e.h || "")}${e.sit === "andamento" ? "<small>AO VIVO</small>" : e.sit === "suspensa" ? "<small>SUSPENSA</small>" : e.sit === "cancelada" ? "<small style='color:var(--muted)'>CANCELADA</small>" : e.sit === "encerrada" ? "<small style='color:var(--muted)'>ENCERRADA</small>" : ""}</span>
        <span class="ds"><b>${e.casa === "C" ? "Câmara" : "Senado"} · ${esc(e.plen ? (e.casa === "C" ? "Plenário" : "Plenário do Senado") : e.org)}</b>${e.cpi ? ' <span class="tg2" style="padding:1px 8px">CPI</span>' : ""} ${esc(e.tipo)}${e.d ? ": " + esc(e.d) : ""}</span>
        <span class="mt">${e.orgn && !e.plen ? `<span>${esc(e.orgn)}</span>` : ""}<a href="${esc(e.u)}" target="_blank" rel="noopener">${e.sit === "andamento" ? "Assistir agora" : /youtu/.test(e.u) ? "Ver gravação" : "Página oficial"}</a></span></li>`;
      const mostra = [...vivo, ...prox.slice(0, Math.max(3, 8 - vivo.length))]; const resto = [...prox.slice(mostra.length - vivo.length), ...fim];
      $("#cg-l").innerHTML = (vivo.length ? "" : '<p class="muted small" style="margin:6px 0">Nada transmitido ao vivo neste momento.</p>') + (mostra.length ? `<ul class="cg">${mostra.map(li).join("")}</ul>` : '<p class="muted small">Sem sessões nem reuniões marcadas para hoje.</p>')
        + (resto.length ? `<button class="btn o" style="justify-self:start;padding:8px 14px;margin-top:8px" id="cg-m">Ver a agenda completa de hoje (${ev.length})</button><ul class="cg" id="cg-r" hidden style="margin-top:8px">${resto.map(li).join("")}</ul>` : "");
      if ($("#cg-m")) $("#cg-m").onclick = () => { $("#cg-r").hidden = !$("#cg-r").hidden; $("#cg-m").textContent = $("#cg-r").hidden ? `Ver a agenda completa de hoje (${ev.length})` : "Fechar a agenda"; };
      $("#cg-st").textContent = `Fonte: Dados Abertos da Câmara e do Senado (agenda de ${new Date(j.dia + "T12:00").toLocaleDateString("pt-BR")}) · atualizado às ${new Date(j.gerado).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}` + (!j.ok.camara ? " · a Câmara não respondeu agora" : "") + (!j.ok.senado ? " · o Senado não respondeu agora" : "");
    } catch (e) { $("#cg-l").innerHTML = '<p class="muted small">A agenda ao vivo funciona no site publicado (vem do servidor do Fiscaliza Brasil no Cloudflare).</p>'; }
  };
  /* notícias do seu estado */
  const UFS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];
  let ufN = (() => { try { return localStorage.getItem("fb_uf_noticias") || (store.get("cidade") || {}).uf || ""; } catch (e) { return ""; } })();
  const loadRegional = async () => {
    const sel = $("#uf-sel"); sel.innerHTML = `<option value="">Escolha o estado</option>` + UFS.map((u) => `<option value="${u}"${u === ufN ? " selected" : ""}>${u}</option>`).join("");
    sel.onchange = () => { ufN = sel.value; try { localStorage.setItem("fb_uf_noticias", ufN); } catch (e) {} loadRegional(); };
    if (!ufN) { $("#uf-l").innerHTML = '<p class="muted small">Escolha o estado ao lado (ou a sua cidade em "Me representa") para ver a política local.</p>'; $("#uf-st").textContent = ""; return; }
    $("#uf-h").textContent = "Notícias do seu estado · " + ufN;
    try {
      const r = await fetch("/api/regional?uf=" + ufN, { cache: "no-store" }); if (!r.ok) throw new Error(r.status); const j = await r.json(); const N = Object.fromEntries(j.fontes.map((f) => [f.id, f.nome]));
      $("#uf-l").innerHTML = j.itens.slice(0, 12).map((i) => `<div class="nw"><span class="src2"><b>${esc(N[i.s] || i.s)}</b><span>${haQuanto(i.d)}</span></span><a class="ti" href="${esc(i.l)}" target="_blank" rel="noopener">${esc(i.t)}</a>${chipsPol(i.t)}</div>`).join("") || '<p class="muted small">Nenhuma notícia de política do estado nos últimos dias.</p>';
      $("#uf-st").textContent = "Fontes: " + j.fontes.filter((f) => f.ok).map((f) => f.nome).join(", ") + ". Cada manchete leva à matéria no site do veículo.";
    } catch (e) { $("#uf-l").innerHTML = '<p class="muted small">As notícias do estado funcionam no site publicado.</p>'; }
  };
  /* vídeos e podcasts */
  let vdTipo = "v", vdData = null;
  const drawVideos = () => {
    $("#vd-f").innerHTML = [["v", "Vídeos"], ["p", "Podcasts"]].map(([k, n]) => `<button data-k="${k}" aria-pressed="${k === vdTipo}">${n}</button>`).join("");
    $("#vd-f").querySelectorAll("button").forEach((b) => (b.onclick = () => { vdTipo = b.dataset.k; drawVideos(); }));
    const N = Object.fromEntries(vdData.fontes.map((f) => [f.id, f.nome])); const its = vdData.itens.filter((i) => i.s.startsWith(vdTipo + "-"));
    $("#vd-l").innerHTML = !its.length ? '<p class="muted small">Nada novo agora.</p>' : vdTipo === "v"
      ? `<div class="vds">${its.slice(0, 24).map((i) => `<a class="vd" href="${esc(i.l)}" target="_blank" rel="noopener">${i.img ? `<img src="${esc(i.img)}" alt="" loading="lazy">` : ""}<b>${esc(N[i.s] || "")} · ${haQuanto(i.d)}</b><span>${esc(i.t)}</span></a>`).join("")}</div>`
      : `<div class="lst">${its.slice(0, 12).map((i) => `<a class="nw" href="${esc(i.l)}" target="_blank" rel="noopener"><span class="src2"><b>🎧 ${esc(N[i.s] || "")}</b><span>${haQuanto(i.d)}</span></span><span class="ti">${esc(i.t)}</span></a>`).join("")}</div>`;
    $("#vd-st").textContent = `Canais e podcasts: ${vdData.fontes.filter((f) => f.ok && f.id.startsWith(vdTipo + "-")).map((f) => f.nome).join(", ")}. O vídeo e o áudio abrem no site de cada um.`;
  };
  const loadVideos = async () => { try { const r = await fetch("/api/videos", { cache: "no-store" }); if (!r.ok) throw new Error(r.status); vdData = await r.json(); drawVideos(); } catch (e) { $("#vd-l").innerHTML = '<p class="muted small">Os vídeos funcionam no site publicado.</p>'; } };
  /* Bluesky */
  const loadBsky = async () => {
    try { const r = await fetch("/api/bluesky", { cache: "no-store" }); if (!r.ok) throw new Error(r.status); const j = await r.json(); const N = Object.fromEntries(j.fontes.map((f) => [f.id, f.nome]));
      $("#bs-l").innerHTML = j.itens.slice(0, 15).map((i) => `<a class="bs" href="${esc(i.l)}" target="_blank" rel="noopener"><b>${esc(N[i.s] || "")} · <span class="muted">${haQuanto(i.d)}</span></b><span>${esc(i.t)}</span></a>`).join("") || '<p class="muted small">Nada novo agora.</p>';
      $("#bs-st").textContent = "Do RSS público de cada perfil no Bluesky.";
    } catch (e) { $("#bs-l").innerHTML = '<p class="muted small">Os posts do Bluesky funcionam no site publicado.</p>'; }
  };
  /* feito pelo Fiscaliza: votações nominais recentes e quem votou contra o partido (dados nossos) */
  const feitoFiscaliza = async () => {
    try {
      const [VCa, VSa, S] = await Promise.all([getJSON("data/camara_votacoes.json").catch(() => []), getJSON("data/senado_votacoes.json").catch(() => []), getJSON("data/semana.json").catch(() => null)]);
      const lim = new Date(Date.now() - 10 * 864e5).toISOString().slice(0, 10); const it = [];
      VCa.forEach((x, i) => { if (x && x[1] >= lim && !/requerimento/i.test(x[7] || "")) it.push([x[1], `<b>Câmara</b> ${x[2] === "1" ? "aprovou" : "rejeitou"} ${esc(x[5] || "votação")} por ${x[3]} a ${x[4]}. <a href="#/votacao/C/${i}">Como votou cada deputado</a>`]); });
      VSa.forEach((x, i) => { if (x && x[1] >= lim && !/requerimento/i.test(x[4] || "")) it.push([x[1], `<b>Senado</b> ${x[5] === "A" ? "aprovou" : "rejeitou"} ${esc(x[2] || "votação")}${x[6] === "S" ? " em voto secreto" : ` por ${x[7]} a ${x[8]}`}. <a href="#/votacao/S/${i}">Como votou cada senador</a>`]); });
      it.sort((a, b) => b[0].localeCompare(a[0]));
      const w = S && S.semanas && S.semanas[0]; const contra = w ? (w.contra || []).slice().sort((a, b) => b[5] - a[5]).slice(0, 4) : [];
      const dt = (d) => new Date(d + "T12:00").toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
      $("#ff-l").innerHTML = (it.length ? it.slice(0, 5).map(([d, h]) => `<div class="nw" style="font-size:.88rem"><span class="src2"><b>Votação nominal</b><span>${dt(d)}</span></span><span>${h}</span></div>`).join("") : '<p class="muted small">Sem votações nominais no Plenário nos últimos 10 dias.</p>')
        + (contra.length ? `<div class="nw" style="font-size:.88rem"><span class="src2"><b>Votaram contra o próprio partido</b><span>semana de ${dt(w.seg)}</span></span><span>${contra.map((c) => `<a href="#/p/${c[0] === "C" ? "c" : "s"}/${c[1]}">${esc(c[2])}</a> (${esc(c[3])}-${esc(c[4])}) ${c[5]}×`).join(" · ")}</span></div>` : "")
        + '<a class="btn o" style="justify-self:start;padding:8px 14px;text-decoration:none" href="#/semana">A semana no Congresso</a>';
    } catch (e) { $("#ff-l").innerHTML = '<p class="muted small">Não consegui carregar agora.</p>'; }
  };
  xLista(); loadTend(); loadCongresso(); loadRegional(); loadVideos(); loadBsky(); feitoFiscaliza();
  await load();
  AG_T = setInterval(() => { if (location.hash.startsWith("#/agora")) { load(); loadTend(); loadCongresso(); } else clearInterval(AG_T); }, 120000);
}
