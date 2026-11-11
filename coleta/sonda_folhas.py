"""Sonda temporária: abre o arquivo mais recente da folha em cada portal e mostra colunas e lotações de gabinete."""
import csv, io, re, sys, requests
from collections import Counter, defaultdict
sys.path.insert(0, "coleta")
from prefeituras_abertas import recente
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
ALVOS = [("https://dados.recife.pe.gov.br", "servidores"), ("https://dadosabertos.poa.br", "folha-de-pagamento-servidores-ativos"),
         ("https://dados.fortaleza.ce.gov.br", "servidores-pmf"), ("https://dados.mg.gov.br", "remuneracao-servidores-ativos"),
         ("https://dados.pe.gov.br", "remuneracao-de-servidores"), ("https://dados.sc.gov.br", "remuneracao-servidores"),
         ("https://dados.ro.gov.br", "servidores"), ("https://dados.pb.gov.br", "remuneracao-servidores")]
RX = re.compile(r"GABINETE|GOVERNADOR|PREFEITO|GAB\.", re.I)
for h, p in ALVOS:
    print("\n########", h, p, flush=True)
    try:
        j = requests.get(f"{h}/api/3/action/package_show", params={"id": p}, headers=H, timeout=60).json()["result"]
        res = j.get("resources") or []
        print("recursos:", len(res), "| últimos:", [(r.get("name"), r.get("format")) for r in res[-4:]])
        r = recente([x for x in res if not re.search(r"inativ|pension|estagi", (x.get("name") or "") + (x.get("url") or ""), re.I)]) or (res and res[-1])
        if not r: continue
        print("arquivo:", r.get("name"), r.get("url"), flush=True)
        resp = requests.get(r["url"], headers=H, timeout=300, stream=True)
        buf = b""
        for ch in resp.iter_content(1 << 20):
            buf += ch
            if len(buf) > 300 << 20: break
        print("bytes lidos:", len(buf), "| tipo:", resp.headers.get("content-type"))
        if buf[:2] == b"PK": print("ZIP/XLSX: precisa abrir"); continue
        txt = buf.decode("utf-8-sig", "ignore") if b"\xc3" in buf[:200000] else buf.decode("latin-1")
        if txt.lstrip()[:1] in "[{": print("JSON:", txt[:600]); continue
        sep = ";" if txt[:3000].count(";") > txt[:3000].count(",") else ","
        rd = csv.reader(io.StringIO(txt[: txt.rfind("\n")]), delimiter=sep)
        cab = next(rd); print("colunas:", cab)
        vals = defaultdict(Counter); n = 0; ex = None
        for row in rd:
            n += 1
            for i, v in enumerate(row):
                if i < len(cab) and RX.search(v) and len(v) < 120: vals[cab[i]][v.strip()] += 1
            if ex is None and any(RX.search(v) for v in row): ex = row
        print("linhas:", n)
        for c, cnt in vals.items(): print("  coluna", c, "→", cnt.most_common(15))
        print("  exemplo:", ex)
    except Exception as e:
        print("ERRO", repr(e)[:200])
    sys.stdout.flush()
