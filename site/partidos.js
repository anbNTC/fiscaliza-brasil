/* PARTIDOS: os 30 partidos registrados no TSE, o que cada um diz defender e como a bancada vota.
   Rotas: #/partidos e #/partidos/<SIGLA>. Dados em data/partidos.json (gerado por build/partidos/partidos.py).
   Verde = votou com a posição do partido; vermelho = votou contra. Posição do partido = voto da maioria da bancada. */
let PART = null;
const loadPart = async () => PART || (PART = await getJSON("data/partidos.json"));

(function css() {
  const s = document.createElement("style");
  s.textContent = `
  .selo{--c1:#0B0B0C;--c2:#F2C200;flex:none;width:56px;height:56px;border-radius:18px;display:grid;place-items:center;position:relative;overflow:hidden;
    background:linear-gradient(135deg,var(--c1) 0 62%,var(--c2) 62% 100%);color:#fff;box-shadow:0 8px 20px rgba(15,20,30,.16),inset 0 0 0 2px rgba(255,255,255,.35)}
  .selo b{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:.86rem;letter-spacing:-.01em;line-height:1;text-shadow:0 1px 2px rgba(0,0,0,.35);max-width:90%;overflow:hidden;text-overflow:clip;white-space:nowrap}
  .selo i{position:absolute;right:5px;bottom:4px;font-style:normal;font-family:var(--f-mono);font-weight:600;font-size:.58rem;color:#0B0B0C;background:rgba(255,255,255,.85);border-radius:6px;padding:1px 4px}
  .selo.lg{width:96px;height:96px;border-radius:26px}.selo.lg b{font-size:1.35rem}.selo.lg i{font-size:.72rem;right:7px;bottom:6px}
  .pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
  .pcard{display:grid;grid-template-columns:auto minmax(0,1fr);gap:14px;align-items:center;padding:16px;border-radius:20px;background:rgba(255,255,255,.75);border:1px solid rgba(11,11,12,.08);text-decoration:none;color:inherit}
  .pcard:hover{border-color:var(--ink)}
  .pcard .t{font-family:var(--f-display);font-weight:700;font-size:1rem;line-height:1.2;text-transform:uppercase;letter-spacing:.02em}
  .pcard .s{font-size:.8rem;color:var(--muted);line-height:1.35}
  .meter{display:flex;height:8px;border-radius:999px;overflow:hidden;background:rgba(11,11,12,.08)}
  .meter .g{background:#1E9E55}.meter .r{background:#D93025}
  .pnum{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px}
  .pnum div{padding:12px;border-radius:16px;background:rgba(255,255,255,.7);border:1px solid rgba(11,11,12,.08);display:grid;gap:2px}
  .pnum b{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:1.6rem;line-height:1}
  .pnum span{font-family:var(--f-display);font-weight:700;font-size:.62rem;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
  .defs{display:flex;flex-wrap:wrap;gap:6px}
  .rkrow{display:grid;grid-template-columns:44px 44px minmax(0,1fr) 120px;gap:12px;align-items:center;padding:10px 0;border-top:1px solid rgba(11,11,12,.08);text-decoration:none;color:inherit}
  .rkrow .av{width:44px;height:44px;border-radius:13px;font-size:.9rem}.rkrow b{font-family:var(--f-display);font-size:.95rem}.rkrow small{display:block;color:var(--muted);font-size:.76rem}
  .rkrow .pc2{font-family:var(--f-mono);font-weight:600;font-size:.72rem;text-align:right;display:grid;gap:4px}
  .rkn{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:1.3rem;text-align:center;color:var(--ink)}
  @media (max-width:520px){.rkrow{grid-template-columns:30px 40px minmax(0,1fr) 84px;gap:8px}.rkn{font-size:1rem}}
  #rkp{padding:8px 12px;border-radius:999px;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.8);font:inherit;font-weight:700;font-size:.85rem}
  .mrow{display:grid;grid-template-columns:44px minmax(0,1fr) 120px;gap:12px;align-items:center;padding:10px 0;border-top:1px solid rgba(11,11,12,.08);text-decoration:none;color:inherit}
  .mrow .av{width:44px;height:44px;border-radius:13px;font-size:.9rem}
  .mrow b{font-family:var(--f-display);font-size:.95rem}.mrow small{display:block;color:var(--muted);font-size:.76rem}
  .mrow .pc2{font-family:var(--f-mono);font-weight:600;font-size:.72rem;text-align:right;display:grid;gap:4px}
  @media (max-width:520px){.mrow{grid-template-columns:40px minmax(0,1fr) 84px}}
  .vrow{display:grid;gap:6px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.75);border:1px solid rgba(11,11,12,.08)}
  .vrow[hidden]{display:none}.vrow .hd{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:center}
  .vrow .cd{font-family:var(--f-mono);font-size:.78rem;font-weight:600}
  .tagv{display:inline-flex;align-items:center;gap:5px;font-family:var(--f-mono);font-size:.68rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:5px 9px;border-radius:999px;line-height:1}
  .tagv.g{background:#E3F4EA;color:#14703C}.tagv.r{background:#FDE7E5;color:#B3261E}.tagv.n{background:rgba(11,11,12,.07);color:var(--ink)}
  .who{font-size:.82rem;line-height:1.45}.who .r{color:#B3261E;font-weight:600}
  .acbtn[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}`;
  document.head.append(s);
})();

const selo = (p, cls) => `<span class="selo ${cls || ""}" style="--c1:${p.cor[0]};--c2:${p.cor[1]}" aria-hidden="true"><b>${esc(p.s)}</b><i>${p.n}</i></span>`;
const meter = (a, c) => { const t = a + c; return t ? `<span class="meter" title="${Math.round(100 * a / t)}% com o partido"><span class="g" style="width:${100 * a / t}%"></span><span class="r" style="width:${100 * c / t}%"></span></span>` : ""; };
const pctx = (x) => (x == null ? "—" : String(x).replace(".", ",") + "%");

async function partidos(sig) {
  setNav("partidos"); await loadPart();
  if (sig) return partidoPg(decodeURIComponent(sig));
  document.title = "Partidos · Fiscaliza Brasil";
  const L = PART.partidos.slice(); const S = PART.stat;
  const com = L.filter((p) => S[p.s].dep + S[p.s].sen > 0).sort((a, b) => (S[b.s].dep + S[b.s].sen) - (S[a.s].dep + S[a.s].sen));
  const sem = L.filter((p) => S[p.s].dep + S[p.s].sen === 0).sort((a, b) => a.s.localeCompare(b.s));
  const card = (p) => { const s = S[p.s]; return `<a class="pcard" href="#/partidos/${encodeURIComponent(p.s)}">${selo(p)}<span style="display:grid;gap:5px;min-width:0"><span class="t">${esc(p.nome)}</span>
     <span class="s">${s.dep || s.sen ? `${s.dep} deputado${s.dep === 1 ? "" : "s"} · ${s.sen} senador${s.sen === 1 ? "" : "es"}` : "Sem parlamentares no Congresso"}${s.coes != null ? ` · votam juntos ${pctx(s.coes)}` : ""}</span>${meter(s.a, s.c)}</span></a>`; };
  M.innerHTML = `<section class="card glass"><span class="kick">Partidos</span><h1>Os 30 partidos do Brasil</h1><span class="fx"></span>
     <p class="muted" style="margin:0">O que cada partido diz defender e como os seus deputados e senadores votam de verdade. <b style="color:#14703C">Verde</b> é quando o parlamentar votou junto com o partido; <b style="color:#B3261E">vermelho</b>, quando votou contra.</p></section>
   <section class="card glass"><h2 style="margin:0">Com parlamentares no Congresso <span class="muted small">(${com.length})</span></h2><div class="pgrid">${com.map(card).join("")}</div></section>
   <section class="card glass" id="rk"><h2 style="margin:0">Ranking: quem mais vota contra o próprio partido</h2>
     <p class="muted small" style="margin:0">Do 1º, quem menos votou junto com o partido, ao último, quem mais votou. Entram deputados e senadores com pelo menos ${RK_MIN} votos em que o partido teve posição.</p>
     <div class="sel" style="display:flex;gap:8px;flex-wrap:wrap"><div class="yrs" id="rkc">${[["", "Câmara e Senado"], ["C", "Câmara"], ["S", "Senado"]].map(([k, n]) => `<button type="button" data-c="${k}" aria-pressed="${k === ""}">${n}</button>`).join("")}</div>
      <select id="rkp" aria-label="Partido"><option value="">Todos os partidos</option>${com.map((p) => `<option value="${esc(p.s)}">${esc(p.s)} · ${esc(p.nome)}</option>`).join("")}</select></div>
     <div id="rkl"></div></section>
   <section class="card glass"><h2 style="margin:0">Sem parlamentares no Congresso <span class="muted small">(${sem.length})</span></h2><div class="pgrid">${sem.map(card).join("")}</div></section>
   <p class="src">Ranking: em cada votação nominal, a posição do partido é o voto da maioria dos seus parlamentares; abstenções e ausências não entram na conta. Partidos registrados no TSE em 2026. Selo com a sigla, o número e as cores de cada partido (não é a logomarca oficial). Fontes: <a href="${PART.fonte_estatutos}" target="_blank" rel="noopener">TSE · partidos registrados, estatutos e programas</a> · ${FONTE_CAM} · ${FONTE_SEN}.</p>`;
  // ranking de todos os parlamentares
  const todos = com.flatMap((p) => S[p.s].membros.map((m) => ({ p, m, t: m[5] + m[6], pc: m[5] + m[6] ? m[5] / (m[5] + m[6]) : 1 }))).filter((x) => x.t >= RK_MIN)
    .sort((a, b) => a.pc - b.pc || b.m[6] - a.m[6]);
  let casa = "", par = "", lim = 20;
  const draw = () => {
    const f = todos.filter((x) => (!casa || x.m[0] === casa) && (!par || x.p.s === par));
    $("#rkl").innerHTML = `<p class="muted small" style="margin:0 0 4px">${f.length} parlamentares</p>` + f.slice(0, lim).map((x, i) => { const m = x.m;
      return `<a class="rkrow" href="#/p/${m[0] === "C" ? "c" : "s"}/${m[1]}"><span class="rkn">${i + 1}º</span>${av(m[2], m[4])}<span style="min-width:0"><b>${esc(m[2])}</b><small>${esc(x.p.s)} · ${m[0] === "C" ? "Deputado(a)" : "Senador(a)"} · ${esc(m[3])}</small></span>
        <span class="pc2"><span><span style="color:#14703C">${(Math.round(1000 * x.pc) / 10).toString().replace(".", ",")}% com</span><br><span style="color:#B3261E">${m[6]} contra</span></span>${meter(m[5], m[6])}</span></a>`; }).join("")
      + (f.length > lim ? `<button class="btn o more" id="rkm" type="button">Ver mais (${f.length - lim})</button>` : "");
    if ($("#rkm")) $("#rkm").onclick = () => { lim += 40; draw(); };
  };
  document.querySelectorAll("#rkc button").forEach((b) => (b.onclick = () => { casa = b.dataset.c; lim = 20; document.querySelectorAll("#rkc button").forEach((x) => x.setAttribute("aria-pressed", x === b)); draw(); }));
  $("#rkp").onchange = (e) => { par = e.target.value; lim = 20; draw(); };
  draw();
}
const RK_MIN = 30;

async function partidoPg(sig) {
  const p = PART.partidos.find((x) => x.s === sig); if (!p) return notFound();
  const s = PART.stat[p.s]; document.title = `${p.nome} · Partidos · Fiscaliza Brasil`;
  const VCx = s.rec.length ? await loadVC() : null; const VSx = s.recS.length ? await loadVS() : null;
  const vrow = (r, VL, casa) => { const x = VL[r[0]]; const pos = r[1] === "S" ? "Sim" : "Não";
    const tit = casa === "C" ? x[5] : x[2], txt = casa === "C" ? (x[6] || x[7]) : (x[3] || x[4]);
    return `<div class="vrow"><div class="hd"><span class="cd">${esc(tit || "Votação")} · ${new Date(x[1] + "T12:00").toLocaleDateString("pt-BR")}</span><span class="tagv n">Partido votou ${pos}</span></div>
      <div class="small">${esc(String(txt || "").slice(0, 220))}</div>
      <div class="who"><span class="tagv g">● ${r[2]} com o partido</span> ${r[3].length ? `<span class="tagv r">● ${r[3].length} contra</span> <span class="r">${r[3].map(esc).join(", ")}</span>` : ""}</div></div>`; };
  const mrow = (m) => { const href = "#/p/" + (m[0] === "C" ? "c/" : "s/") + m[1]; const t = m[5] + m[6];
    return `<a class="mrow" href="${href}">${av(m[2], m[4])}<span style="min-width:0"><b>${esc(m[2])}</b><small>${m[0] === "C" ? "Deputado(a) federal" : "Senador(a)"} · ${esc(m[3])}</small></span>
      <span class="pc2">${t ? `<span><span style="color:#14703C">${Math.round(100 * m[5] / t)}% com</span><br><span style="color:#B3261E">${m[6]} contra</span></span>${meter(m[5], m[6])}` : '<span class="muted">sem votos</span>'}</span></a>`; };
  const LIM = 12, membros = s.membros.slice(0, LIM).map(mrow).join("");
  M.innerHTML = `<section class="card glass"><a class="muted small" href="#/partidos">← Partidos</a>
     <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">${selo(p, "lg")}<div style="display:grid;gap:6px;min-width:0;flex:1"><span class="kick">Partido · número ${p.n}</span><h1 style="margin:0">${esc(p.nome)}</h1><span class="fx"></span>
      ${p.fed ? `<span class="small muted">Federação: ${esc(p.fed)}</span>` : ""}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn o acbtn" id="pac" type="button" style="padding:10px 16px">☆ Acompanhar</button><a class="btn o" style="padding:10px 16px;text-decoration:none" target="_blank" rel="noopener" href="https://wa.me/?text=${encodeURIComponent(p.nome + " no Fiscaliza Brasil: " + location.origin + "/partido/" + encodeURIComponent(p.s))}">WhatsApp</a></div></div></section>
   <section class="card glass"><h2 style="margin:0">O que o partido diz defender</h2>
     <p style="margin:0;font-size:1.05rem;line-height:1.55;max-width:70ch">${esc(p.desc)}</p>
     <div class="defs">${p.def.map((d) => `<span class="chip">${esc(d)}</span>`).join("")}</div>
     <p class="src" style="margin:0">Resumo do Fiscaliza Brasil a partir do estatuto e do programa registrados pelo partido. Leia os documentos completos no <a href="${PART.fonte_estatutos}" target="_blank" rel="noopener">TSE</a>.</p></section>
   ${s.dep + s.sen ? `<section class="card glass"><h2 style="margin:0">Como a bancada vota</h2>
     <div class="pnum"><div><b>${s.dep}</b><span>Deputados federais</span></div><div><b>${s.sen}</b><span>Senadores</span></div>
      <div><b style="color:#14703C">${pctx(s.coes)}</b><span>Votos junto com o partido</span></div><div><b style="color:#B3261E">${mil(s.c)}</b><span>Votos contra o partido</span></div>
      ${s.gov != null ? `<div><b>${pctx(s.gov)}</b><span>Com o governo (Câmara)</span></div>` : ""}</div>
     ${meter(s.a, s.c)}
     <p class="src" style="margin:0">Em cada votação nominal, a posição do partido é o voto da maioria dos seus parlamentares. Verde: votou junto; vermelho: votou contra. Abstenções e ausências não entram na conta. Votações desde fevereiro de 2023, com o partido atual de cada parlamentar.</p></section>
   <section class="card glass"><h2 style="margin:0">Parlamentares do partido</h2><p class="muted small" style="margin:0">Quem mais votou contra o partido aparece primeiro.</p><div id="pmem">${membros}</div>${s.membros.length > LIM ? `<button class="btn o more" id="pmm" type="button">Ver todos os ${s.membros.length}</button>` : ""}</section>
   ${s.rec.length ? `<section class="card glass"><h2 style="margin:0">Últimas votações na Câmara</h2><div style="display:grid;gap:8px" class="vlist">${s.rec.map((r, k) => vrow(r, VCx, "C").replace('class="vrow"', k >= 5 ? 'class="vrow" hidden' : 'class="vrow"')).join("")}</div>${s.rec.length > 5 ? '<button class="btn o more" type="button" data-vm>Ver mais votações</button>' : ""}</section>` : ""}
   ${s.recS.length ? `<section class="card glass"><h2 style="margin:0">Últimas votações no Senado</h2><div style="display:grid;gap:8px" class="vlist">${s.recS.map((r, k) => vrow(r, VSx, "S").replace('class="vrow"', k >= 5 ? 'class="vrow" hidden' : 'class="vrow"')).join("")}</div>${s.recS.length > 5 ? '<button class="btn o more" type="button" data-vm>Ver mais votações</button>' : ""}</section>` : ""}`
  : `<section class="card glass"><p class="muted" style="margin:0">O ${esc(p.nome)} não tem deputados federais nem senadores em exercício, então não há votações no Congresso para mostrar.</p></section>`}
   <p class="src">Fontes: ${FONTE_CAM} · ${FONTE_SEN} · <a href="${PART.fonte_estatutos}" target="_blank" rel="noopener">TSE</a>.</p>`;
  if (window.FBAcomp) FBAcomp.botao($("#pac"), { tipo: "partido", ref: p.s, nome: p.nome });
  if ($("#pmm")) $("#pmm").onclick = () => { $("#pmem").innerHTML = s.membros.map(mrow).join(""); $("#pmm").remove(); };
  document.querySelectorAll("[data-vm]").forEach((b) => (b.onclick = () => { b.previousElementSibling.querySelectorAll(".vrow[hidden]").forEach((x) => (x.hidden = false)); b.remove(); }));
}

/* Usado na ficha do político: posição do partido em cada votação */
function posPartido(part, casa) { if (!PART) return ""; return (casa === "C" ? PART.cam : PART.sen)[part] || ""; }
