"""Verba de gabinete de cada deputado federal: quanto do limite mensal foi usado para pagar os secretários parlamentares.
Fonte: página oficial de cada deputado na Câmara (www.camara.leg.br/deputados/{id}?ano=AAAA), quadro "Verba de gabinete".
Saída: site/data/gab/verba.json {"limite": valor mensal atual, "fonte", "gerado", "dep": {id: {ano: [[mês, valor gasto, % do limite]...]}}}
Anos passados ficam gravados; o ano corrente é refeito a cada coleta (ANOS_REFAZ)."""
import json, re, sys, time, html, datetime, os
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "gab"; OUT.mkdir(exist_ok=True); ARQ = OUT / "verba.json"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
HOJE = datetime.date.today(); ANOS = range(2023, HOJE.year + 1)
REFAZ = {int(a) for a in os.environ.get("ANOS_REFAZ", str(HOJE.year)).split()}
MES = {m: i + 1 for i, m in enumerate("JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split())}
num = lambda s: float(s.replace(".", "").replace(",", ".")) if re.match(r"^[\d.]+,\d+$", s.strip()) else None
S = requests.Session(); S.headers.update(H)

def tabela(t, rotulo):
    m = re.search(r'aria-label="' + rotulo + r'"[\s\S]*?</table>', t)
    if not m: return []
    return [[re.sub(r"<[^>]+>", "", html.unescape(c)).strip() for c in re.findall(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", tr)] for tr in re.findall(r"<tr[\s\S]*?</tr>", m.group(0))]

def extras(t):
    """Imóvel funcional, auxílio-moradia e nº de viagens em missão oficial (quadro "Benefícios" da página do deputado)."""
    txt = lambda m: " ".join(re.sub(r"<[^>]+>", " ", html.unescape(m.group(1))).split()) if m else ""
    im = txt(re.search(r'Imóvel funcional.*?</h3>\s*<span[^>]*>(.*?)</span>', t, re.S))
    au = txt(re.search(r'Auxílio-moradia.*?</h3>\s*(.*?)</div>', t, re.S))
    vg = re.search(r'Viagens em missão oficial.*?</h3>\s*<(?:a|span)[^>]*>\s*(\d+)\s*<', t, re.S)
    return {"imovel": im, "auxilio": au[:160], "viagens": int(vg.group(1)) if vg else None}

def presenca(t):
    """Presença em Plenário no ano da página: [presenças, ausências justificadas, ausências não justificadas] (em dias)."""
    m = re.search(r'presenca-plenario/\d{4}"[\s\S]*?</section>', t)
    if not m: return None
    v = [int(x) for x in re.findall(r'presencas__qtd">\s*(\d+)\s*dias?', m.group(0))]
    return v[:3] if len(v) >= 3 else None

def missoes(idd):
    """Viagens em missão oficial: período, assunto, destino, passagens e diárias (página pública de cada deputado)."""
    for k in range(3):
        try:
            r = S.get(f"https://www.camara.leg.br/deputados/{idd}/missao-oficial", timeout=60)
            if r.ok: break
        except Exception: pass
        time.sleep(4 * (k + 1))
    else: return None
    out = []
    for tr in re.findall(r"<tr>\s*<td>[\s\S]*?</tr>", r.text):
        c = [" ".join(re.sub(r"<[^>]+>", " ", html.unescape(x)).split()) for x in re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr)]
        cod = re.search(r"codViagem(?:=|&#x3D;)(\d+)", tr)
        if len(c) >= 5: out.append([cod.group(1) if cod else c[0], c[0], c[1][:200], c[2].strip(" ,"), num(c[3]) or 0, num(c[4]) or 0])
    return out

def um(idd, ano, html_out=None):
    for k in range(3):
        try:
            r = S.get(f"https://www.camara.leg.br/deputados/{idd}?ano={ano}", timeout=60)
            if r.status_code == 404: return None, None
            if r.ok: break
        except Exception: pass
        time.sleep(4 * (k + 1))
    else: return None, None
    t = r.text
    if html_out is not None: html_out.append(t)
    lim = re.search(r"limite mensal de R\$ ([\d.]+,\d\d) para pagar", t)
    meses = []
    for row in tabela(t, "Gasto mensal da verba de gabinete"):
        if len(row) >= 2 and row[0][:3].upper() in MES and num(row[1]) is not None:
            meses.append([MES[row[0][:3].upper()], round(num(row[1]), 2), float(row[2].replace("%", "").replace(",", ".")) if len(row) > 2 and re.match(r"^[\d.,]+%?$", row[2]) else None])
    return meses, (num(lim.group(1)) if lim else None)

def main():
    BR = json.load(open(D / "br.json")); ids = [d[0] for d in BR["dep"]]
    try: X = json.load(open(ARQ))
    except Exception: X = {"dep": {}}
    lim = X.get("limite"); n = 0; vazios = 0
    VG = D / "gab" / "viagens.json"; PA = D / "gab" / "presenca.json"
    try: PR = json.load(open(PA))["dep"]
    except Exception: PR = {}
    try: Y = json.load(open(VG))
    except Exception: Y = {"dep": {}}
    for idd in ids:
        reg = X["dep"].setdefault(str(idd), {})
        for ano in ANOS:
            if str(ano) in reg and ano not in REFAZ:
                if str(ano) not in PR.get(str(idd), {}):
                    pag = []; um(idd, ano, pag); time.sleep(0.4)
                    pr = presenca(pag[0]) if pag else None
                    if pr: PR.setdefault(str(idd), {})[str(ano)] = pr
                continue
            pag = []; m, l = um(idd, ano, pag); time.sleep(0.4)
            if pag:
                pr = presenca(pag[0])
                if pr: PR.setdefault(str(idd), {})[str(ano)] = pr
            if pag and ano == HOJE.year:
                ex = extras(pag[0]); y = Y["dep"].setdefault(str(idd), {"v": []}); y.update({"imovel": ex["imovel"], "auxilio": ex["auxilio"]})
                if ex["viagens"]:
                    ms = missoes(idd); time.sleep(0.4)
                    if ms:
                        vis = {v[0] for v in y["v"]}; y["v"] += [v for v in ms if v[0] not in vis]
                        y["v"].sort(key=lambda v: "-".join(reversed(v[1][:10].split("/"))), reverse=True)
            if m is None: continue
            if l: lim = l
            if m: reg[str(ano)] = m; n += 1
            else: vazios += 1
    X.update({"limite": lim, "fonte": "Câmara dos Deputados · página oficial de cada deputado (verba de gabinete)", "url": "https://www.camara.leg.br/deputados/quem-sao", "gerado": HOJE.isoformat()})
    X["dep"] = {k: v for k, v in X["dep"].items() if v}
    if n == 0 and not X["dep"]: raise RuntimeError("nenhuma verba de gabinete lida: a página pode ter mudado")
    json.dump(X, open(ARQ, "w"), ensure_ascii=False, separators=(",", ":"))
    Y.update({"fonte": "Câmara dos Deputados · página oficial de cada deputado (benefícios e viagens em missão oficial)", "gerado": HOJE.isoformat()})
    json.dump(Y, open(VG, "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump({"fonte": "Câmara dos Deputados · página oficial de cada deputado (presença em Plenário)", "gerado": HOJE.isoformat(), "dep": PR}, open(PA, "w"), ensure_ascii=False, separators=(",", ":"))
    # presença nas sessões (desde 2023, somando os anos) vai para a ficha de cada deputado: sess = [dias presente, dias com sessão deliberativa]
    porUF = {}
    for d in BR["dep"]: porUF.setdefault(d[3], []).append(str(d[0]))
    atual = 0
    for uf, L in porUF.items():
        f = D / "c" / f"{uf}.json"
        try: C = json.load(open(f))
        except Exception: continue
        for k in L:
            a = PR.get(k)
            if not a or k not in C: continue
            p = sum(v[0] for v in a.values()); tot = sum(sum(v) for v in a.values())
            if tot: C[k]["sess"] = [p, tot]; atual += 1
        json.dump(C, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
    print("presença atualizada:", atual)
    print(json.dumps({"deputados": len(X["dep"]), "anos_lidos": n, "sem_dado": vazios, "limite": lim}))

if __name__ == "__main__":
    if len(sys.argv) > 1:  # teste: python camara_verba_gabinete.py 220683
        pg = []; print(um(sys.argv[1], HOJE.year, pg)); print(extras(pg[0])); print(missoes(sys.argv[1]))
    else: main()
