/* RESUMO DA SEMANA (#/semana) e VOTAÇÕES QUE IMPORTAM (#/votacoes). */
(function css() {
  const s = document.createElement("style");
  s.textContent = `
  .vimp{display:grid;gap:8px;padding:14px;border-radius:18px;background:rgba(255,255,255,.75);border:1px solid rgba(11,11,12,.08)}
  .vimp .hd{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:center}
  .vimp .cd{font-family:var(--f-mono);font-size:.78rem;font-weight:600}
  .vimp .ti{font-family:var(--f-display);font-weight:700;font-size:1.05rem;line-height:1.3}
  .vimp .pl{display:flex;flex-wrap:wrap;gap:5px}
  .vimp .pl span{font-family:var(--f-mono);font-size:.66rem;font-weight:600;letter-spacing:.04em;padding:4px 8px;border-radius:999px;border:1px solid rgba(11,11,12,.16)}
  .vimp .pl span.s{background:var(--ink);color:#fff;border-color:var(--ink)}
  .res2{font-family:var(--f-mono);font-size:.7rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:5px 9px;border-radius:999px}
  .res2.a{background:#E3F4EA;color:#14703C}.res2.r{background:#FDE7E5;color:#B3261E}
  .wk{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px}
  .wk div{padding:12px;border-radius:16px;background:rgba(255,255,255,.7);border:1px solid rgba(11,11,12,.08);display:grid;gap:2px}
  .wk b{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:1.7rem;line-height:1}
  .wk span{font-family:var(--f-display);font-weight:700;font-size:.62rem;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
  .prow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:9px 0;border-top:1px solid rgba(11,11,12,.08);text-decoration:none;color:inherit}
  .prow b{font-family:var(--f-display)}.prow small{color:var(--muted)}.prow i{font-style:normal;font-family:var(--f-mono);font-weight:600;font-size:.78rem}`;
  document.head.append(s);
})();

const dataBR = (d) => new Date(d + "T12:00").toLocaleDateString("pt-BR");
const frase1 = (t) => { const s = String(t || "").replace(/\s+/g, " ").replace(/NOVA EMENTA:.*$/i, "").trim(); const m = s.match(/^.{20,240}?[.;](\s|$)/); return (m ? m[0] : s.slice(0, 220)).trim(); };
function linhaVot(casa, i, VL) {
  const x = VL[i]; const C = casa === "C";
  const tit = C ? x[5] : x[2], ement = C ? (x[6] || x[7]) : (x[3] || x[4]);
  const apr = C ? x[2] === "1" : x[5] === "A", rej = C ? x[2] === "0" : x[5] === "R";
  const sim = C ? x[3] : x[7], nao = C ? x[4] : x[8], secreta = !C && x[6] === "S";
  const pos = PART ? (C ? PART.cam : PART.sen) : {};
  const pl = Object.entries(pos).filter(([s]) => (PART.stat[s] || {})[C ? "dep" : "sen"] >= (C ? 3 : 2)).map(([s, p]) => [s, p[i]]).filter(([, v]) => v === "S" || v === "N").sort((a, b) => (PART.stat[b[0]][C ? "dep" : "sen"]) - (PART.stat[a[0]][C ? "dep" : "sen"]));
  return `<div class="vimp"><div class="hd"><span class="cd">${C ? "CÂMARA" : "SENADO"} · ${esc(tit || "Votação")} · ${dataBR(x[1])}</span>${apr ? '<span class="res2 a">Aprovado</span>' : rej ? '<span class="res2 r">Rejeitado</span>' : ""}</div>
    <div class="ti">${esc(frase1(ement))}</div>
    ${(C ? x[7] : x[4]) ? `<div class="small"><b>Votação:</b> ${esc(frase1(C ? x[7] : x[4]))}</div>` : ""}
    <div class="small muted">${secreta ? "Votação secreta" : `Sim ${mil(sim)} × Não ${mil(nao)}`}${C && x[8] ? " · Governo orientou " + esc(x[8]) : ""}</div>
    ${pl.length ? `<div class="pl">${pl.map(([s, v]) => `<span class="${v === "S" ? "s" : ""}" title="A maioria do ${esc(s)} votou ${v === "S" ? "Sim" : "Não"}">${esc(s)} ${v === "S" ? "SIM" : "NÃO"}</span>`).join("")}</div>` : ""}<a class="small" style="font-weight:700" href="#/votacao/${casa}/${i}">${secreta ? "Ver detalhes →" : `Como votou cada ${C ? "deputado" : "senador"} do seu estado · card para Stories →`}</a></div>`;
}

async function votacoesImportam() {
  setNav("congresso"); document.title = "Votações que importam · Fiscaliza Brasil";
  M.innerHTML = `<section class="card glass"><span class="kick">Congresso</span><h1>Votações que importam</h1><span class="fx"></span><p class="muted small" style="margin:0">Carregando…</p></section>`;
  await loadPart(); const VC = await loadVC(), VS = await loadVS();
  const lim = new Date(); lim.setFullYear(lim.getFullYear() - 1); const L0 = lim.toISOString().slice(0, 10);
  // relevância: propostas de mudança de lei (não requerimentos), muitos votantes e placar disputado
  const cam = VC.map((x, i) => [i, x]).filter(([, x]) => x[1] >= L0 && /^(PEC|PLP|PL|MPV|PDL|PLV)\b/.test(x[5] || "") && !/requerimento/i.test(x[7] || "") && x[3] + x[4] >= 300)
    .map(([i, x]) => [i, (x[3] + x[4]) * (1 - Math.abs(x[3] - x[4]) / (x[3] + x[4]) * 0.6) * (/^PEC/.test(x[5]) ? 1.3 : 1)]).sort((a, b) => b[1] - a[1]).slice(0, 15).map((a) => a[0]).sort((a, b) => VC[b][1].localeCompare(VC[a][1]));
  const sen = VS.map((x, i) => [i, x]).filter(([, x]) => x[1] >= L0 && x[6] !== "S" && /^(PEC|PLP|PL|MPV|PDL|PLV)\b/.test(x[2] || "") && !/requerimento/i.test(x[4] || "") && x[7] + x[8] >= 50)
    .map(([i, x]) => [i, (x[7] + x[8]) * (1 - Math.abs(x[7] - x[8]) / (x[7] + x[8]) * 0.6) * (/^PEC/.test(x[2]) ? 1.3 : 1)]).sort((a, b) => b[1] - a[1]).slice(0, 10).map((a) => a[0]).sort((a, b) => VS[b][1].localeCompare(VS[a][1]));
  M.innerHTML = `<section class="card glass"><span class="kick">Congresso</span><h1>Votações que importam</h1><span class="fx"></span>
     <p class="muted" style="margin:0">As votações mais disputadas e com mais parlamentares dos últimos 12 meses: mudanças na Constituição, leis complementares, projetos de lei e medidas provisórias. Os selos mostram como votou a maioria de cada partido. <b>Preto = Sim</b>, contorno = Não.</p>
     <div class="btns"><a class="btn o" href="#/semana">Resumo da semana</a><a class="btn o" href="#/congresso">Pauta e calendário</a></div></section>
   <section class="card glass"><h2>Câmara dos Deputados</h2><div style="display:grid;gap:10px">${cam.map((i) => linhaVot("C", i, VC)).join("") || '<p class="muted">Sem votações no período.</p>'}</div></section>
   <section class="card glass"><h2>Senado Federal</h2><div style="display:grid;gap:10px">${sen.map((i) => linhaVot("S", i, VS)).join("") || '<p class="muted">Sem votações no período.</p>'}</div></section>
   <p class="src">Critério: votações nominais do Plenário de propostas (PEC, PLP, PL, MPV, PDL), sem requerimentos, com pelo menos 300 deputados ou 50 senadores votando; quanto mais votantes e mais apertado o placar, mais alto na escolha. Posição do partido = voto da maioria da bancada. Fontes: ${FONTE_CAM} · ${FONTE_SEN}.</p>`;
}

async function semanaCongresso(n) {
  setNav("congresso"); document.title = "Resumo da semana · Fiscaliza Brasil";
  M.innerHTML = `<section class="card glass"><span class="kick">Resumo da semana</span><h1>A semana no Congresso</h1><span class="fx"></span><p class="muted small" style="margin:0">Carregando…</p></section>`;
  await loadPart(); const VC = await loadVC(), VS = await loadVS(); const S = await getJSON("data/semana.json");
  const k = Math.min(+n || 0, S.semanas.length - 1); const w = S.semanas[k]; if (!w) { M.innerHTML = '<section class="card glass"><p class="muted">Sem dados.</p></section>'; return; }
  const ini = new Date(w.seg + "T12:00"), fim = new Date(ini); fim.setDate(fim.getDate() + 6);
  const per = `${ini.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })} a ${fim.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" })}`;
  const pessoa = (x, val) => `<a class="prow" href="#/p/${x[0] === "C" ? "c" : "s"}/${x[1]}"><span><b>${esc(x[2])}</b> <small>${esc(x[3])}-${esc(x[4])} · ${x[0] === "C" ? "deputado(a)" : "senador(a)"}</small></span><i>${val}</i></a>`;
  const txt = `A semana no Congresso (${per}): ${w.c.length + w.s.length} votações no Plenário, ${w.aprov} aprovadas e ${w.rej} rejeitadas. Veja como cada um votou no Fiscaliza Brasil: ${location.origin}/fiscalize#/semana`;
  M.innerHTML = `<section class="card glass"><span class="kick">Resumo da semana</span><h1>A semana no Congresso</h1><span class="fx"></span>
     <p class="muted" style="margin:0">Semana de ${per}. As votações do Plenário, quem não registrou voto e quem votou contra o próprio partido.</p>
     <div class="yrs">${S.semanas.map((s, i) => `<button type="button" data-w="${i}" aria-pressed="${i === k}">${new Date(s.seg + "T12:00").toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })}</button>`).join("")}</div>
     <div class="wk"><div><b>${w.c.length}</b><span>Votações na Câmara</span></div><div><b>${w.s.length}</b><span>Votações no Senado</span></div><div><b style="color:#14703C">${w.aprov}</b><span>Aprovadas</span></div><div><b style="color:#B3261E">${w.rej}</b><span>Rejeitadas</span></div></div>
     <div class="btns"><a class="btn" target="_blank" rel="noopener" href="https://wa.me/?text=${encodeURIComponent(txt)}">Compartilhar no WhatsApp</a><a class="btn o" href="#/votacoes">Votações que importam</a></div></section>
   ${w.c.length + w.s.length ? `<section class="card glass"><h2>O que foi votado</h2><div style="display:grid;gap:10px">${w.c.slice().reverse().map((i) => linhaVot("C", i, VC)).join("")}${w.s.slice().reverse().map((i) => linhaVot("S", i, VS)).join("")}</div></section>` : ""}
   ${w.falt.length ? `<section class="card glass"><h2>Quem mais deixou de votar</h2><p class="muted small" style="margin:0">Parlamentares que não registraram voto na maior parte das votações da semana. Pode ser falta, licença, missão oficial ou não ter votado estando presente.</p><div>${w.falt.map((x) => pessoa(x, `${x[5]} de ${x[6]} sem voto`)).join("")}</div></section>` : ""}
   ${w.contra.length ? `<section class="card glass"><h2>Quem votou contra o próprio partido</h2><div>${w.contra.map((x) => pessoa(x, `${x[5]} voto${x[5] > 1 ? "s" : ""} contra`)).join("")}</div></section>` : ""}
   <p class="src">Posição do partido = voto da maioria da bancada. Veja <a href="#/metodologia">Como calculamos</a>. Fontes: ${FONTE_CAM} · ${FONTE_SEN}.</p>`;
  document.querySelectorAll("[data-w]").forEach((b) => (b.onclick = () => semanaCongresso(b.dataset.w)));
}

/* ---------- COMO VOTOU CADA UM (#/votacao/C/índice/UF) e CARD PARA STORIES da votação ---------- */
const deUF = (n) => (/^(Bahia|Paraíba)$/.test(n) ? "da " : /^(Acre|Amapá|Amazonas|Ceará|Distrito Federal|Espírito Santo|Maranhão|Mato Grosso|Mato Grosso do Sul|Pará|Paraná|Piauí|Rio de Janeiro|Rio Grande do Norte|Rio Grande do Sul|Tocantins)$/.test(n) ? "do " : "de ") + n;
const VNOME = { S: "Sim", N: "Não", A: "Abstenção", O: "Obstrução", P: "Presidiu a sessão", R: "Presidiu a sessão", V: "Votou (secreta)" };
async function votacaoPag(casa, i, uf) {
  casa = casa === "S" ? "S" : "C"; i = +i; const C = casa === "C";
  setNav("congresso"); await loadBR();
  const meu = store.get("cidade"); uf = (uf || (meu && meu.uf) || "PR").toUpperCase(); if (!BR.ufs[uf]) uf = "PR";
  M.innerHTML = `<section class="card glass"><span class="kick">Votação</span><h1>Carregando…</h1></section>`;
  const VL = C ? await loadVC() : await loadVS(); const x = VL[i]; if (!x) return notFound();
  const tit = C ? x[5] : x[2]; let ement = frase1(C ? (x[6] || x[7]) : (x[3] || x[4])); if (!/[.;)]$/.test(ement)) ement = ement.replace(/\s+\S*$/, "").replace(/[,;:]$/, "") + "…";
  const apr = C ? x[2] === "1" : x[5] === "A", rej = C ? x[2] === "0" : x[5] === "R", secreta = !C && x[6] === "S";
  const sim = C ? x[3] : x[7], nao = C ? x[4] : x[8]; const oque = String((C ? x[7] : x[4]) || "").replace(/\s+/g, " ").trim().replace(/^Votação nominal (d[oa]s?|de) /i, "").replace(/^./, (c) => c.toUpperCase());
  const V = C ? await loadC(uf) : await loadS(uf);
  const gente = C ? BR.dep.filter((d) => d[3] === uf).map((d) => ({ id: String(d[0]), nome: d[1], part: d[2], foto: d[4], h: "#/p/c/" + d[0] }))
    : BR.sen.filter((s) => s[4] === uf).map((s) => ({ id: String(s[0]), nome: s[1], part: s[3], foto: s[5], h: "#/p/s/" + s[0] }));
  const G = { S: [], N: [], outro: [], fora: [] };
  gente.forEach((p) => { const v = ((V[p.id] || {}).v || "")[i]; p.voto = v;
    if (v === "S" || v === "N") G[v].push(p); else if (v && v !== "-" && v !== "?") G.outro.push(p); else if ((V[p.id] || {}).v) G.fora.push(p); });
  // quem não tem registro nenhum (ainda não estava no mandato) não entra na conta
  const doc = document.title = `${tit || "Votação"} · como votou ${uf} · Fiscaliza Brasil`;
  const casaN = C ? "Câmara dos Deputados" : "Senado Federal", quemN = C ? "deputados federais" : "senadores";
  const lista = (arr, rot) => arr.length ? `<h3>${rot} <span class="muted small">(${arr.length})</span></h3><div>${arr.map((p) => `<a class="prow" href="${p.h}"><span><b>${esc(p.nome)}</b> <small>${esc(p.part)}</small></span><i>${esc(VNOME[p.voto] || "Não registrou voto")}</i></a>`).join("")}</div>` : "";
  M.innerHTML = `<section class="card glass"><a class="muted small" href="#/votacoes">← Votações que importam</a><span class="kick">${casaN} · ${esc(tit || "Votação")} · ${dataBR(x[1])}</span><h1 style="font-size:clamp(1.3rem,3.6vw,1.9rem)">${esc(ement)}</h1><span class="fx"></span>
     ${oque ? `<p style="margin:0 0 8px"><b>O que foi votado:</b> ${esc(oque)}</p>` : ""}
     <div class="chips">${apr ? '<span class="res2 a">Aprovado</span>' : rej ? '<span class="res2 r">Rejeitado</span>' : ""}<span class="chip">${secreta ? "Votação secreta" : `Placar geral: Sim ${mil(sim)} × Não ${mil(nao)}`}</span>${C && x[8] ? `<span class="chip">Governo orientou ${esc(x[8])}</span>` : ""}</div>
     <p class="muted small" style="margin:8px 0 4px">Escolha o estado:</p><div class="chips">${Object.keys(BR.ufs).sort().map((u) => `<a class="chip${u === uf ? " on" : ""}" aria-pressed="${u === uf}" style="${u === uf ? "background:var(--ink);color:var(--bg,#fff)" : ""}" href="#/votacao/${casa}/${i}/${u}">${u}</a>`).join("")}</div><div class="btns" style="margin-top:10px"><button class="btn o" id="vlk" type="button">Copiar link desta votação</button></div></section>
   <div class="row2"><section class="card glass"><h2>Como votaram os ${quemN} ${deUF(BR.ufs[uf].nome)}</h2>
     ${secreta ? '<p class="muted">Votação secreta: o Senado não publica o voto de cada senador.</p>' : lista(G.S, "Sim") + lista(G.N, "Não") + lista(G.outro, "Outro registro") + lista(G.fora, "Não registraram voto")}
     <p class="src">Voto registrado no painel do Plenário. "Não registrou voto" inclui ausência, licença e falta de registro; os dados abertos não dizem o motivo. Partido = partido atual. Fonte: ${C ? FONTE_CAM : FONTE_SEN}.</p></section>
    <section class="card glass"><h2>Card para Stories</h2><div id="vstc">${secreta ? '<p class="muted">Sem card: a votação foi secreta.</p>' : '<p class="muted">Montando a imagem…</p>'}</div></section></div>`;
  const link = "https://fiscalizaja.com.br/votacao/" + casa + "/" + i + "/" + uf;
  $("#vlk").onclick = async () => { try { if (navigator.share && /Mobi/i.test(navigator.userAgent)) await navigator.share({ title: document.title, url: link }); else { await navigator.clipboard.writeText(link); $("#vlk").textContent = "Link copiado ✓"; } } catch (e) {} };
  if (!secreta) cardVotacao($("#vstc"), { casa, uf, ufN: BR.ufs[uf].nome, tit, ement, oque, data: dataBR(x[1]), apr, rej, sim, nao, G });
}

async function cardVotacao(el, o) {
  const W = 1080, H = 1920, cv = document.createElement("canvas"); cv.width = W; cv.height = H; const g = cv.getContext("2d");
  try { await Promise.all(["800 80px 'Bricolage Grotesque'", "700 40px 'Familjen Grotesk'", "600 30px 'JetBrains Mono'"].map((f) => document.fonts.load(f))); } catch (e) {}
  const F = (w, s, fam) => `${w} ${s}px ${fam === "m" ? "'JetBrains Mono',monospace" : fam === "d" ? "'Familjen Grotesk',sans-serif" : "'Bricolage Grotesque','Familjen Grotesk',sans-serif"}`;
  const rr = (x, y, w, h, r) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };
  const quebra = (t, max) => { const ws = String(t).split(" "); const L = []; let cur = ""; ws.forEach((w) => { const n = cur ? cur + " " + w : w; if (g.measureText(n).width > max && cur) { L.push(cur); cur = w; } else cur = n; }); if (cur) L.push(cur); return L; };
  g.fillStyle = "#FBFBF7"; g.fillRect(0, 0, W, H);
  [[0, 0, "rgba(0,156,59,.24)"], [W, 560, "rgba(255,214,0,.32)"], [300, H, "rgba(30,100,235,.22)"]].forEach(([x, y, c]) => { const gr = g.createRadialGradient(x, y, 0, x, y, 1000); gr.addColorStop(0, c); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, W, H); });
  const logo = await new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = "/icon-192.png"; });
  if (logo) { g.save(); rr(80, 96, 76, 76, 20); g.clip(); g.drawImage(logo, 80, 96, 76, 76); g.restore(); }
  g.fillStyle = "#0B0B0C"; g.font = F(800, 46); g.textBaseline = "middle"; g.fillText("FISCALIZA BRASIL", 176, 136);
  g.textBaseline = "top"; let y = 230;
  g.fillStyle = "#5E6066"; g.font = F(600, 28, "m"); g.fillText(((o.casa === "C" ? "Câmara" : "Senado") + " · " + (o.tit || "Votação") + " · " + o.data).toUpperCase(), 80, y); y += 56;
  let fs = 60; g.font = F(800, fs); let L = quebra(o.ement, W - 160); while (L.length > 4 && fs > 40) { fs -= 4; g.font = F(800, fs); L = quebra(o.ement, W - 160); }
  if (L.length > 4) { L = L.slice(0, 4); L[3] = L[3].replace(/\s*\S*$/, "") + "…"; }
  g.fillStyle = "#0B0B0C"; L.forEach((l) => { g.fillText(l, 80, y); y += fs * 1.08; });
  if (o.oque) { y += 6; g.font = F(700, 30, "d"); g.fillStyle = "#5E6066"; let q = quebra("Votação: " + o.oque, W - 160); if (q.length > 2) { q = q.slice(0, 2); q[1] = q[1].replace(/\s*\S*$/, "") + "…"; } q.forEach((l) => { g.fillText(l, 80, y); y += 38; }); }
  y += 18; g.font = F(700, 34, "d"); const res = (o.apr ? "APROVADO" : o.rej ? "REJEITADO" : "") ; 
  if (res) { const tw = g.measureText(res).width; rr(80, y, tw + 48, 60, 30); g.fillStyle = o.apr ? "#14703C" : "#B3261E"; g.fill(); g.fillStyle = "#fff"; g.fillText(res, 104, y + 13); }
  g.fillStyle = "#5E6066"; g.font = F(700, 32, "d"); g.fillText(`Placar geral: Sim ${mil(o.sim)} × Não ${mil(o.nao)}`, res ? 80 + g.measureText(res).width + 90 : 80, y + 13); y += 100;
  [["#0E8A4B", 0], ["#F7C21B", 1], ["#1F4FBF", 2]].forEach(([c, k]) => { g.fillStyle = c; g.fillRect(80 + k * 48, y, 48, 10); }); y += 44;
  g.fillStyle = "#0B0B0C"; const cab = `COMO VOTOU ${o.casa === "C" ? "CADA DEPUTADO" : "CADA SENADOR"} ${deUF(o.ufN).split(" ")[0].toUpperCase()} ${o.uf}`; let hf = 50; g.font = F(800, hf); while (g.measureText(cab).width > W - 160 && hf > 30) { hf -= 2; g.font = F(800, hf); } g.fillText(cab, 80, y); y += 84;
  // duas colunas: SIM e NÃO; embaixo, quem não votou
  const fim = H - 300, cw = (W - 160 - 24) / 2;
  const nomes = (arr) => arr.map((p) => p.nome + " (" + p.part + ")");
  const disp = fim - y - (o.G.outro.length || o.G.fora.length ? 150 : 0);
  // nomes quebram em duas linhas quando não cabem; a letra diminui até tudo caber
  const linhasDe = (arr, lf) => { g.font = F(700, lf, "d"); return nomes(arr).flatMap((n) => { return quebra(n, cw - 64); }); };
  let lf = 46, LS, LN; for (;;) { LS = linhasDe(o.G.S, lf); LN = linhasDe(o.G.N, lf); if (110 + Math.max(LS.length, LN.length) * lf * 1.3 + 30 <= disp || lf <= 22) break; lf -= 2; }
  const colH = Math.min(disp, Math.max(380, 110 + Math.max(LS.length, LN.length) * lf * 1.3 + 30));
  [["SIM", o.G.S, LS, "#0B0B0C", "#fff"], ["NÃO", o.G.N, LN, "rgba(255,255,255,.78)", "#0B0B0C"]].forEach(([rot, arr, ls, bg, fg], k) => {
    const x = 80 + k * (cw + 24); g.save(); g.shadowColor = "rgba(15,20,30,.10)"; g.shadowBlur = 30; g.shadowOffsetY = 8; rr(x, y, cw, colH, 36); g.fillStyle = bg; g.fill(); g.restore();
    if (k) { g.strokeStyle = "rgba(11,11,12,.25)"; g.lineWidth = 3; rr(x, y, cw, colH, 36); g.stroke(); }
    g.fillStyle = fg; g.font = F(800, 64); g.fillText(rot + " · " + arr.length, x + 32, y + 26);
    g.font = F(700, lf, "d"); const max = Math.floor((colH - 140) / (lf * 1.3) + 0.01); let L2 = ls; if (ls.length > max) L2 = ls.slice(0, max - 1).concat([`+ ${ls.length - max + 1} linhas no site`]);
    L2.forEach((t, j) => { let u = t; while (g.measureText(u).width > cw - 64 && u.length > 4) u = u.slice(0, -2); g.fillText(u === t ? t : u.slice(0, -1) + "…", x + 32, y + 110 + j * lf * 1.3); });
  });
  y += colH + 30;
  const resto = [o.G.outro.length ? o.G.outro.length + " com outro registro (abstenção, obstrução ou presidência)" : "", o.G.fora.length ? o.G.fora.length + " não registraram voto" : ""].filter(Boolean).join(" · ");
  if (resto) { g.font = F(700, 32, "d"); const rl = quebra(resto, W - 232).slice(0, 2); rr(80, y, W - 160, 50 + rl.length * 42, 32); g.fillStyle = "rgba(255,255,255,.78)"; g.fill(); g.fillStyle = "#0B0B0C"; rl.forEach((t, j) => g.fillText(t, 116, y + 26 + j * 42)); }
  g.textBaseline = "middle";
  g.fillStyle = "rgba(11,11,12,.15)"; g.fillRect(80, H - 250, W - 160, 2);
  g.textAlign = "center"; g.fillStyle = "#0B0B0C"; g.font = F(800, 60); g.fillText("SIGA: @oabraaonery", W / 2, H - 200);
  g.fillStyle = "#5E6066"; g.font = F(600, 28, "m"); g.fillText("VAMOS FISCALIZAR TUDO · fiscalizaja.com.br", W / 2, H - 112); g.textAlign = "left";
  const nome = "votacao-" + String(o.tit || "card").toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, "-") + "-" + o.uf.toLowerCase() + ".png";
  el.innerHTML = `<div class="storyw"></div><div class="btns" style="justify-content:center"><button class="btn" id="vdl" type="button">Baixar imagem</button><button class="btn o" id="vsh" type="button" hidden>Compartilhar</button></div><p class="muted small" style="margin:0;text-align:center">Imagem em 1080 × 1920, no tamanho dos Stories.</p>`;
  el.querySelector(".storyw").append(cv);
  let blob = null; try { blob = await new Promise((ok) => cv.toBlob(ok, "image/png")); } catch (e) {}
  $("#vdl").onclick = () => { if (!blob) return; const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = nome; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); };
  if (blob && navigator.canShare && navigator.canShare({ files: [new File([blob], nome, { type: "image/png" })] })) { $("#vsh").hidden = false; $("#vsh").onclick = () => navigator.share({ files: [new File([blob], nome, { type: "image/png" })] }).catch(() => {}); }
}
