/* Ferramentas: OUVIR (leitura em voz alta), INSTALAR O APP, COMPARAR (2 a 4 parlamentares) e CARD PARA STORIES (imagem 1080x1920 para baixar). */
(function css() {
  const s = document.createElement("style");
  s.textContent = `
  .top .ouvir{min-width:38px;justify-content:center}
  .cmpbar{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(84px + env(safe-area-inset-bottom,0px));z-index:29;display:flex;gap:10px;align-items:center;padding:8px 8px 8px 16px;border-radius:999px;background:var(--ink);color:#fff;box-shadow:0 10px 30px rgba(0,0,0,.25);font-weight:700;font-size:.85rem}
  .cmpbar a{background:#fff;color:var(--ink);border-radius:999px;padding:8px 14px;text-decoration:none}.cmpbar button{background:none;border:0;color:#fff;opacity:.7;font-size:1rem}
  .cmpt{width:100%;border-collapse:separate;border-spacing:0;font-size:.9rem}
  .cmpt th,.cmpt td{padding:10px 12px;border-bottom:1px solid rgba(11,11,12,.08);text-align:left;vertical-align:top}
  .cmpt thead th{vertical-align:bottom}.cmpt tbody th{font-family:var(--f-display);font-weight:700;font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
  .cmpt td b{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:1.15rem}
  .cmpw{overflow-x:auto;margin:0 -4px}.cmph{display:grid;gap:6px;justify-items:start;min-width:130px}.cmph a{font-family:var(--f-display);font-weight:700;color:inherit;text-decoration:none}
  .storyw{display:grid;gap:12px;justify-items:center}.storyw canvas{width:min(100%,360px);height:auto;border-radius:22px;box-shadow:0 20px 50px rgba(15,20,30,.18)}`;
  document.head.append(s);
})();

/* ---------- OUVIR ---------- */
const FBOuvir = (() => {
  let falando = false;
  const parar = () => { try { speechSynthesis.cancel(); } catch (e) {} falando = false; marca(); };
  const marca = () => document.querySelectorAll(".ouvir").forEach((b) => { b.setAttribute("aria-pressed", falando); b.title = falando ? "Parar a leitura" : "Ouvir esta página"; b.innerHTML = falando ? '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/></svg><span class="acl-t"> Parar</span>' : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg><span class="acl-t"> Ouvir</span>'; });
  const texto = () => { const m = document.getElementById("main"); if (!m) return ""; const c = m.cloneNode(true); c.querySelectorAll("script,style,svg,button,select,input,textarea,.src").forEach((e) => e.remove()); return c.innerText.replace(/\s+\n/g, "\n").replace(/[·•→←]/g, " ").trim(); };
  const falar = () => {
    if (!("speechSynthesis" in window)) { alert("Este navegador não tem leitura em voz alta."); return; }
    if (falando) return parar();
    const partes = texto().split(/(?<=[.!?\n])\s+/).filter((x) => x.trim()).reduce((a, x) => { if (a.length && (a[a.length - 1] + " " + x).length < 220) a[a.length - 1] += " " + x; else a.push(x); return a; }, []);
    const voz = speechSynthesis.getVoices().find((v) => /pt[-_]BR/i.test(v.lang)) || speechSynthesis.getVoices().find((v) => /^pt/i.test(v.lang));
    falando = true; marca();
    partes.forEach((t, i) => { const u = new SpeechSynthesisUtterance(t); u.lang = "pt-BR"; if (voz) u.voice = voz; u.rate = 1.02; if (i === partes.length - 1) u.onend = () => { falando = false; marca(); }; speechSynthesis.speak(u); });
  };
  addEventListener("hashchange", parar);
  return { falar, parar, marca };
})();

/* ---------- INSTALAR O APP ---------- */
let FB_PROMPT = null;
addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); FB_PROMPT = e; });
async function instalarApp() {
  if (FB_PROMPT) { FB_PROMPT.prompt(); await FB_PROMPT.userChoice.catch(() => null); FB_PROMPT = null; return; }
  const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const d = document.createElement("dialog"); d.className = "rep";
  d.innerHTML = `<form method="dialog" class="glass"><h2>Instalar o Fiscaliza Brasil</h2>
    ${matchMedia("(display-mode: standalone)").matches ? "<p>O aplicativo já está instalado neste aparelho.</p>" : ios
      ? "<ol style=\"margin:0;padding-left:20px;display:grid;gap:8px;line-height:1.5\"><li>Abra este site no <b>Safari</b>.</li><li>Toque no botão <b>Compartilhar</b> (o quadrado com a seta para cima).</li><li>Escolha <b>Adicionar à Tela de Início</b> e toque em <b>Adicionar</b>.</li></ol>"
      : "<ol style=\"margin:0;padding-left:20px;display:grid;gap:8px;line-height:1.5\"><li>Abra o menu do navegador (os três pontinhos).</li><li>Toque em <b>Instalar aplicativo</b> ou <b>Adicionar à tela inicial</b>.</li></ol>"}
    <p class="muted small" style="margin:0">O ícone da lupa-bandeira aparece na tela do celular e o site abre como um aplicativo, sem passar por loja.</p>
    <div class="btns"><button class="btn" value="ok">Entendi</button></div></form>`;
  document.body.append(d); d.addEventListener("close", () => d.remove()); d.showModal();
}

/* ---------- COMPARAR ---------- */
const FBCmp = (() => {
  const K = "fb_cmp";
  const ler = () => { try { return JSON.parse(localStorage.getItem(K) || "[]"); } catch (e) { return []; } };
  const gravar = (l) => { try { localStorage.setItem(K, JSON.stringify(l)); } catch (e) {} barra(); };
  const tem = (ref) => ler().some((x) => x.ref === ref);
  function alternar(it) { let l = ler(); if (tem(it.ref)) l = l.filter((x) => x.ref !== it.ref); else { if (l.length >= 4) { alert("Dá para comparar até 4 de cada vez. Tire alguém da comparação primeiro."); return; } l.push(it); } gravar(l); }
  function botao(el, it) { if (!el) return; const pinta = () => { const on = tem(it.ref); el.setAttribute("aria-pressed", on); el.textContent = on ? "✓ Na comparação" : "+ Comparar"; }; pinta(); el.classList.add("acbtn"); el.onclick = () => { alternar(it); pinta(); }; }
  function barra() {
    let b = document.getElementById("cmpbar"); const l = ler();
    if (!l.length || location.hash.startsWith("#/comparar")) { if (b) b.remove(); return; }
    if (!b) { b = document.createElement("div"); b.id = "cmpbar"; b.className = "cmpbar"; document.body.append(b); }
    b.innerHTML = `<span>${l.length} na comparação${l.length < 2 ? " · escolha mais um" : ""}</span>${l.length >= 2 ? '<a href="#/comparar">Comparar</a>' : ""}<button type="button" aria-label="Limpar comparação">✕</button>`;
    b.querySelector("button").onclick = () => gravar([]);
  }
  addEventListener("hashchange", barra); addEventListener("load", barra);
  async function pagina() {
    setNav("mais"); document.title = "Comparar · Fiscaliza Brasil"; barra();
    const l = ler();
    if (l.length < 2) { M.innerHTML = `<section class="card glass"><span class="kick">Comparar</span><h1>Compare políticos lado a lado</h1><span class="fx"></span><p class="muted" style="margin:0">Abra a ficha de um deputado federal ou senador e toque em <b>+ Comparar</b>. Escolha de 2 a 4.</p><div class="btns"><a class="btn o" href="#/quem">Buscar políticos</a></div></section>`; return; }
    M.innerHTML = `<section class="card glass"><span class="kick">Comparar</span><h1>Lado a lado</h1><span class="fx"></span><p class="muted small" style="margin:0">Carregando…</p></section>`;
    await loadPart().catch(() => null); const VC = await loadVC(), VS = await loadVS();
    const cols = await Promise.all(l.map(async (it) => {
      const X = it.casa === "C" ? (await loadC(it.uf))[it.id] : (await loadS(it.uf))[it.id]; const VL = it.casa === "C" ? VC : VS; const v = (X && X.v) || "";
      const pos = posPartido(it.part, it.casa); let a = 0, c = 0, ga = 0, gt = 0; const fp = X && X.fp;
      for (let i = 0; i < v.length; i++) { const x = v[i]; if (x !== "S" && x !== "N") continue; if (fp) { if (fp[i] === "g") a++; else if (fp[i] === "r") c++; } else { const p = pos[i]; if (p === "S" || p === "N") { if (x === p) a++; else c++; } }
        if (it.casa === "C") { const g = (VL[i][8] || "")[0]; if (g === "S" || g === "N") { gt++; if (g === x) ga++; } } }
      const au = (X && X.au && X.au.c) || {}; const nprop = ["PL", "PLP", "PEC", "PDL", "PRS"].reduce((s, t) => s + (au[t] || 0), 0);
      const cota = X && X.cota ? Object.values(X.cota.a).reduce((s, t) => s + Object.values(t).reduce((x, y) => x + y, 0), 0) : null;
      const pt = X && X.pat && X.pat.length ? X.pat[X.pat.length - 1] : null;
      return { it, X, a, c, ga, gt, nprop, cota, pt };
    }));
    const pc = (x, y) => (y ? Math.round((100 * x) / y) + "%" : "—");
    const L = [
      ["Cargo", (k) => esc(k.it.cargo || "")],
      ["Partido · UF", (k) => esc((k.it.part || "") + " · " + (k.it.uf || ""))],
      ["Presença nas sessões", (k) => k.X && k.X.sess ? `<b>${pc(k.X.sess[0], k.X.sess[1])}</b>` : "—"],
      ["Participação nas votações", (k) => k.X && k.X.pres ? `<b>${pc(k.X.pres[0], k.X.pres[1])}</b>` : "—"],
      ["Votou com o partido", (k) => k.a + k.c ? `<b style="color:#14703C">${pc(k.a, k.a + k.c)}</b>${meter(k.a, k.c)}` : "—"],
      ["Votos contra o partido", (k) => `<b style="color:#B3261E">${mil(k.c)}</b>`],
      ["Votou com o governo", (k) => k.gt ? `<b>${pc(k.ga, k.gt)}</b>` : "—"],
      ["Projetos apresentados", (k) => `<b>${mil(k.nprop)}</b>`],
      ["Cota parlamentar gasta", (k) => k.cota != null ? `<b>${brl(k.cota)}</b>` : "—"],
      ["Discursos", (k) => k.X && k.X.disc ? `<b>${mil(k.X.disc.n)}</b>` : "—"],
      ["Patrimônio declarado", (k) => k.pt ? `<b>${brl(k.pt[6])}</b><br><small class="muted">em ${k.pt[0]}</small>` : "—"],
    ];
    M.innerHTML = `<section class="card glass"><span class="kick">Comparar</span><h1>Lado a lado</h1><span class="fx"></span>
       <div class="cmpw"><table class="cmpt"><thead><tr><th></th>${cols.map((k) => `<th><div class="cmph">${av(k.it.nome, k.it.foto)}<a href="#/p/${esc(k.it.ref)}">${esc(k.it.nome)}</a><button class="btn o" style="padding:5px 10px;font-size:.75rem" data-x="${esc(k.it.ref)}" type="button">Tirar</button></div></th>`).join("")}</tr></thead>
       <tbody>${L.map(([n, f]) => `<tr><th scope="row">${n}</th>${cols.map((k) => `<td>${f(k)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>
       <p class="src" style="margin:0">Desde fevereiro de 2023. Presença e votações do Plenário; projetos como autor ou coautor; cota com os reembolsos de 2023 a 2026; patrimônio declarado ao TSE. Veja <a href="#/metodologia">Como calculamos</a>. Fontes: ${FONTE_CAM} · ${FONTE_SEN} · ${FONTE_TSE}.</p></section>`;
    document.querySelectorAll("[data-x]").forEach((b) => (b.onclick = () => { gravar(ler().filter((x) => x.ref !== b.dataset.x)); pagina(); }));
  }
  return { botao, alternar, ler, pagina, barra };
})();
window.FBCmp = FBCmp; window.FBOuvir = FBOuvir;
window.comparar = FBCmp.pagina;

/* ---------- CARD PARA STORIES (canvas 1080x1920) ---------- */
async function cardStories(el, o, stats, nota) {
  const W = 1080, H = 1920, cv = document.createElement("canvas"); cv.width = W; cv.height = H; const g = cv.getContext("2d");
  try { await Promise.all(["800 80px 'Bricolage Grotesque'", "700 40px 'Familjen Grotesk'", "600 30px 'JetBrains Mono'"].map((f) => document.fonts.load(f))); } catch (e) {}
  const F = (w, s, fam) => `${w} ${s}px ${fam === "m" ? "'JetBrains Mono',monospace" : fam === "d" ? "'Familjen Grotesk',sans-serif" : "'Bricolage Grotesque','Familjen Grotesk',sans-serif"}`;
  const img = (src, semCors) => new Promise((ok) => { if (!src) return ok(null); const i = new Image(); if (!semCors) i.crossOrigin = "anonymous"; i.onload = () => ok(i); i.onerror = () => ok(null); i.src = src; });
  const rr = (x, y, w, h, r) => { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); };
  // fundo claro com o brilho das cores do Brasil
  g.fillStyle = "#FBFBF7"; g.fillRect(0, 0, W, H);
  [[0, 0, "rgba(0,156,59,.24)"], [W, 560, "rgba(255,214,0,.32)"], [300, H, "rgba(30,100,235,.22)"]].forEach(([x, y, c]) => { const gr = g.createRadialGradient(x, y, 0, x, y, 1000); gr.addColorStop(0, c); gr.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, W, H); });
  // marca
  const logo = await img("/icon-192.png"); if (logo) { g.save(); rr(80, 96, 76, 76, 20); g.clip(); g.drawImage(logo, 80, 96, 76, 76); g.restore(); }
  g.fillStyle = "#0B0B0C"; g.font = F(800, 46); g.textBaseline = "middle"; g.fillText("FISCALIZA BRASIL", 176, 136);
  // foto
  // foto: pelo nosso servidor; se falhar, pelo wsrv.nl (envia permissão para desenhar e baixar a imagem)
  let foto = null;
  if (o.foto) for (const src of [typeof fimg === "function" ? fimg(o.foto) : "", "https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?container=focus&refresh=2592000&url=" + encodeURIComponent(o.foto), "https://wsrv.nl/?url=" + encodeURIComponent(o.foto) + "&w=600&h=600&fit=cover&a=top&n=-1"]) { if (!src || src === o.foto) continue; foto = await img(src); if (foto) break; }
  // último recurso: a foto direto do site oficial. Aparece no card, mas o navegador não deixa baixar a imagem; aí a pessoa tira print
  let soPrint = false;
  if (o.foto && !foto) { foto = await img(o.foto, true); soPrint = !!foto; }
  const px = 80, py = 250, ps = 360;
  g.save(); g.shadowColor = "rgba(15,20,30,.25)"; g.shadowBlur = 50; g.shadowOffsetY = 18; rr(px, py, ps, ps, 64); g.fillStyle = "#fff"; g.fill(); g.restore();
  g.save(); rr(px + 12, py + 12, ps - 24, ps - 24, 54); g.clip();
  if (foto) { const r = Math.max((ps - 24) / foto.width, (ps - 24) / foto.height), w = foto.width * r, h = foto.height * r; g.drawImage(foto, px + 12 + (ps - 24 - w) / 2, py + 12, w, h); }
  else { g.fillStyle = "#0B0B0C"; g.fillRect(px, py, ps, ps); g.fillStyle = "#fff"; g.font = F(800, 130); g.textAlign = "center"; g.fillText(ini(o.nome), px + ps / 2, py + ps / 2 + 6); g.textAlign = "left"; }
  g.restore();
  if (o.part) { g.font = F(600, 32, "m"); const tw = g.measureText(o.part).width; rr(px + ps + 30, py + ps - 70, tw + 44, 64, 32); g.fillStyle = "#0B0B0C"; g.fill(); g.fillStyle = "#fff"; g.fillText(o.part, px + ps + 52, py + ps - 37); }
  // cargo e nome
  let y = py + ps + 100; g.fillStyle = "#5E6066"; g.font = F(600, 30, "m"); g.fillText((o.cargo + (o.uf ? " · " + o.uf : "")).toUpperCase().split("").join(String.fromCharCode(8202)), 80, y);
  y += 40; g.fillStyle = "#0B0B0C"; g.textBaseline = "top"; let fs = 118; g.font = F(800, fs);
  const linhas = (t, max) => { const ws = t.toUpperCase().split(" "); const L = []; let cur = ""; ws.forEach((w) => { const n = cur ? cur + " " + w : w; if (g.measureText(n).width > max && cur) { L.push(cur); cur = w; } else cur = n; }); if (cur) L.push(cur); return L; };
  let nl = linhas(o.nome, W - 160); while (nl.length > 2 && fs > 70) { fs -= 8; g.font = F(800, fs); nl = linhas(o.nome, W - 160); }
  nl.slice(0, 3).forEach((l) => { g.fillText(l, 80, y); y += fs * 0.92; });
  y += 22; [["#0E8A4B", 0], ["#F7C21B", 1], ["#1F4FBF", 2]].forEach(([c, i]) => { g.fillStyle = c; g.fillRect(80 + i * 48, y, 48, 10); });
  // números
  y += 60; const cw = (W - 160 - 24) / 2, ch = 220;
  stats.slice(0, 4).forEach(([n, l, cor], i) => { const x = 80 + (i % 2) * (cw + 24), yy = y + Math.floor(i / 2) * (ch + 24);
    g.save(); g.shadowColor = "rgba(15,20,30,.08)"; g.shadowBlur = 30; g.shadowOffsetY = 8; rr(x, yy, cw, ch, 36); g.fillStyle = "rgba(255,255,255,.72)"; g.fill(); g.restore();
    g.strokeStyle = "rgba(255,255,255,.95)"; g.lineWidth = 2; rr(x, yy, cw, ch, 36); g.stroke();
    g.fillStyle = cor || "#0B0B0C"; let nf = 92; g.font = F(800, nf); while (g.measureText(String(n)).width > cw - 72 && nf > 48) { nf -= 4; g.font = F(800, nf); } g.fillText(String(n), x + 36, yy + 30 + (92 - nf) * 0.6);
    g.fillStyle = "#5E6066"; g.font = F(700, 28, "d"); const ll = linhas(l, cw - 72); ll.slice(0, 2).forEach((t, j) => g.fillText(t, x + 36, yy + 140 + j * 34)); });
  y += 2 * (ch + 24);
  if (nota) { g.font = F(700, 32, "d"); const nl2 = (() => { const ws = nota.split(" "); const L = []; let cur = ""; ws.forEach((w) => { const n = cur ? cur + " " + w : w; if (g.measureText(n).width > W - 232 && cur) { L.push(cur); cur = w; } else cur = n; }); if (cur) L.push(cur); return L; })().slice(0, 3);
    const hh = 60 + nl2.length * 44; rr(80, y, W - 160, hh, 36); g.fillStyle = "#0B0B0C"; g.fill(); g.fillStyle = "#fff"; nl2.forEach((t, j) => g.fillText(t, 116, y + 32 + j * 44)); }
  // rodapé
  g.fillStyle = "rgba(11,11,12,.15)"; g.fillRect(80, H - 250, W - 160, 2);
  g.textAlign = "center"; g.fillStyle = "#0B0B0C"; g.font = F(800, 60); g.fillText("SIGA: @oabraaonery", W / 2, H - 200);
  g.fillStyle = "#5E6066"; g.font = F(600, 28, "m"); g.fillText("VAMOS FISCALIZAR TUDO · fiscalizaja.com.br", W / 2, H - 112); g.textAlign = "left";
  const nome = "fiscaliza-" + (o.nome || "card").toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, "-") + ".png";
  el.innerHTML = `<div class="storyw"></div><div class="btns" style="justify-content:center"><button class="btn" id="stdl" type="button">Baixar imagem</button><button class="btn o" id="stsh" type="button" hidden>Compartilhar</button></div><p class="muted small" style="margin:0;text-align:center">Imagem em 1080 × 1920, no tamanho dos Stories.</p>`;
  el.querySelector(".storyw").append(cv);
  let blob = null; if (!soPrint) try { blob = await new Promise((ok) => cv.toBlob(ok, "image/png")); } catch (e) {}
  if (!blob && $("#stsh")) $("#stsh").remove();
  if (!blob) { $("#stdl").textContent = "Como salvar"; el.querySelector("p.muted").innerHTML = "O site oficial não liberou a foto para download. <b>Tire um print desta imagem</b> e recorte no celular: ela já está no formato dos Stories."; }
  $("#stdl").onclick = () => { if (!blob) { alert("Tire um print da imagem acima e recorte no celular. O site oficial não permitiu baixar a foto direto, mas o card já está no tamanho dos Stories."); return; } const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = nome; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); };
  if (blob && navigator.canShare && navigator.canShare({ files: [new File([blob], nome, { type: "image/png" })] })) { $("#stsh").hidden = false; $("#stsh").onclick = () => navigator.share({ files: [new File([blob], nome, { type: "image/png" })], title: o.nome }).catch(() => {}); }
}

/* ---------- MINIMIZAR CAIXAS: botão − no canto de cada caixa com título; + volta como estava ---------- */
(function () {
  const css = document.createElement("style");
  css.textContent = `#main .card.cl{position:relative}
  #main .minb{position:absolute;top:var(--mt,20px);right:var(--mr,35px);height:var(--mh,30px);min-width:22px;padding:0;margin:0;border:0;background:none;box-shadow:none;border-radius:0;color:var(--ink);font:700 1.45rem/1 var(--f-display);display:flex;align-items:center;justify-content:flex-end;z-index:3;cursor:pointer;opacity:.85}
  #main .minb:hover{opacity:1}#main .minb:focus-visible{outline:2px solid var(--ink);outline-offset:4px;border-radius:6px}
  #main .card.cl > .khd{padding-right:46px}
  #main .card.min > :not(.khd):not(.minb){display:none!important}
  #main .card.min{gap:0}`;
  document.head.append(css);
  const estado = new Map();
  const chave = (c, h) => (location.hash || "#/").split("/").slice(0, 3).join("/") + "|" + h.textContent.trim().slice(0, 60);
  function prepara() {
    const M = document.getElementById("main"); if (!M) return;
    M.querySelectorAll(".card").forEach((c) => {
      if (c.dataset.clp) return; c.dataset.clp = "1";
      if (c.querySelector(":scope > h1, :scope > div > h1")) return; // caixa de abertura da página
      const h = c.querySelector("h2"); if (!h) return;
      let kid = h; while (kid.parentElement && kid.parentElement !== c) kid = kid.parentElement;
      if (kid.parentElement !== c || c.children.length < 2) return;
      kid.classList.add("khd"); c.classList.add("cl");
      const b = document.createElement("button"); b.type = "button"; b.className = "minb";
      const k = chave(c, h);
      const pinta = () => { const min = c.classList.contains("min"); b.textContent = min ? "+" : "−"; b.setAttribute("aria-label", (min ? "Mostrar " : "Minimizar ") + h.textContent.trim()); b.setAttribute("aria-expanded", !min); };
      if (estado.get(k)) c.classList.add("min");
      b.onclick = () => { c.classList.toggle("min"); estado.set(k, c.classList.contains("min")); pinta(); if (c.classList.contains("min") && c.getBoundingClientRect().top < 70) c.scrollIntoView({ block: "start", behavior: "smooth" }); };
      pinta(); c.append(b);
      requestAnimationFrame(() => { try {
        const cr = c.getBoundingClientRect(), hr = h.getBoundingClientRect();
        c.style.setProperty("--mt", Math.round(hr.top - cr.top) + "px"); c.style.setProperty("--mh", Math.round(hr.height) + "px");
        const seta = [...c.querySelectorAll(".lead > span:last-child, .go .seta, .menu a > span:last-child, .res a > small")].find((e) => e.offsetParent);
        const cs = getComputedStyle(c); let dir = parseFloat(cs.paddingRight) || 20;
        if (seta) dir = Math.round(cr.right - seta.getBoundingClientRect().right);
        c.style.setProperty("--mr", dir + "px");
      } catch (e) {} });
    });
  }
  const iniciar = () => { const M = document.getElementById("main"); if (!M) return; prepara(); new MutationObserver(() => prepara()).observe(M, { childList: true, subtree: true }); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar); else iniciar();
})();
