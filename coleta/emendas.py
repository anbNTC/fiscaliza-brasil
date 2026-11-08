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
            dest = Path("/tmp/emendas.zip")
            with requests.get(u, timeout=(30, 120), headers={"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}, allow_redirects=True, stream=True) as r:
                if not r.ok: print("HTTP", r.status_code, "em", u, flush=True); continue
                with open(dest, "wb") as f:
                    for ch in r.iter_content(1 << 20): f.write(ch)
            if dest.read_bytes()[:2] == b"PK": print("baixou", u, dest.stat().st_size // 1024 // 1024, "MB", flush=True); return zipfile.ZipFile(dest)
            print("o arquivo baixado não é zip:", u, flush=True)
        except Exception as e: print("erro", u, e, flush=True)
    raise RuntimeError("não consegui baixar o arquivo de emendas")

def col(h, *pals, nao=()):
    for i, c in enumerate(h):
        cn = norm(c)
        if all(norm(p) in cn for p in pals) and not any(norm(x) in cn for x in nao): return i
    return None

UFN = {"ACRE": "AC", "ALAGOAS": "AL", "AMAPA": "AP", "AMAZONAS": "AM", "BAHIA": "BA", "CEARA": "CE", "DISTRITO FEDERAL": "DF", "ESPIRITO SANTO": "ES",
       "GOIAS": "GO", "MARANHAO": "MA", "MATO GROSSO DO SUL": "MS", "MATO GROSSO": "MT", "MINAS GERAIS": "MG", "PARA": "PA", "PARAIBA": "PB", "PARANA": "PR",
       "PERNAMBUCO": "PE", "PIAUI": "PI", "RIO DE JANEIRO": "RJ", "RIO GRANDE DO NORTE": "RN", "RIO GRANDE DO SUL": "RS", "RONDONIA": "RO", "RORAIMA": "RR",
       "SANTA CATARINA": "SC", "SAO PAULO": "SP", "SERGIPE": "SE", "TOCANTINS": "TO"}
ABREV = {"COM": "Comissão", "DESENV": "Desenvolvimento", "AGRIC": "Agricultura", "EDUC": "Educação", "SAUDE": "Saúde", "SEG": "Segurança", "PUB": "Pública",
         "INFRA": "Infraestrutura", "CIENC": "Ciência", "TECN": "Tecnologia", "ASSUNTOS": "Assuntos", "REGIONAL": "Regional"}

def coletiva(a):
    """Emendas que não são de um parlamentar: de bancada estadual, de comissão ou do relator-geral do Orçamento.
    Devolve (tipo, chave, nome) ou None."""
    n = norm(a)
    if n.startswith("BANCADA"):
        resto = re.sub(r"^BANCADA (D[OAE]S? )?", "", n).strip()
        uf = UFN.get(resto) or next((v for k, v in sorted(UFN.items(), key=lambda x: -len(x[0])) if resto.startswith(k)), None)
        return ("B", uf or resto, "Bancada federal " + ("(" + uf + ")" if uf else resto.title())) if uf or resto else None
    if n.startswith("COM ") or n.startswith("COMISSAO") or n.startswith("COM."):
        pal = [ABREV.get(w, w.capitalize() if len(w) > 2 else w.lower()) for w in re.sub(r"^COM(ISSAO)? ", "", n).split()]
        nm = " ".join(pal).replace(" Da ", " da ").replace(" De ", " de ").replace(" Do ", " do ").replace(" E ", " e ")
        nm = re.sub(r"^(Da|De|Do|Das|Dos) ", lambda x: x.group(1).lower() + " ", nm)
        nm = re.sub(r"^da ", "de ", nm)
        if not re.match(r"(da|de|do|das|dos) ", nm): nm = "de " + nm
        return ("K", re.sub(r"[^A-Z]", "", n)[:40], "Comissão " + nm)
    if "RELATOR" in n: return ("R", "RG", "Relator-geral do Orçamento")
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
    colet = defaultdict(lambda: [0.0, defaultdict(float), ""])
    for r in rd:
        if len(r) <= max(iA, iF, iU, iM, iV): continue
        ano = re.search(r"(20\d\d)", r[iY] if iY is not None else "")
        if ano and int(ano.group(1)) < 2023: continue
        a = autores.get(norm(r[iA]))
        v = num(r[iV]); uf = (r[iU] or "").strip().upper(); m = norm(r[iM])
        if not v or len(uf) != 2 or not m: continue
        if not a:
            c = coletiva(r[iA])
            if not c:
                semAutor[r[iA].strip()] += v
                if norm(r[iA]) in ("", "SEM INFORMACAO"): continue
                c = ("X", "", " ".join(w.capitalize() if len(w) > 2 else w.lower() for w in r[iA].strip().split()))
            a = (c[0], c[1], c[2], "")
            if c[0] == "X": k = (uf, m, a); tot[k] += v; fav[k][r[iF].strip()] += v; n += 1; continue
            colet[(c[0], c[1])][0] += v; colet[(c[0], c[1])][1][(uf, m)] += v; colet[(c[0], c[1])][2] = c[2]
        if a[0] not in "CS": k = (uf, m, a); tot[k] += v; fav[k][r[iF].strip()] += v; n += 1; continue
        k = (uf, m, a); tot[k] += v; fav[k][r[iF].strip()] += v; porAutor[a[0] + ":" + a[1]] += v; n += 1
    cid = defaultdict(lambda: defaultdict(list))
    for (uf, m, a), v in tot.items():
        top = sorted(fav[(uf, m, a)].items(), key=lambda x: -x[1])[:3]
        cid[uf][m].append([a[0], a[1], a[2], a[3], round(v), [[x, round(y)] for x, y in top]])
    for uf, cs in cid.items():
        for m in cs: cs[m].sort(key=lambda x: -x[4])
        json.dump({"fonte": "Portal da Transparência (CGU) · Emendas parlamentares por favorecido, desde 2023", "cid": cs}, open(OUTD / f"{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump({"fonte": "Portal da Transparência (CGU) · Emendas parlamentares por favorecido, desde 2023",
               "lista": sorted([[t, ch, nm, round(v), [[uf, m, round(x)] for (uf, m), x in sorted(cs.items(), key=lambda y: -y[1])[:15]]]
                                for (t, ch), (v, cs, nm) in colet.items()], key=lambda x: -x[3])},
              open(OUTD / "coletivas.json", "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump({k: round(v) for k, v in porAutor.items()}, open(OUTD / "autores.json", "w"), separators=(",", ":"))
    print("linhas usadas:", n, "UFs:", len(cid), "autores não ligados (maiores):", sorted(semAutor.items(), key=lambda x: -x[1])[:8])
    return {"linhas": n, "ufs": len(cid), "autores": len(porAutor), "cidades": sum(len(c) for c in cid.values()), "coletivas": len(colet), "valor_coletivas": round(sum(x[0] for x in colet.values()))}

if __name__ == "__main__":
    print(json.dumps(main()))
