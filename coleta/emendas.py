"""Emendas parlamentares do Brasil todo (Portal da Transparência, CGU), por cidade que recebeu o dinheiro.
Baixa o arquivo único de emendas, lê a planilha "por favorecido" (quem recebeu, em que cidade, quanto) desde 2023
e liga o autor da emenda ao deputado federal ou senador do site.
Saída: site/data/emendas/{UF}.json  {"cid": {CIDADE_NORMALIZADA: [[casa, id, nome, partido, total, [[favorecido, valor] x3]]]}}
       site/data/emendas/autores.json {"C:id"|"S:id": total pago desde 2023}"""
import csv, io, json, re, sys, unicodedata, zipfile
from collections import defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"
OUTD = D / "emendas"; OUTD.mkdir(exist_ok=True)
URLS = ["https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO",
        "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/EmendasParlamentares.zip"]
norm = lambda s: re.sub(r"[^A-Z ]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()).strip()
num = lambda s: float(str(s or "0").replace(".", "").replace(",", ".") or 0)

def baixa():
    for u in URLS:
        try:
            r = requests.get(u, timeout=600, headers={"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}, allow_redirects=True)
            if r.ok and r.content[:2] == b"PK": print("baixou", u, len(r.content) // 1024 // 1024, "MB", flush=True); return zipfile.ZipFile(io.BytesIO(r.content))
            print("sem zip em", u, r.status_code, r.headers.get("content-type"), flush=True)
        except Exception as e: print("erro", u, e, flush=True)
    raise RuntimeError("não consegui baixar o arquivo de emendas")

def col(h, *pals, nao=()):
    for i, c in enumerate(h):
        cn = norm(c)
        if all(norm(p) in cn for p in pals) and not any(norm(x) in cn for x in nao): return i
    return None

def main():
    z = baixa(); print("arquivos:", z.namelist(), flush=True)
    nome = next((n for n in z.namelist() if "favorecido" in n.lower()), None)
    if not nome: raise RuntimeError("planilha por favorecido não encontrada: " + ", ".join(z.namelist()))
    BR = json.load(open(D / "br.json"))
    autores = {}
    for d in BR["dep"]:
        for k in (d[1], d[5]):
            if k: autores.setdefault(norm(k), ("C", str(d[0]), d[1], d[2]))
    for s in BR["sen"]:
        for k in (s[1], s[2]):
            if k: autores.setdefault(norm(k), ("S", str(s[0]), s[1], s[3]))
    f = io.TextIOWrapper(z.open(nome), encoding="latin-1", newline="")
    rd = csv.reader(f, delimiter=";"); h = next(rd); print("colunas:", h, flush=True)
    iA = col(h, "nome", "autor"); iF = col(h, "favorecido", nao=("codigo", "tipo", "natureza", "uf", "municipio"))
    iU = col(h, "uf", "favorecido") or col(h, "uf"); iM = col(h, "municipio", "favorecido") or col(h, "municipio", nao=("codigo",))
    iV = col(h, "valor", "recebido") or col(h, "valor"); iY = col(h, "ano")
    if None in (iA, iF, iU, iM, iV): raise RuntimeError(f"colunas não reconhecidas: {h}")
    tot = defaultdict(float); fav = defaultdict(lambda: defaultdict(float)); porAutor = defaultdict(float); semAutor = defaultdict(float); n = 0
    for r in rd:
        if len(r) <= max(iA, iF, iU, iM, iV): continue
        ano = re.search(r"(20\d\d)", r[iY] if iY is not None else "")
        if ano and int(ano.group(1)) < 2023: continue
        a = autores.get(norm(r[iA]))
        v = num(r[iV]); uf = (r[iU] or "").strip().upper(); m = norm(r[iM])
        if not v or len(uf) != 2 or not m: continue
        if not a: semAutor[r[iA].strip()] += v; continue
        k = (uf, m, a); tot[k] += v; fav[k][r[iF].strip()] += v; porAutor[a[0] + ":" + a[1]] += v; n += 1
    cid = defaultdict(lambda: defaultdict(list))
    for (uf, m, a), v in tot.items():
        top = sorted(fav[(uf, m, a)].items(), key=lambda x: -x[1])[:3]
        cid[uf][m].append([a[0], a[1], a[2], a[3], round(v), [[x, round(y)] for x, y in top]])
    for uf, cs in cid.items():
        for m in cs: cs[m].sort(key=lambda x: -x[4])
        json.dump({"fonte": "Portal da Transparência (CGU) · Emendas parlamentares por favorecido, desde 2023", "cid": cs}, open(OUTD / f"{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump({k: round(v) for k, v in porAutor.items()}, open(OUTD / "autores.json", "w"), separators=(",", ":"))
    print("linhas usadas:", n, "UFs:", len(cid), "autores não ligados (maiores):", sorted(semAutor.items(), key=lambda x: -x[1])[:8])
    return {"linhas": n, "ufs": len(cid), "autores": len(porAutor), "cidades": sum(len(c) for c in cid.values())}

if __name__ == "__main__":
    print(json.dumps(main()))
