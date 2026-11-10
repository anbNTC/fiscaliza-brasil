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

def um(idd, ano):
    for k in range(3):
        try:
            r = S.get(f"https://www.camara.leg.br/deputados/{idd}?ano={ano}", timeout=60)
            if r.status_code == 404: return None, None
            if r.ok: break
        except Exception: pass
        time.sleep(4 * (k + 1))
    else: return None, None
    t = r.text; lim = re.search(r"limite mensal de R\$ ([\d.]+,\d\d) para pagar", t)
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
    for idd in ids:
        reg = X["dep"].setdefault(str(idd), {})
        for ano in ANOS:
            if str(ano) in reg and ano not in REFAZ: continue
            m, l = um(idd, ano); time.sleep(0.4)
            if m is None: continue
            if l: lim = l
            if m: reg[str(ano)] = m; n += 1
            else: vazios += 1
    X.update({"limite": lim, "fonte": "Câmara dos Deputados · página oficial de cada deputado (verba de gabinete)", "url": "https://www.camara.leg.br/deputados/quem-sao", "gerado": HOJE.isoformat()})
    X["dep"] = {k: v for k, v in X["dep"].items() if v}
    if n == 0 and not X["dep"]: raise RuntimeError("nenhuma verba de gabinete lida: a página pode ter mudado")
    json.dump(X, open(ARQ, "w"), ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({"deputados": len(X["dep"]), "anos_lidos": n, "sem_dado": vazios, "limite": lim}))

if __name__ == "__main__":
    if len(sys.argv) > 1:  # teste: python camara_verba_gabinete.py 220683
        for a in ANOS: print(a, um(sys.argv[1], a))
    else: main()
