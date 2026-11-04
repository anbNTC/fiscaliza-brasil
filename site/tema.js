/* MODO ESCURO: cores próprias para a noite (fotos, logo e selos dos partidos continuam com as cores originais).
   Guarda a escolha no aparelho; sem escolha, segue o modo do celular/computador. */
(function () {
  const K = "fb_tema";
  const CX = [".glass", ".card", ".lead", ".pc", ".tile", ".menu a", ".nw", ".hot", ".vimp", ".vrow", ".pcard", ".accard", ".sess", ".it", ".kv > div", ".cal button:not(:disabled)", ".nums div", ".go", ".note", ".cb-key", ".pnum div", ".wk div", ".acst div", ".pbox", ".xfb", ".tn li.it3", ".res a", ".ufb", ".step", ".lk-a", ".mapa", ".stage", ".cfgwarn", ".item", ".panel", ".tabs2", ".dt", ".dcard.w", ".search", ".rep form", ".live", ".cmpbar a"];
  const INK = [".btn:not(.o)", ".menu i", ".cal button[aria-pressed=\"true\"]", ".yrs button[aria-pressed=\"true\"]", ".trend button[aria-pressed=\"true\"]", ".nav a[aria-current]", ".tabs2 button[aria-selected=\"true\"]", ".tabs button[aria-pressed=\"true\"]", ".xlogo", ".chip.sg", ".acn", ".tg2.pol", ".vimp .pl span.s", ".cb-list li i", ".acbtn[aria-pressed=\"true\"]", ".dcard.k", ".cmpbar", ".step b", ".step > b", ".rk", ".dterm .dcard.k", ".lk-av", ".tema-fixo-x"];
  const css = `
  html.escuro{color-scheme:dark;--ink:#EDEDEA;--muted:#A4A7AD;--bg:#0D0F12;--surface:rgba(255,255,255,.05);--edge:rgba(255,255,255,.10);
    --fb-base:#0B0D10;--fb-verde:rgba(0,156,59,.16);--fb-amarelo:rgba(255,214,0,.10);--fb-azul:rgba(30,100,235,.16)}
  html.escuro body{color:var(--ink)}
  html.escuro body::before{mix-blend-mode:screen;opacity:.05}
  html.escuro :is(${CX.join(",")}){background-color:rgba(255,255,255,.05)!important;background-image:none!important;border-color:rgba(255,255,255,.10)!important;color:var(--ink)}
  html.escuro .glass{-webkit-backdrop-filter:blur(24px) saturate(140%);backdrop-filter:blur(24px) saturate(140%);box-shadow:0 10px 40px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.06)!important}
  html.escuro :is(.top,.nav){background-color:rgba(16,18,22,.72)!important}
  html.escuro :is(${INK.join(",")}){background:#EDEDEA!important;color:#0B0B0C!important;border-color:#EDEDEA!important}
  html.escuro :is(${INK.join(",")}) *{color:#0B0B0C}
  html.escuro :is(.btn.o,.home,.yrs button,.trend button,.chip,.tagv.n,.dnav button,.mnav button,.az button,.x,.seta,.minb + *,.cb-form input,.cb-form textarea,.aclogin input,.in,input,select,textarea){background-color:rgba(255,255,255,.07)!important;color:var(--ink)!important;border-color:rgba(255,255,255,.16)!important}
  html.escuro :is(input,select,textarea)::placeholder{color:#8C9097}
  html.escuro .go .seta{background:rgba(255,255,255,.08)!important;border-color:rgba(255,255,255,.18)!important;color:var(--ink)}
  html.escuro .av{background:linear-gradient(135deg,#2A2D33,#1E2126)!important;color:#C9CBD0!important}
  html.escuro .tagv.g,html.escuro .res2.a{background:rgba(30,158,85,.18)!important;color:#7FD6A2!important}
  html.escuro .tagv.r,html.escuro .res2.r{background:rgba(217,48,37,.18)!important;color:#FF9A92!important}
  html.escuro [style*="color:#14703C"]{color:#6FD39A!important}html.escuro [style*="color:#B3261E"],html.escuro .who .r{color:#FF8F86!important}
  html.escuro .hot{background:linear-gradient(135deg,rgba(255,255,255,.05),rgba(217,48,37,.10))!important;border-color:rgba(217,48,37,.35)!important}
  html.escuro .meter{background:rgba(255,255,255,.10)}html.escuro .hb{background:rgba(255,255,255,.10)!important}html.escuro .hb i{background:#EDEDEA!important}
  html.escuro .map path,html.escuro .mapa path{fill:rgba(255,255,255,.14)!important;stroke:#0B0D10!important}
  html.escuro .map text{stroke:#0B0D10!important;fill:#EDEDEA!important}
  html.escuro .mapa a:hover path,html.escuro .map a:hover path{fill:#1E9E55!important}
  html.escuro .src,html.escuro .muted{color:var(--muted)}
  html.escuro a{color:inherit}
  html.escuro .mbars i{background:rgba(255,255,255,.28)}html.escuro .mbars i.top{background:#FF6B60}
  html.escuro .cmpt th,html.escuro .cmpt td,html.escuro .dt,html.escuro .mrow,html.escuro .rkrow,html.escuro .prow{border-color:rgba(255,255,255,.08)!important}
  html.escuro .dcard{border-color:#EDEDEA!important}
  html.escuro .tema-fixo{background:rgba(16,18,22,.7)!important;border-color:rgba(255,255,255,.14)!important;color:var(--ink)!important}
  .temab{line-height:1}`;
  const st = document.createElement("style"); st.id = "fb-tema"; st.textContent = css;
  const pe = () => { if (!document.getElementById("fb-tema")) (document.body || document.head).append(st); };
  let pref = null; try { pref = localStorage.getItem(K); } catch (e) {}
  const sistema = matchMedia("(prefers-color-scheme: dark)");
  const aplica = () => { pe(); const esc = pref ? pref === "escuro" : sistema.matches; document.documentElement.classList.toggle("escuro", esc);
    document.querySelectorAll(".temab").forEach((b) => { b.innerHTML = esc ? '☀<span class="acl-t"> Claro</span>' : '☾<span class="acl-t"> Escuro</span>'; b.title = esc ? "Usar o modo claro" : "Usar o modo escuro"; });
    const mc = document.querySelector('meta[name="theme-color"]'); if (mc) mc.content = esc ? "#0B0D10" : "#FBFBF7"; };
  window.FBTema = { alternar() { const esc = document.documentElement.classList.contains("escuro"); pref = esc ? "claro" : "escuro"; try { localStorage.setItem(K, pref); } catch (e) {} aplica(); } };
  sistema.addEventListener && sistema.addEventListener("change", aplica);
  aplica(); document.addEventListener("DOMContentLoaded", aplica);
})();
