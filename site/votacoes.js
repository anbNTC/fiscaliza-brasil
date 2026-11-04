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
    <div class="small muted">${secreta ? "Votação secreta" : `Sim ${mil(sim)} × Não ${mil(nao)}`}${C && x[8] ? " · Governo orientou " + esc(x[8]) : ""}</div>
    ${pl.length ? `<div class="pl">${pl.map(([s, v]) => `<span class="${v === "S" ? "s" : ""}" title="A maioria do ${esc(s)} votou ${v === "S" ? "Sim" : "Não"}">${esc(s)} ${v === "S" ? "SIM" : "NÃO"}</span>`).join("")}</div>` : ""}</div>`;
}

async function votacoesImportam() {
  setNav("congresso"); document.title = "Votações que importam · Fiscaliza Brasil";
  M.innerHTML = `<section class="card glass"><span class="kick">Congresso</span><h1>Votações que importam</h1><span class="fx"></span><p class="muted small" style="margin:0">Carregando…</p></section>`;
  await loadPart(); const VC = await loadVC(), VS = await loadVS();
  const lim = new Date(); lim.setFullYear(lim.getFullYear() - 1); const L0 = lim.toISOString().slice(0, 10);
  // relevância: propostas de mudança de lei (não requerimentos), muitos votantes e placar disputado
  const cam = VC.map((x, i) => [i, x]).filter(([, x]) => x[1] >= L0 && /^(PEC|PLP|PL|MPV|PDL|PLV)\b/.test(x[5] || "") && !/requerimento/i.test(x[7] || "") && x[3] + x[4] >= 300)
    .map(([i, x]) => [i, (x[3] + x[4]) * (1 - Math.abs(x[3] - x[4]) / (x[3] + x[4]) * 0.6) * (/^PEC/.test(x[5]) ? 1.3 : 1)]).sort((a, b) => b[1] - a[1]).slice(0, 15).map((a) => a[0]).sort((a, b) => VC[b][1].localeCompare(VC[a][1]));
  const sen = VS.map((x, i) => [i, x]).filter(([, x]) => x[1] >= L0 && x[6] !== "S" && /^(PEC|PLP|PL|MPV|PDL|PLV)\b/.test(x[2] || "") && x[7] + x[8] >= 50)
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
