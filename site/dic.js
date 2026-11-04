/* Dicionário político: termos da política em linguagem simples, por letra e por tema, com a fonte oficial.
   Rotas: #/dicionario e #/dicionario/<id-do-termo>. Dados em data/dicionario.json. */
let DIC = null;

(function css() {
  const s = document.createElement("style");
  s.textContent = `
  .dhd{display:grid;grid-template-columns:auto minmax(0,1fr);gap:6px 18px;align-items:center}
  .dhd .n{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:clamp(3.4rem,13vw,5.6rem);line-height:.85;letter-spacing:-.04em;grid-row:span 2}
  .dhd h1{margin:0}.dhd p{margin:0;color:var(--muted);max-width:60ch}
  .dtools{display:grid;gap:12px}
  .az{display:grid;grid-template-columns:repeat(13,minmax(0,1fr));gap:4px}@media (min-width:760px){.az{grid-template-columns:repeat(26,minmax(0,1fr))}}
  .az button{width:100%;height:34px;border-radius:10px;border:1px solid rgba(11,11,12,.12);background:rgba(255,255,255,.7);font-family:var(--f-mono);font-weight:600;font-size:.82rem;padding:0}
  .az button:disabled{opacity:.3;cursor:default}.az button[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
  .dbar{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
  main{grid-template-columns:minmax(0,1fr)}.card{grid-template-columns:minmax(0,1fr)}#dbox{min-width:0}
  .dcols{display:grid;grid-auto-flow:column;grid-auto-columns:78%;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:thin;padding:2px 2px 12px}
  @media (min-width:600px){.dcols{grid-auto-columns:calc((100% - 14px)/2)}}@media (min-width:900px){.dcols{grid-auto-columns:calc((100% - 42px)/4)}}
  .dcol{scroll-snap-align:start;display:grid;align-content:start;gap:0;min-width:0}
  .dcard{position:relative;aspect-ratio:1/1;max-height:220px;border-radius:20px;display:flex;align-items:flex-end;padding:14px 16px;overflow:hidden;margin-bottom:10px;border:1.5px solid var(--ink)}
  .dcard b{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:clamp(6rem,14vw,9rem);line-height:.78;letter-spacing:-.04em}
  .dcard small{position:absolute;top:12px;right:14px;font-family:var(--f-mono);font-weight:600;font-size:.8rem}
  .dcard.k{background:var(--ink);color:#fff}.dcard.w{background:rgba(255,255,255,.85);color:var(--ink)}
  .dcard.v{background:var(--verde);color:#fff;border-color:var(--verde)}.dcard.a{background:var(--amarelo);color:var(--ink);border-color:var(--amarelo)}.dcard.z{background:var(--azul);color:#fff;border-color:var(--azul)}
  .dt{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 8px;padding:9px 2px;border-top:1px solid rgba(11,11,12,.09);text-decoration:none;color:inherit}
  .dt:hover b{text-decoration:underline}
  .dt b{font-family:var(--f-display);font-weight:700;font-size:.95rem;line-height:1.25;overflow-wrap:anywhere}
  .dt small{grid-column:1;color:var(--muted);font-size:.76rem}
  .dt i{grid-row:1;grid-column:2;font-style:normal;font-family:var(--f-mono);font-weight:600;font-size:.68rem;color:var(--muted);align-self:center}
  .dres{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:0 18px}
  .dnav{display:flex;gap:8px}.dnav button{width:40px;height:40px;border-radius:50%;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.75);font-size:1.1rem}
  .dterm{display:grid;grid-template-columns:auto minmax(0,1fr);gap:18px;align-items:start}
  .dterm .dcard{width:120px;margin:0}.dterm .dcard b{font-size:6rem}
  @media (max-width:560px){.dterm{grid-template-columns:1fr}.dterm .dcard{width:96px}.dterm .dcard b{font-size:4.6rem}}
  .ddef{font-size:1.15rem;line-height:1.55;margin:0;text-wrap:pretty;max-width:62ch}
  .chip{display:inline-flex;align-items:center;gap:6px;font-family:var(--f-mono);font-size:.7rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:5px 11px;border-radius:999px;background:rgba(11,11,12,.07);color:var(--ink);text-decoration:none;border:0}
  .chip.sg{background:var(--ink);color:#fff}`;
  document.head.append(s);
})();

const dFold = (x) => String(x || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const dCurto = (d) => { const f = d.split(". ")[0]; if (f.length <= 100) return f.replace(/\.$/, "") + "."; return f.slice(0, 100).replace(/[\s,;:]+\S*$/, "") + "…"; };
const CORES = ["k", "w", "v", "w", "a", "w", "z", "w"];

async function dicionario(id) {
  setNav("mais");
  DIC = DIC || await getJSON("data/dicionario.json");
  const T = DIC.temas, I = DIC.itens;
  if (id && !id.startsWith("tema-")) return termo(id);
  document.title = "Dicionário político · Fiscaliza Brasil";
  let tema = id && T[id.slice(5)] ? id.slice(5) : null, q = "";
  const letras = [...new Set(I.map((x) => x.l))];
  M.innerHTML = `<section class="card glass"><div class="dhd"><span class="n">${I.length}</span><div><span class="kick">Dicionário</span><h1>Dicionário político</h1></div>
      <p>Os termos da política explicados em palavras simples: o que é uma PEC, uma votação simbólica, uma emenda parlamentar, o quociente eleitoral. Cada termo tem a fonte oficial, para conferir.</p></div>
     <div class="dtools"><label class="search">${typeof ICON_S !== "undefined" ? ICON_S : ""}<input id="dq" type="search" placeholder="Procure: PEC, simbólica, emenda Pix…" autocomplete="off" aria-label="Procurar no dicionário"></label>
      <div class="yrs" id="dtm"></div>
      <div class="az" id="daz"></div></div></section>
   <section class="card glass"><div class="dbar"><span class="muted small" id="dct"></span><div style="display:flex;gap:8px;align-items:center"><button class="btn o" id="dsg" style="padding:9px 16px">+ Sugerir uma palavra</button><div class="dnav" id="dnv"><button id="dpv" aria-label="Letras anteriores">‹</button><button id="dnx" aria-label="Próximas letras">›</button></div></div></div>
     <div id="dbox"></div></section>
   <p class="src">Textos do Fiscaliza Brasil, escritos a partir de: ${Object.values(Object.fromEntries(Object.values(DIC.fontes).map((f) => [f[1], f]))).map((f) => `<a href="${f[1]}" target="_blank" rel="noopener">${esc(f[0])}</a>`).join(" · ")}.</p>`;
  const linha = (x) => `<a class="dt" href="#/dicionario/${x.id}"><b>${esc(x.t)}</b>${x.s ? `<i>${esc(x.s)}</i>` : ""}<small>${esc(T[x.c])}</small></a>`;
  const filtrados = () => I.filter((x) => (!tema || x.c === tema) && (!q || dFold(x.t + " " + x.s + " " + x.d).includes(q)));
  const draw = () => {
    $("#dtm").innerHTML = [["", "Todos os temas"], ...Object.entries(T)].map(([k, n]) => `<button data-k="${k}" aria-pressed="${(tema || "") === k}">${esc(n)}</button>`).join("");
    $("#dtm").querySelectorAll("button").forEach((b) => (b.onclick = () => { tema = b.dataset.k || null; draw(); }));
    const f = filtrados(); const tem = new Set(f.map((x) => x.l));
    $("#daz").innerHTML = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map((l) => `<button data-l="${l}" ${tem.has(l) ? "" : "disabled"}>${l}</button>`).join("");
    $("#dct").textContent = f.length === I.length ? `${I.length} termos` : `${f.length} de ${I.length} termos`;
    const box = $("#dbox");
    if (q) { // busca: lista simples, os mais parecidos primeiro
      const nome = (x) => dFold(x.t + " " + x.s).includes(q);
      f.sort((a, b) => nome(b) - nome(a));
      box.innerHTML = f.length ? `<div class="dres">${f.map(linha).join("")}</div>` : `<p class="muted">Nenhum termo encontrado. Quer sugerir essa palavra? Use o botão "Sugerir uma palavra".</p>`;
      $("#dnv").hidden = true;
    } else {
      const ls = letras.filter((l) => tem.has(l));
      box.innerHTML = `<div class="dcols" id="dcols">${ls.map((l, k) => { const xs = f.filter((x) => x.l === l); return `<div class="dcol" id="dl-${l}"><div class="dcard ${CORES[letras.indexOf(l) % CORES.length]}"><small>${String(xs.length).padStart(2, "0")}</small><b>${l}</b></div>${xs.map(linha).join("")}</div>`; }).join("")}</div>`;
      $("#dnv").hidden = false;
    }
    $("#daz").querySelectorAll("button:not([disabled])").forEach((b) => (b.onclick = () => {
      $("#daz").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b));
      if (q) { q = ""; $("#dq").value = ""; draw(); }
      const col = $("#dl-" + b.dataset.l), c = $("#dcols"); if (col && c) c.scrollTo({ left: c.scrollLeft + col.getBoundingClientRect().left - c.getBoundingClientRect().left - 2, behavior: "smooth" });
      $("#dbox").scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
    }));
  };
  draw();
  let tm; $("#dq").addEventListener("input", (e) => { clearTimeout(tm); tm = setTimeout(() => { q = dFold(e.target.value.trim()); draw(); }, 120); });
  const passo = (d) => { const c = $("#dcols"); if (c) c.scrollBy({ left: d * c.clientWidth, behavior: "smooth" }); };
  $("#dpv").onclick = () => passo(-1); $("#dnx").onclick = () => passo(1);
  $("#dsg").onclick = () => sugerirPalavra($("#dq").value.trim());
}

function termo(id) {
  const T = DIC.temas, I = DIC.itens; const x = I.find((y) => y.id === id);
  if (!x) { M.innerHTML = `<section class="card glass"><a class="muted small" href="#/dicionario">← Dicionário</a><h1>Termo não encontrado</h1></section>`; return; }
  const k = I.indexOf(x), ant = I[k - 1], prox = I[k + 1];
  const rel = I.filter((y) => y.c === x.c && y.id !== x.id); const mesmos = rel.slice(Math.max(0, rel.findIndex((y) => y.t > x.t) - 3)).slice(0, 6);
  const f = DIC.fontes[x.c]; const letras = [...new Set(I.map((y) => y.l))];
  document.title = `${x.t} · Dicionário político · Fiscaliza Brasil`;
  M.innerHTML = `<section class="card glass"><a class="muted small" href="#/dicionario">← Dicionário político</a>
     <div class="dterm"><div class="dcard ${CORES[letras.indexOf(x.l) % CORES.length]}"><b>${x.l}</b></div>
      <div style="display:grid;gap:12px;min-width:0"><div style="display:flex;gap:6px;flex-wrap:wrap"><a class="chip" href="#/dicionario/tema-${x.c}">${esc(T[x.c])}</a>${x.s ? `<span class="chip sg">${esc(x.s)}</span>` : ""}</div>
       <h1 style="margin:0">${esc(x.t)}</h1><span class="fx"></span>
       <p class="ddef">${esc(x.d)}</p>
       <p class="src" style="margin:0">Fonte para conferir: <a href="${f[1]}" target="_blank" rel="noopener">${esc(f[0])}</a></p>
       <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn o" id="dcp" style="padding:9px 16px">Copiar link</button><button class="btn o" id="drp" style="padding:9px 16px">Reportar erro</button></div></div></div></section>
   ${mesmos.length ? `<section class="card glass"><h2 style="margin:0">Mais sobre ${esc(T[x.c].toLowerCase())}</h2><div class="dres">${mesmos.map((y) => `<a class="dt" href="#/dicionario/${y.id}"><b>${esc(y.t)}</b>${y.s ? `<i>${esc(y.s)}</i>` : ""}<small>${esc(dCurto(y.d))}</small></a>`).join("")}</div></section>` : ""}
   <div class="dbar">${ant ? `<a class="btn o" style="text-decoration:none;padding:9px 16px" href="#/dicionario/${ant.id}">‹ ${esc(ant.t)}</a>` : "<span></span>"}${prox ? `<a class="btn o" style="text-decoration:none;padding:9px 16px" href="#/dicionario/${prox.id}">${esc(prox.t)} ›</a>` : ""}</div>`;
  $("#dcp").onclick = async () => { const u = location.href; try { await navigator.clipboard.writeText(u); $("#dcp").textContent = "Link copiado"; } catch (e) { prompt("Copie o link:", u); } };
  $("#drp").onclick = () => (typeof reportar === "function" ? reportar("Dicionário: " + x.t) : null);
}

function sugerirPalavra(pre) {
  let d = document.getElementById("sugdlg");
  if (!d) { d = document.createElement("dialog"); d.id = "sugdlg"; d.className = "rep"; document.body.appendChild(d); }
  d.innerHTML = `<form method="dialog" class="glass"><h2>Sugerir uma palavra</h2><p class="muted small" style="margin:0">Que termo da política você quer ver explicado aqui?</p>
    <input id="sw" type="text" required maxlength="120" placeholder="Ex.: Fundo eleitoral" value="${esc(pre || "")}"><textarea id="sx" rows="3" placeholder="Onde você viu esse termo? (opcional)"></textarea>
    <div class="err small" id="se" style="color:var(--verm);min-height:18px"></div>
    <div class="btns"><button class="btn" id="ss" value="send">Enviar</button><button class="btn o" value="cancel" formnovalidate>Cancelar</button></div></form>`;
  d.showModal();
  d.querySelector("#ss").onclick = async (e) => {
    e.preventDefault(); const w = d.querySelector("#sw").value.trim(); if (w.length < 2) { d.querySelector("#se").textContent = "Escreva a palavra."; return; }
    const b = d.querySelector("#ss"); b.disabled = true;
    try {
      const sb = sbClient(); if (!sb) throw new Error("Envio indisponível no momento.");
      const r = await sb.from("reportes").insert({ pagina: location.href.slice(0, 300), sobre: "Sugestão para o dicionário", texto: (w + (d.querySelector("#sx").value.trim() ? " — " + d.querySelector("#sx").value.trim() : "")).slice(0, 2000) });
      if (r.error) throw r.error;
      d.close(); if (typeof toast2 === "function") toast2("Obrigado! A sugestão foi enviada.");
    } catch (err) { d.querySelector("#se").textContent = "Não foi possível enviar: " + (err.message || err); b.disabled = false; }
  };
}
