/* Página de links da bio: desenho compartilhado entre /links (público) e a prévia do painel. */
(function () {
  const DEF_STYLE = {
    avatar: 104,            // tamanho da foto (px)
    foto: { zoom: 100, x: 50, y: 50, forma: "circulo", borda: true },  // enquadramento da foto
    name: { size: 24, ls: 6, upper: true },   // ls em centésimos de em
    handle: { size: 12, ls: 22 },
    bio: { size: 15 },
    btn: { size: 13, ls: 14, upper: true },
    gap1: 22,               // foto -> nome
    gap2: 30,               // textos -> botões
    stripe: true            // faixa verde-amarelo-azul
  };
  const DEF_PROFILE = {
    name: "Abraão Nery",
    handle: "@oabraaonery",
    bio: "Vamos fiscalizar tudo.",
    theme: "claro",
    avatar_path: null,
    style: {}
  };
  const DEF_LINKS = [
    { label: "Fiscaliza Brasil", url: "/", active: true },
    { label: "Fiscalize os políticos", url: "/fiscalize", active: true },
    { label: "Simulador do voto distrital", url: "/distrital", active: true },
    { label: "Instagram", url: "https://instagram.com/oabraaonery", active: true }
  ];

  const merge = (o) => {
    const d = JSON.parse(JSON.stringify(DEF_STYLE));
    const m = (a, b) => { for (const k in b) { if (b[k] && typeof b[k] === "object" && !Array.isArray(b[k])) m(a[k] = a[k] || {}, b[k]); else a[k] = b[k]; } };
    m(d, o && typeof o === "object" ? o : {});
    return d;
  };
  const fixUrl = (u) => {
    u = (u || "").trim();
    if (!u) return "";
    if (/^\//.test(u)) return u;                       // endereço do próprio site
    if (/^(https?:\/\/|mailto:|tel:)/i.test(u)) return u;
    if (/^@/.test(u)) return "https://instagram.com/" + u.slice(1);
    return "https://" + u.replace(/^[a-z]+:\/*/i, "");
  };
  const go = (u) => (window.FB_ROUTES && window.FB_ROUTES[u]) || u;   // permite testar fora do domínio
  const mk = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  const initials = (n) => (n || "").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase() || "AN";

  /* p: perfil; ls: links ativos; opt: {pub(path)->url, onClick(link)} */
  function render(root, p, ls, opt) {
    opt = opt || {};
    const S = merge(p.style);
    root.textContent = "";
    root.classList.add("lkr");
    root.classList.toggle("dark", p.theme === "escuro");
    const w = mk("main", "lk-w");

    const av = mk("div", "lk-av");
    av.style.width = av.style.height = S.avatar + "px";
    av.style.marginBottom = S.gap1 + "px";
    const src = p.avatar_path && opt.pub ? opt.pub(p.avatar_path) : (p.avatar_url || "");
    const F = S.foto || {};
    av.style.borderRadius = F.forma === "arredondada" ? "28%" : "50%";
    if (F.borda === false) av.style.boxShadow = "0 14px 36px rgba(15,20,30,.18)";
    if (src) { const im = mk("img"); im.src = src; im.alt = p.name || ""; const pos = `${F.x ?? 50}% ${F.y ?? 50}%`;
      im.style.objectPosition = pos; im.style.transformOrigin = pos; im.style.transform = `scale(${(F.zoom || 100) / 100})`; av.append(im); }
    else { av.textContent = initials(p.name); av.style.fontSize = Math.round(S.avatar * 0.34) + "px"; }
    w.append(av);

    const h = mk("h1", "lk-n", p.name || "");
    h.style.fontSize = S.name.size + "px";
    h.style.letterSpacing = S.name.ls / 100 + "em";
    h.style.textTransform = S.name.upper ? "uppercase" : "none";
    w.append(h);
    if ((p.handle || "").trim()) {
      const hd = mk("p", "lk-h", p.handle.trim());
      hd.style.fontSize = S.handle.size + "px";
      hd.style.letterSpacing = S.handle.ls / 100 + "em";
      hd.style.paddingLeft = S.handle.ls / 100 + "em";
      w.append(hd);
    }
    if (S.stripe) w.append(mk("span", "lk-fx"));
    const lines = (p.bio || "").split(/\r?\n/).map((x) => x.trim()).filter(Boolean);
    if (lines.length) {
      const b = mk("div", "lk-b");
      lines.forEach((t) => { const e = mk("p", null, t); e.style.fontSize = S.bio.size + "px"; b.append(e); });
      w.append(b);
    }
    const sp = mk("div"); sp.style.height = S.gap2 + "px"; w.append(sp);

    (ls || []).forEach((l) => {
      const a = mk("a", "lk-a", l.label);
      const fu = fixUrl(l.url);
      a.href = go(fu);
      if (!/^\//.test(fu)) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
      a.style.fontSize = S.btn.size + "px";
      a.style.letterSpacing = S.btn.ls / 100 + "em";
      a.style.textTransform = S.btn.upper ? "uppercase" : "none";
      if (opt.onClick) a.addEventListener("click", () => opt.onClick(l));
      w.append(a);
    });

    const f = mk("a", "lk-f");
    f.href = go("/");
    f.innerHTML = '<svg viewBox="4 4 106 106" aria-hidden="true"><defs><clipPath id="fbl"><circle cx="50" cy="50" r="27"/></clipPath></defs><path d="M50 8 92 50 50 92 8 50Z" fill="#F7C21B"/><rect x="78" y="74" width="34" height="15" rx="7.5" transform="rotate(45 78 74)" fill="#0E8A4B"/><circle cx="50" cy="50" r="31" fill="#fff"/><circle cx="50" cy="50" r="27" fill="#1F4FBF"/><path clip-path="url(#fbl)" d="M14 52C34 36 66 36 88 46L88 54C66 45 34 45 14 60Z" fill="#fff"/><circle cx="40" cy="38" r="5" fill="#fff" opacity=".45"/></svg><span>Fiscaliza Brasil</span>';
    w.append(f);

    root.append(mk("div", "lk-bg"), w);
  }

  window.FBLinks = { DEF_STYLE, DEF_PROFILE, DEF_LINKS, merge, fixUrl, render, go };
})();
