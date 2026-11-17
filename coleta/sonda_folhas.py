"""Sonda temporária: folha do Ceará (CSV mensal no Ceará Transparente) e relação de servidores de Curitiba (dados abertos)."""
import sys, io, csv, re, requests, collections, datetime
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, texto
from saida_br import get as gbr
hoje = datetime.date.today()
for k in range(1, 6):
    am = f"{(hoje.year * 12 + hoje.month - 1 - k) // 12}{(hoje.year * 12 + hoje.month - 1 - k) % 12 + 1:02d}"
    u = f"https://cearatransparente.ce.gov.br/files/downloads/integration/servers/server_salaries/{am}/servidores_{am}.csv"
    for via, f in (("direto", lambda u: requests.get(u, headers={**H, "Range": "bytes=0-300000"}, timeout=60)), ("br", lambda u: gbr(u, headers={**H, "Range": "bytes=0-300000"}, timeout=90))):
        try:
            r = f(u); print("CE", am, via, r.status_code if r is not None else None, len(r.content) if r is not None else 0, flush=True)
            if r is not None and r.ok and len(r.content) > 1000:
                t = texto(r.content); sep = ";" if t[:3000].count(";") > t[:3000].count(",") else ","
                rows = list(csv.DictReader(io.StringIO(t.rsplit("\n", 1)[0]), delimiter=sep)); print("CECOLS", list(rows[0].keys()), flush=True); print("CEROW", rows[0], flush=True)
                for c in rows[0]:
                    if re.search(r"orgao|órgão|lota|unidade|setor", c, re.I): print("CETOP", c, collections.Counter(x[c] for x in rows).most_common(5), flush=True)
                raise StopIteration
        except StopIteration: break
        except Exception as e: print("CE", am, via, "falhou", repr(e)[:120], flush=True)
    else: continue
    break
for u in ["https://dadosabertos.curitiba.pr.gov.br/", "https://dadosabertos.curitiba.pr.gov.br/conjuntodado/"]:
    for via, f in (("direto", lambda u: requests.get(u, headers=H, timeout=40)), ("br", lambda u: gbr(u, headers=H, timeout=60))):
        try:
            r = f(u); t = r.text if r is not None else ""
            print("CWB", u, via, r.status_code if r is not None else None, len(t), sorted(set(re.findall(r'href="([^"]*(?:servidor|Servidor|cargo|pessoal|folha)[^"]*)"', t)))[:15], flush=True)
            if t: break
        except Exception as e: print("CWB", u, via, "falhou", repr(e)[:100], flush=True)
