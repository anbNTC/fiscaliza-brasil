"""Gabinete do prefeito e do vice nas Prefeituras que publicam a folha com nome e lotação em dados abertos (arquivo CSV).
Uma entrada por cidade em PREF abaixo. Cada uma diz onde está o conjunto de dados (CKAN) e como reconhecer o gabinete.
Saída: junta em site/data/gabm/{ue}.json (chaves "p" e "v"), igual às outras fontes de gabinete."""
import csv, io, json, re, sys, time, datetime, unicodedata
from collections import Counter
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gabinetes_elotech import grava

H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
HOJE = datetime.date.today()
PREF = [
    {"cidade": "Belo Horizonte", "uf": "MG", "ue": "41238", "ckan": "https://ckan.pbh.gov.br", "pacote": "relatorio-do-funcionalismo-publico-administracao-direta",
     "pagina": "https://dados.pbh.gov.br/dataset/relatorio-do-funcionalismo-publico-administracao-direta",
     "nome": "NOME", "cargo": "CARGO", "lot": ["ORGAO", "UNIDADE DE LOTACAO"], "valor": "REMUNERACAO TOTAL"},
    # Recife: um arquivo por ano, com a coluna do mês; ficamos com o mês mais recente do arquivo.
    {"cidade": "Recife", "uf": "PE", "ue": "25313", "ckan": "https://dados.recife.pe.gov.br", "pacote": "servidores",
     "pagina": "https://dados.recife.pe.gov.br/dataset/servidores",
     "nome": "nsalsenome", "cargo": "nsalsecarg", "lot": ["esalseunidade", "eslserlotacao"], "valor": "vsalseremu", "liq": "vsalseliqd",
     "ano": "asalseanoo", "mes": "asalsemess"},
]
GABP = re.compile(r"GABINETE\s+DO\s+PREFEITO|GAB\.?\s*(DO\s+)?PREFEITO|VICE[\s-]*PREFEIT", re.I)
num = lambda s: float(re.sub(r"[^\d,.-]", "", str(s or "0")).replace(".", "").replace(",", ".") or 0) if "," in str(s or "") else float(re.sub(r"[^\d.-]", "", str(s or "0")) or 0)
MESES = {m: i + 1 for i, m in enumerate("jan fev mar abr mai jun jul ago set out nov dez".split())}

def get(u, js=True):
    for k in range(4):
        try:
            r = requests.get(u, headers=H, timeout=300)
            if r.ok: return r.json() if js else r.content
            print(u, r.status_code, flush=True)
        except Exception as e: print(u, repr(e)[:120], flush=True)
        time.sleep(6 * (k + 1))

def recente(res):
    """Escolhe o arquivo do mês mais recente pelo nome (ex.: ...-08-2025.csv) ou pela data de criação."""
    def chave(r):
        s = (r.get("name") or "") + " " + (r.get("url") or "")
        m = re.search(r"(\d{2})[-_/](20\d\d)", s) or re.search(r"(20\d\d)[-_/](\d{2})", s)
        if m:
            a, b = m.groups(); return (int(b), int(a)) if len(a) == 2 else (int(a), int(b))
        m = re.search(r"\b(20\d\d)\b", s)
        return (int(m.group(1)), 0) if m else (0, 0)
    cs = [r for r in res if (r.get("format") or "").upper() == "CSV" or (r.get("url") or "").lower().endswith(".csv")]
    return max(cs, key=lambda r: (chave(r), r.get("created") or "")) if cs else None

def uma(c):
    j = get(f'{c["ckan"]}/api/3/action/package_show?id={c["pacote"]}')
    if not j or not j.get("success"): return "conjunto de dados indisponível"
    r = recente(j["result"].get("resources") or [])
    if not r: return "sem arquivo CSV"
    b = get(r["url"], js=False)
    if not b: return "arquivo indisponível"
    txt = b.decode("utf-8-sig") if b[:3] == b"\xef\xbb\xbf" or b"\xc3" in b[:50000] else b.decode("latin-1")
    sep = ";" if txt[:2000].count(";") > txt[:2000].count(",") else ","
    sa = lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().strip().upper()
    rd = csv.DictReader(io.StringIO(txt), delimiter=sep); cols = {sa(k): k for k in (rd.fieldnames or [])}
    col = lambda nome: cols.get(sa(nome))
    out = {"p": [], "v": []}; n = 0; gabs = Counter(); topo = (0, 0)
    per = lambda row: (int(num(row.get(col(c["ano"])))), int(num(row.get(col(c["mes"]))))) if c.get("mes") else (0, 0)
    for row in rd:
        n += 1; pr = per(row); topo = max(topo, pr)
        lot = " · ".join((row.get(col(k)) or "").strip() for k in c["lot"] if col(k))
        if re.search(r"GAB|PREFEIT", lot, re.I): gabs[lot] += 1
        if not GABP.search(lot): continue
        cg = (row.get(col(c["cargo"])) or "").strip()
        if re.match(r"^\s*(VICE[\s-]*)?PREFEIT", cg, re.I): continue
        k = "v" if re.search(r"VICE", lot, re.I) else "p"
        lin = [(row.get(col(c["nome"])) or "").strip().title(), (cg.capitalize() + (" · " + lot.split(" · ")[-1].title() if " · " in lot else "")), "", round(num(row.get(col(c["valor"]))), 2)]
        if c.get("liq"): lin.append(round(num(row.get(col(c["liq"]))), 2))
        out[k].append((pr, lin))
    out = {k: [l for pr, l in v if pr == topo] for k, v in out.items()}
    for v in out.values(): v.sort(key=lambda r: -r[3])
    out = {k: v for k, v in out.items() if v}
    comp = re.search(r"(\d{2})[-_](20\d\d)", r.get("url") or ""); comp = f"{comp.group(1)}/{comp.group(2)}" if comp else ""
    if topo != (0, 0): comp = f"{topo[1]:02d}/{topo[0]}"
    if out:
        grava(c["ue"], {"_tipo": "pref", "dep": out, "fonte": f"Prefeitura de {c['cidade']} · dados abertos (folha dos servidores)", "url": c["pagina"], "competencia": comp,
                        "obs": f"Remuneração {'bruta e líquida' if c.get('liq') else 'total'}{' de ' + comp if comp else ''}, como publicada pela Prefeitura em dados abertos. Só servidores lotados no gabinete do prefeito ou do vice."})
    return {"linhas": n, "gabinete": {k: len(v) for k, v in out.items()}, "arquivo": r.get("name"), "lotacoes_gab": gabs.most_common(12) if not out else []}

def main():
    for c in PREF:
        try: print(c["cidade"], uma(c), flush=True)
        except Exception as e: print(c["cidade"], "falhou:", repr(e)[:200], flush=True)

if __name__ == "__main__":
    main()
