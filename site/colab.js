/* COLABORE: doação por Pix (chave e QR editados no painel) e envio de ideias, sugestões e correções.
   Rota: #/colabore. O Pix fica em site_config (chave "pix", valor em JSON). As mensagens vão para a tabela reportes. */
(function css() {
  const s = document.createElement("style");
  s.textContent = `
  .cb-hero{display:grid;gap:12px}
  .cb-pix{display:grid;grid-template-columns:auto minmax(0,1fr);gap:18px;align-items:center}
  @media (max-width:560px){.cb-pix{grid-template-columns:1fr;justify-items:center;text-align:center}}
  .cb-qr{width:180px;height:180px;border-radius:20px;background:#fff;border:1px solid rgba(11,11,12,.1);box-shadow:0 10px 30px rgba(15,20,30,.10);display:grid;place-items:center;overflow:hidden;padding:10px}
  .cb-qr img{width:100%;height:100%;object-fit:contain}
  .cb-key{display:grid;gap:4px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.8);border:1px solid rgba(11,11,12,.1);text-align:left}
  .cb-key code{font-family:var(--f-mono);font-size:.92rem;font-weight:600;overflow-wrap:anywhere}
  .cb-key small{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
  .cb-btns{display:flex;gap:8px;flex-wrap:wrap}
  .cb-list{display:grid;gap:10px;margin:0;padding:0;list-style:none}
  .cb-list li{display:grid;grid-template-columns:28px minmax(0,1fr);gap:10px;align-items:start}
  .cb-list li i{width:28px;height:28px;border-radius:9px;background:var(--ink);color:#fff;display:grid;place-items:center;font-style:normal;font-size:.8rem;font-weight:700}
  .cb-list b{font-family:var(--f-display)}.cb-list span{color:var(--muted);font-size:.92rem;line-height:1.4}
  .cb-form{display:grid;gap:10px}
  .cb-form textarea,.cb-form input{width:100%;padding:12px 14px;border-radius:14px;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.8);font:inherit}
  .cb-form textarea:focus,.cb-form input:focus{outline:none;border-color:var(--ink);box-shadow:0 0 0 1px var(--ink)}
  .cb-two{display:grid;grid-template-columns:1fr 1fr;gap:10px}@media (max-width:560px){.cb-two{grid-template-columns:1fr}}`;
  document.head.append(s);
})();

async function colabore() {
  setNav("colabore");
  document.title = "Colabore · Fiscaliza Brasil";
  let tipo = "Ideia";
  M.innerHTML = `<section class="card glass cb-hero"><span class="kick">Colabore</span><h1>Ajude o Fiscaliza Brasil a continuar</h1><span class="fx"></span>
     <p class="muted" style="margin:0">O Fiscaliza Brasil é gratuito, independente e sem anúncios. As doações pagam o servidor, o domínio e o tempo para buscar dados oficiais e criar novas ferramentas. Ideias e correções também ajudam muito.</p></section>
   <section class="card glass" id="cb-pix"><h2 style="margin:0">Doe pelo Pix</h2><p class="muted small" style="margin:0">Carregando…</p></section>
   <section class="card glass"><h2 style="margin:0">Mande uma ideia, sugestão ou correção</h2>
     <p class="muted small" style="margin:0">Viu um dado errado, sentiu falta de algo ou tem uma ideia de ferramenta? Conte aqui. Todas as mensagens são lidas.</p>
     <div class="cb-form">
      <div class="yrs" id="cb-t">${["Ideia", "Sugestão", "Correção", "Outro"].map((t) => `<button type="button" data-t="${t}" aria-pressed="${t === tipo}">${t}</button>`).join("")}</div>
      <textarea id="cb-m" rows="5" maxlength="2000" placeholder="Escreva sua mensagem"></textarea>
      <div class="cb-two"><input id="cb-n" maxlength="80" placeholder="Seu nome (opcional)"><input id="cb-c" maxlength="200" placeholder="E-mail ou @ para resposta (opcional)"></div>
      <p class="src" style="margin:0">Seu nome e contato são usados só para responder a esta mensagem. Não são publicados nem compartilhados. Para apagar, peça pelo mesmo contato. <a href="#/privacidade">Privacidade</a></p>
      <div class="cb-btns"><button class="btn" id="cb-s" type="button">Enviar</button><span class="small" id="cb-e" style="align-self:center"></span></div></div></section>
   <section class="card glass"><h2 style="margin:0">Para onde vai o dinheiro</h2>
     <ul class="cb-list">
      <li><i>1</i><div><b>Manter o site no ar</b><br><span>Servidor, banco de dados e domínio fiscalizaja.com.br.</span></div></li>
      <li><i>2</i><div><b>Dados sempre atualizados</b><br><span>Tempo e ferramentas para buscar e conferir os dados da Câmara, do Senado, do TSE e dos estados.</span></div></li>
      <li><i>3</i><div><b>Novas ferramentas</b><br><span>Acompanhar políticos e partidos, comparar, mais cidades e estados.</span></div></li>
     </ul></section>
   <section class="card glass"><h2 style="margin:0">Regras das doações</h2>
     <ul class="cb-list">
      <li><i>✓</i><div><b>Doação voluntária e sem contrapartida</b><br><span>Não é assinatura e não libera nada exclusivo. O site continua igual e gratuito para todo mundo.</span></div></li>
      <li><i>✓</i><div><b>Independência</b><br><span>Não aceitamos doações de partidos, candidatos, gabinetes ou órgãos públicos. Quem doa não influencia o conteúdo nem os dados.</span></div></li>
      <li><i>✓</i><div><b>Confira antes de pagar</b><br><span>No aplicativo do banco, confira se o nome do recebedor é o que aparece nesta página.</span></div></li>
     </ul></section>`;
  // tipo da mensagem
  const marca = () => document.querySelectorAll("#cb-t button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.t === tipo));
  document.querySelectorAll("#cb-t button").forEach((b) => (b.onclick = () => { tipo = b.dataset.t; marca(); }));
  $("#cb-s").onclick = async () => {
    const m = $("#cb-m").value.trim(), e = $("#cb-e");
    if (m.length < 3) { e.style.color = "var(--verm,#C62828)"; e.textContent = "Escreva sua mensagem."; return; }
    const b = $("#cb-s"); b.disabled = true; e.style.color = "var(--muted)"; e.textContent = "Enviando…";
    try {
      const sb = sbClient(); if (!sb) throw new Error("envio indisponível no momento");
      const nome = $("#cb-n").value.trim();
      const r = await sb.from("reportes").insert({ pagina: location.href.slice(0, 300), sobre: "Colabore · " + tipo, texto: ((nome ? nome + ": " : "") + m).slice(0, 2000), contato: $("#cb-c").value.trim().slice(0, 200) });
      if (r.error) throw r.error;
      $("#cb-m").value = ""; e.style.color = "var(--verde)"; e.textContent = "Recebido! Obrigado por ajudar.";
    } catch (err) { e.style.color = "var(--verm,#C62828)"; e.textContent = "Não foi possível enviar: " + (err.message || err); }
    b.disabled = false;
  };
  // Pix
  let pix = null;
  try { pix = JSON.parse(localStorage.getItem("fb_pix") || "null"); } catch (e) {}
  const drawPix = () => {
    const box = $("#cb-pix"); if (!box) return;
    if (!pix || pix.ativo === false || (!pix.chave && !pix.copia && !pix.qr)) { box.innerHTML = `<h2 style="margin:0">Doe pelo Pix</h2><p class="muted" style="margin:0">A chave Pix vai aparecer aqui em breve. Enquanto isso, você pode ajudar mandando ideias e correções logo abaixo.</p>`; return; }
    box.innerHTML = `<h2 style="margin:0">Doe pelo Pix</h2>
     <div class="cb-pix">${pix.qr ? `<div class="cb-qr"><img src="${esc(pix.qr)}" alt="QR code do Pix"></div>` : ""}
      <div style="display:grid;gap:10px;min-width:0;width:100%">
       <p class="muted small" style="margin:0">${pix.qr ? "Aponte a câmera do aplicativo do banco para o QR code, ou copie a chave." : "Copie a chave e cole na área Pix do aplicativo do banco."} Qualquer valor ajuda.</p>
       ${pix.chave ? `<div class="cb-key"><small>Chave Pix</small><code id="cb-k">${esc(pix.chave)}</code></div>` : ""}
       ${pix.nome ? `<div class="cb-key"><small>Recebedor</small><code>${esc(pix.nome)}</code></div>` : ""}
       <div class="cb-btns">${pix.chave ? '<button class="btn" type="button" data-cp="chave">Copiar chave</button>' : ""}${pix.copia ? '<button class="btn o" type="button" data-cp="copia">Copiar Pix copia e cola</button>' : ""}</div>
      </div></div>`;
    box.querySelectorAll("[data-cp]").forEach((b) => (b.onclick = async () => {
      const t = pix[b.dataset.cp]; const o = b.textContent;
      try { await navigator.clipboard.writeText(t); b.textContent = "Copiado!"; } catch (e) { prompt("Copie:", t); }
      setTimeout(() => (b.textContent = o), 1800);
    }));
  };
  drawPix();
  try {
    const sb = sbClient();
    if (sb) { const q = await sb.from("site_config").select("valor").eq("chave", "pix").maybeSingle(); if (!q.error) { pix = q.data && q.data.valor ? JSON.parse(q.data.valor) : null; try { localStorage.setItem("fb_pix", JSON.stringify(pix)); } catch (e) {} } }
  } catch (e) {}
  drawPix();
}
