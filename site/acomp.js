/* ACOMPANHAR: a pessoa escolhe vários políticos (de qualquer cargo) e partidos para acompanhar.
   Fica salvo no aparelho na hora (localStorage) e, se a pessoa entrar com o e-mail (código ou link, sem senha),
   é sincronizado na tabela "acompanha" do Supabase e aparece em qualquer aparelho. Rota: #/acompanho. */
(function () {
  const KEY = "fb_acomp";
  let SBU = null, USER = null;
  const sbU = () => {
    const C = window.FB_CFG || {};
    if (!SBU && C.url && C.key && window.supabase) SBU = supabase.createClient(C.url, C.key, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: "pkce", storageKey: "fb-usuario" } });
    return SBU;
  };
  const ler = () => { try { const x = JSON.parse(localStorage.getItem(KEY) || "null"); if (x && Array.isArray(x.itens)) return x; } catch (e) {} return { itens: [] }; };
  const gravar = (x) => { try { localStorage.setItem(KEY, JSON.stringify(x)); } catch (e) {} contador(); };
  const chave = (it) => it.tipo + ":" + it.ref;
  const tem = (tipo, ref) => ler().itens.some((i) => i.tipo === tipo && i.ref === ref);

  async function servidor(op, it) {
    if (!USER) return; const sb = sbU(); if (!sb) return;
    try {
      if (op === "add") await sb.from("acompanha").upsert({ user_id: USER.id, tipo: it.tipo, ref: it.ref, dados: it });
      else await sb.from("acompanha").delete().eq("tipo", it.tipo).eq("ref", it.ref);
    } catch (e) {}
  }
  async function sincronizar() {
    const sb = sbU(); if (!sb || !USER) return;
    const q = await sb.from("acompanha").select("tipo,ref,dados"); if (q.error) return;
    const local = ler(); const mapa = new Map(local.itens.map((i) => [chave(i), i]));
    const faltam = local.itens.filter((i) => !q.data.some((r) => r.tipo === i.tipo && r.ref === i.ref));
    q.data.forEach((r) => { const it = Object.assign({ tipo: r.tipo, ref: r.ref }, r.dados || {}); if (!mapa.has(chave(it))) mapa.set(chave(it), it); });
    gravar({ itens: [...mapa.values()] });
    if (faltam.length) await sb.from("acompanha").upsert(faltam.map((i) => ({ user_id: USER.id, tipo: i.tipo, ref: i.ref, dados: i })));
  }
  function alternar(it) {
    const x = ler(); const k = chave(it); const i = x.itens.findIndex((y) => chave(y) === k);
    if (i >= 0) { x.itens.splice(i, 1); gravar(x); servidor("del", it); return false; }
    x.itens.push(Object.assign({ em: new Date().toISOString().slice(0, 10) }, it)); gravar(x); servidor("add", it); return true;
  }
  function botao(el, it) {
    if (!el) return;
    const pinta = () => { const on = tem(it.tipo, it.ref); el.setAttribute("aria-pressed", on); el.textContent = on ? "★ Acompanhando" : "☆ Acompanhar"; };
    pinta(); el.classList.add("acbtn");
    el.onclick = () => { const on = alternar(it); pinta(); if (typeof toast2 === "function") toast2(on ? "Adicionado em Acompanhando." : "Removido de Acompanhando."); };
  }
  function contador() { const n = ler().itens.length; document.querySelectorAll(".acn").forEach((e) => (e.textContent = n ? n : "")); }

  const erroPT = (m) => { m = String(m || "");
    if (/rate limit|too many|security purposes/i.test(m)) return "Muitos pedidos seguidos: espere um minuto e tente de novo.";
    if (/signups? not allowed/i.test(m)) return "O cadastro de novos e-mails está fechado no momento. Tente mais tarde.";
    if (/invalid.*email|email.*invalid/i.test(m)) return "Confira se o e-mail está certo.";
    if (/sending|smtp|confirmation email/i.test(m)) return "O serviço de e-mail falhou. Tente de novo em alguns minutos.";
    return "Tente de novo em alguns minutos."; };
  /* ---------- login por e-mail (código de 6 dígitos ou link) ---------- */
  async function iniciar() {
    const sb = sbU(); if (!sb) return;
    try {
      const { data } = await sb.auth.getSession(); USER = data.session ? data.session.user : null;
      sb.auth.onAuthStateChange((ev, ses) => { const antes = USER; USER = ses ? ses.user : null; if (USER && !antes) sincronizar().then(() => { if (location.hash.startsWith("#/acompanho")) acompanho(); }); });
      if (USER) await sincronizar();
    } catch (e) {}
    // volta do link do e-mail: limpa o ?code= do endereço e abre a página Acompanhando
    if (/[?&]code=/.test(location.search)) { history.replaceState(null, "", location.pathname + "#/acompanho"); if (typeof route === "function") route(); }
    contador();
  }

  const css = document.createElement("style");
  css.textContent = `
  .acn{font-family:var(--f-mono);font-size:.7rem;font-weight:600;background:var(--ink);color:#fff;border-radius:999px;padding:2px 6px;margin-left:4px}.acn:empty{display:none}
  .top .acl{display:inline-flex;align-items:center;gap:4px;white-space:nowrap}
  .acgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
  .accard{display:grid;gap:10px;padding:16px;border-radius:20px;background:rgba(255,255,255,.78);border:1px solid rgba(11,11,12,.08)}
  .accard .hd{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:12px;align-items:center}
  .accard .hd b{font-family:var(--f-display);font-size:1rem;display:block;line-height:1.2}.accard .hd small{color:var(--muted);font-size:.78rem}
  .accard .x{border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.8);border-radius:999px;width:32px;height:32px;font-size:.9rem}
  .acst{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.acst div{padding:8px;border-radius:12px;background:rgba(11,11,12,.04);display:grid;gap:2px}
  .acst b{font-family:"Bricolage Grotesque",var(--f-display);font-weight:800;font-size:1.15rem;line-height:1}.acst span{font-family:var(--f-display);font-weight:700;font-size:.56rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
  .acv{display:grid;gap:6px}.acv a{display:grid;grid-template-columns:auto minmax(0,1fr);gap:8px;align-items:start;font-size:.82rem;line-height:1.3;color:inherit;text-decoration:none}
  .acv i{font-style:normal;width:10px;height:10px;border-radius:50%;margin-top:4px}.acv i.g{background:#1E9E55}.acv i.r{background:#D93025}.acv i.n{background:#C9CBD0}
  .aclogin{display:grid;gap:10px;max-width:520px}.aclogin input{width:100%;padding:12px 14px;border-radius:14px;border:1px solid rgba(11,11,12,.14);background:rgba(255,255,255,.85);font:inherit}
  .aclogin .row[hidden]{display:none}.aclogin .row{display:flex;gap:8px;flex-wrap:wrap}.aclogin .row input{flex:1;min-width:200px}`;
  document.head.append(css);

  function loginHTML() {
    if (USER) return `<div class="aclogin"><p style="margin:0">Salvando no e-mail <b>${esc(USER.email || "")}</b>. A sua lista aparece em qualquer aparelho em que você entrar com ele.</p>
      <label class="row" style="align-items:center;gap:10px;cursor:pointer"><input type="checkbox" id="acres" style="width:22px;height:22px;flex:none;min-width:0"> <span><b>Receber o resumo semanal por e-mail</b><br><span class="small muted">Toda segunda: como votaram e o que apresentaram os políticos que você acompanha. Dá para parar quando quiser, pelo link do próprio e-mail.</span></span></label>
      <label class="row" style="align-items:center;gap:10px;cursor:pointer"><input type="checkbox" id="acdia" style="width:22px;height:22px;flex:none;min-width:0"> <span><b>Receber alerta diário</b><br><span class="small muted">Na manhã seguinte ao dia em que um político que você acompanha votar no Plenário ou apresentar projeto. Só chega quando há novidade.</span></span></label>
      <div class="row"><button class="btn o" id="acout" type="button">Sair</button><button class="btn o" id="acdel" type="button">Apagar minha conta</button></div></div>`;
    return `<div class="aclogin"><p style="margin:0">Sua lista já está salva <b>neste aparelho</b>. Para ver em qualquer celular ou computador, entre com o seu e-mail. Não precisa de senha: você recebe um código.</p>
      <div class="row"><input id="acem" type="email" autocomplete="email" placeholder="seu@email.com"><button class="btn" id="acsend" type="button">Receber código</button></div>
      <div class="row" id="accode" hidden><input id="actk" inputmode="numeric" autocomplete="one-time-code" maxlength="10" placeholder="Código recebido no e-mail"><button class="btn" id="acok" type="button">Entrar</button></div>
      <p class="small" id="acmsg" style="margin:0;min-height:1.2em"></p>
      <p class="src" style="margin:0">Guardamos só o seu e-mail e a lista do que você acompanha, para mostrar a lista nos seus aparelhos. Nada é publicado ou compartilhado, e você pode apagar tudo quando quiser. <a href="#/privacidade">Privacidade</a></p></div>`;
  }
  function ligarLogin() {
    const sb = sbU(); const msg = (t, ok) => { const m = $("#acmsg"); if (m) { m.textContent = t; m.style.color = ok ? "var(--verde)" : "#B3261E"; } };
    if ($("#acsend")) $("#acsend").onclick = async () => {
      const em = $("#acem").value.trim(); if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) return msg("Digite um e-mail válido.");
      if (!sb) return msg("Login indisponível no momento.");
      $("#acsend").disabled = true; msg("Enviando…", true); $("#acmsg").style.color = "var(--muted)";
      const r = await sb.auth.signInWithOtp({ email: em, options: { shouldCreateUser: true, emailRedirectTo: location.origin + "/fiscalize" } });
      $("#acsend").disabled = false;
      if (r.error) return msg("Não foi possível enviar o código. " + erroPT(r.error.message));
      $("#accode").hidden = false; $("#actk").focus(); msg("Enviamos um e-mail. Digite o código aqui ou toque no link do e-mail neste aparelho.", true);
    };
    if ($("#acok")) $("#acok").onclick = async () => {
      const em = $("#acem").value.trim(), tk = $("#actk").value.replace(/\D/g, ""); if (tk.length < 6) return msg("Digite o código completo.");
      $("#acok").disabled = true; const r = await sb.auth.verifyOtp({ email: em, token: tk, type: "email" }); $("#acok").disabled = false;
      if (r.error) return msg("Código inválido ou vencido. Peça um novo.");
      USER = r.data.user; await sincronizar(); acompanho();
    };
    if ($("#acres") && sb && USER) {
      sb.from("resumo_email").select("ativo,diario").maybeSingle().then((r) => { if (r.data) { $("#acres").checked = r.data.ativo; if ($("#acdia")) $("#acdia").checked = !!r.data.diario; } else if (r.error) { if ($("#acdia")) $("#acdia").closest("label").hidden = true; sb.from("resumo_email").select("ativo").maybeSingle().then((q) => { if (q.data) $("#acres").checked = q.data.ativo; }); } });
      if ($("#acdia")) $("#acdia").onchange = async (e) => { const r = await sb.from("resumo_email").upsert({ user_id: USER.id, diario: e.target.checked, ativo: $("#acres").checked, atualizado: new Date().toISOString() });
        if (r.error) { e.target.checked = !e.target.checked; alert("Não foi possível salvar agora. Tente de novo em alguns minutos."); } };
      $("#acres").onchange = async (e) => { const r = await sb.from("resumo_email").upsert({ user_id: USER.id, ativo: e.target.checked, atualizado: new Date().toISOString() });
        if (r.error) { e.target.checked = !e.target.checked; alert("Não foi possível salvar agora. Tente de novo em alguns minutos."); } };
    }
    if ($("#acout")) $("#acout").onclick = async () => { await sb.auth.signOut(); USER = null; acompanho(); };
    if ($("#acdel")) $("#acdel").onclick = async () => {
      if (!confirm("Apagar sua conta e a lista salva no e-mail? A lista continua neste aparelho.")) return;
      const r = await sb.rpc("apagar_minha_conta"); if (r.error) { alert("Não foi possível apagar: " + r.error.message); return; }
      await sb.auth.signOut(); USER = null; acompanho();
    };
  }

  /* ---------- página Acompanhando ---------- */
  async function cartaoPolitico(it) {
    const href = "#/p/" + it.ref;
    let extra = `<a class="btn o" style="justify-self:start;padding:8px 14px;text-decoration:none" href="${href}">Abrir a ficha</a>`;
    try {
      if (it.casa === "C" || it.casa === "S") {
        const X = (await (it.casa === "C" ? loadC(it.uf) : loadS(it.uf)))[it.id];
        const VL = it.casa === "C" ? await loadVC() : await loadVS(); await loadPart();
        if (X) {
          const pos = posPartido(it.part, it.casa); const v = X.v || ""; let a = 0, c = 0, ult = [];
          for (let i = v.length - 1; i >= 0; i--) { const x = v[i];
            if (x in VOTO && x !== "-") { const p = pos[i]; const cls = X.fp ? (X.fp[i] === "g" ? "g" : X.fp[i] === "r" ? "r" : "n") : x === "S" || x === "N" ? (p === "S" || p === "N" ? (x === p ? "g" : "r") : "n") : "n";
              if (cls === "g") a++; else if (cls === "r") c++;
              if (ult.length < 4) ult.push([i, x, cls]); } }
          const pres = X.pres && X.pres[1] ? Math.round((100 * X.pres[0]) / X.pres[1]) + "%" : "—";
          const tit = (i) => (it.casa === "C" ? VL[i][5] : VL[i][2]) || "Votação";
          extra = `<div class="acst"><div><b>${pres}</b><span>Presença nas votações</span></div><div><b style="color:#14703C">${a + c ? Math.round((100 * a) / (a + c)) + "%" : "—"}</b><span>Com o partido</span></div><div><b style="color:#B3261E">${c}</b><span>Contra o partido</span></div></div>
            <div class="acv">${ult.map(([i, x, cls]) => `<a href="${href}"><i class="${cls}"></i><span><b>${VOTO[x][0]}</b> · ${esc(tit(i))} · ${new Date(VL[i][1] + "T12:00").toLocaleDateString("pt-BR")}</span></a>`).join("")}</div>` + extra;
        }
      }
    } catch (e) {}
    return `<div class="accard"><div class="hd">${av(it.nome, it.foto)}<span style="min-width:0"><b>${esc(it.nome)}</b><small>${esc(it.cargo || "")}${it.part ? " · " + esc(it.part) : ""}</small></span><button class="x" type="button" data-rm="${esc(it.tipo + ":" + it.ref)}" aria-label="Parar de acompanhar">✕</button></div>${extra}</div>`;
  }
  async function acompanho() {
    setNav("mais"); document.title = "Acompanhando · Fiscaliza Brasil";
    const L = ler().itens; const pol = L.filter((i) => i.tipo === "p"), par = L.filter((i) => i.tipo === "partido");
    M.innerHTML = `<section class="card glass"><span class="kick">Acompanhando</span><h1>Quem você acompanha</h1><span class="fx"></span>
       <p class="muted" style="margin:0">Escolha políticos de qualquer cargo e partidos com o botão <b>☆ Acompanhar</b> na ficha de cada um. Aqui você vê, num lugar só, se eles estão indo às votações e se votam junto com o partido (<b style="color:#14703C">verde</b>) ou contra (<b style="color:#B3261E">vermelho</b>).</p>
       <div class="btns"><a class="btn o" href="#/quem">Buscar políticos</a><a class="btn o" href="#/partidos">Ver partidos</a></div></section>
     <section class="card glass"><h2 style="margin:0">Salvar em todos os aparelhos</h2><div id="aclog">${loginHTML()}</div></section>
     <section class="card glass"><h2 style="margin:0">Políticos <span class="muted small">(${pol.length})</span></h2><div class="acgrid" id="acp">${pol.length ? '<p class="muted">Carregando…</p>' : '<p class="muted" style="margin:0">Nenhum político ainda. Abra a ficha de um político e toque em ☆ Acompanhar.</p>'}</div></section>
     <section class="card glass"><h2 style="margin:0">Partidos <span class="muted small">(${par.length})</span></h2><div class="acgrid" id="acpt">${par.length ? "" : '<p class="muted" style="margin:0">Nenhum partido ainda. Abra um partido em PARTIDOS e toque em ☆ Acompanhar.</p>'}</div></section>`;
    ligarLogin();
    if (par.length) { await loadPart(); $("#acpt").innerHTML = par.map((it) => { const p = PART.partidos.find((x) => x.s === it.ref); if (!p) return ""; const s = PART.stat[p.s];
      return `<div class="accard"><div class="hd">${selo(p)}<span style="min-width:0"><b>${esc(p.nome)}</b><small>${s.dep} deputados · ${s.sen} senadores</small></span><button class="x" type="button" data-rm="partido:${esc(p.s)}" aria-label="Parar de acompanhar">✕</button></div>
        ${s.coes != null ? `<div class="acst"><div><b style="color:#14703C">${pctx(s.coes)}</b><span>Votos com o partido</span></div><div><b style="color:#B3261E">${mil(s.c)}</b><span>Votos contra</span></div><div><b>${pctx(s.gov)}</b><span>Com o governo</span></div></div>${meter(s.a, s.c)}` : '<p class="muted small" style="margin:0">Sem parlamentares no Congresso.</p>'}
        <a class="btn o" style="justify-self:start;padding:8px 14px;text-decoration:none" href="#/partidos/${encodeURIComponent(p.s)}">Ver o partido</a></div>`; }).join(""); }
    if (pol.length) $("#acp").innerHTML = (await Promise.all(pol.map(cartaoPolitico))).join("");
    document.querySelectorAll("[data-rm]").forEach((b) => (b.onclick = () => { const [tipo, ...r] = b.dataset.rm.split(":"); alternar({ tipo, ref: r.join(":") }); acompanho(); }));
  }

  /* link "parar de receber" do e-mail semanal: #/sair/<código> */
  async function sair(t) {
    setNav(""); M.innerHTML = `<section class="card glass"><span class="kick">Resumo semanal</span><h1>Cancelando…</h1></section>`;
    const sb = sbU(); let ok = false; if (sb && /^[0-9a-f-]{36}$/i.test(t || "")) { const r = await sb.rpc("sair_resumo", { t }); ok = !r.error && r.data; }
    M.innerHTML = `<section class="card glass"><span class="kick">Resumo semanal</span><h1>${ok ? "Pronto: você não vai mais receber o resumo" : "Não encontrei esta inscrição"}</h1><span class="fx"></span>
      <p class="muted" style="margin:0">${ok ? "Sua lista de políticos acompanhados continua salva. Para voltar a receber, marque a opção na página Acompanhando." : "Talvez você já tenha saído antes. Se ainda receber o e-mail, desmarque a opção na página Acompanhando."}</p>
      <div class="btns"><a class="btn" href="#/acompanho">Acompanhando</a><a class="btn o" href="#/">Início</a></div></section>`;
  }
  window.FBAcomp = { botao, tem, alternar, ler, iniciar, acompanho, sair };
  window.acompanho = acompanho;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar); else iniciar();
})();
