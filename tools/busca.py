"""Índice de busca de todos os políticos do site (Quem é quem): deputados federais e estaduais, senadores, governadores e vices,
prefeitos e vices, vereadores, eleitos de 2026. Saída: site/data/busca/{3 letras}.json, cada um com os nomes que têm uma palavra
começando por essas letras: [[nome, cargo · partido · lugar, UF, link, texto normalizado]]."""
import json, re, unicodedata, shutil
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "busca"
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper())).strip()
tit = lambda s: " ".join(w.lower() if w.upper() in ("DA", "DE", "DO", "DAS", "DOS", "E") and i else w.capitalize() for i, w in enumerate(str(s).split()))
gen = lambda c, sx: re.sub(r"\(a\)", "a", re.sub(r"o\(a\)", "a", c)) if sx == "F" else c.replace("(a)", "")
E = []
def add(p, cargo, uf, h, lugar=""):
    if not p or not p[0]: return
    sx = p[4] if len(p) > 4 else ""
    E.append([tit(p[0]), gen(cargo, sx) + (" · " + p[2] if p[2] else "") + (" · " + lugar if lugar else ""), uf, h, norm(p[0] + " " + p[1])])

B = json.load(open(D / "br.json"))
for d in B["dep"]: E.append([d[1], gen("Deputado(a) federal", d[10] if len(d) > 10 else "") + " · " + d[2], d[3], f"#/p/c/{d[0]}", norm(d[1] + " " + d[5])])
for s in B["sen"]: E.append([s[1], ("Senador(a)" if s[6] == "Titular" else "Senador(a) suplente") + " · " + s[3], s[4], f"#/p/s/{s[0]}", norm(s[1] + " " + s[2])])
vistos = {e[4] + e[2] for e in E}
for uf, u in B["ufs"].items():
    for ano, k in (("22", "gov"), ("26", "gov26")):
        for i, p in enumerate((u.get(k) or [])[:2]):
            if p: add(p, ("Governador(a)" if i == 0 else "Vice-governador(a)") + (" eleito(a) em 2026" if ano == "26" else ""), uf, f"#/p/g/{uf}/{i}/{ano}")
for f in sorted((D / "uf").glob("*.json")):
    uf = f.stem; U = json.load(open(f))
    for i, p in enumerate(U.get("de22") or []): add(p, "Deputado(a) estadual", uf, f"#/p/e/{uf}/22/{i}")
    for i, p in enumerate(U.get("de26") or []): add(p, "Deputado(a) estadual eleito(a) em 2026", uf, f"#/p/e/{uf}/26/{i}")
    for i, p in enumerate(U.get("df26") or []):
        if norm(p[0] + " " + p[1]) + uf not in vistos: add(p, "Deputado(a) federal eleito(a) em 2026", uf, f"#/p/f/{uf}/26/{i}")
    for i, p in enumerate(U.get("se26") or []):
        if norm(p[0] + " " + p[1]) + uf not in vistos: add(p, "Senador(a) eleito(a) em 2026", uf, f"#/p/n/{uf}/26/{i}")
    for ue, m in (U.get("mun") or {}).items():
        c = tit(m[0]); add(m[1], "Prefeito(a)", uf, f"#/p/m/{uf}/{ue}/p", c); add(m[2], "Vice-prefeito(a)", uf, f"#/p/m/{uf}/{ue}/v", c)
        for i, p in enumerate(m[3] or []): add(p, "Vereador(a)", uf, f"#/p/m/{uf}/{ue}/{i}", c)
G = defaultdict(list)
for e in E:
    for k in {w[:3] for w in e[4].split() if len(w) >= 3 and w not in ("DAS", "DOS")}: G[k].append(e)
shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()
for k, L in G.items(): json.dump(L, open(OUT / f"{k}.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("busca:", len(E), "políticos,", len(G), "arquivos,", round(sum(p.stat().st_size for p in OUT.glob("*.json")) / 1e6, 1), "MB")
