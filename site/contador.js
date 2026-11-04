/* Conta cada abertura de página (inclusive F5) e mantém o "no site agora" (quem abriu nos últimos 5 minutos).
   Uso: <script src="contador.js"></script> depois de config.js e da biblioteca do Supabase. */
(function () {
  const C = window.FB_CFG || {};
  let sb = null;
  try { if (C.url && C.key && window.supabase) sb = supabase.createClient(C.url, C.key, { auth: { persistSession: false } }); } catch (e) {}
  let sess = null;
  try { sess = sessionStorage.getItem("fb_sess"); if (!sess) { sess = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now()).replace(/-/g, ""); sessionStorage.setItem("fb_sess", sess); } } catch (e) { sess = String(Date.now()) + "x" + String(Math.random()).slice(2, 10); }
  const ouvintes = [];
  const avisa = (d) => ouvintes.forEach((f) => { try { f(d); } catch (e) {} });
  const chama = async (conta) => {
    if (!sb) return null;
    try { const r = await sb.rpc("registrar_acesso", { p_sessao: sess, p_conta: conta }); if (!r.error && r.data) { window.FB_ACESSOS = r.data; avisa(r.data); return r.data; } } catch (e) {}
    return null;
  };
  chama(true);
  setInterval(() => { if (!document.hidden) chama(false); }, 60000);
  window.FBContador = { ouvir: (f) => { ouvintes.push(f); if (window.FB_ACESSOS) f(window.FB_ACESSOS); } };
})();
