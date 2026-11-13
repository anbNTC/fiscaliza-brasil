"""Sonda temporária: onde a ALEP publica o e-mail de cada gabinete (página conheca e perfil). Só contagens, sem imprimir endereços."""
import re, sys, html, time, requests
sys.path.insert(0, "tools"); sys.path.insert(0, "coleta")
from convite_parlamentares import UA, EMAIL, GENERICO
S = requests.Session(); S.headers.update(UA)
t = html.unescape(S.get("https://www.assembleia.pr.leg.br/deputados/conheca", timeout=60).text)
ems = list(dict.fromkeys(EMAIL.findall(t)))
print("CONHECA emails:", len(ems), "| genericos:", sum(1 for e in ems if GENERICO.search(e)), "| mailto:", t.count("mailto:"), flush=True)
print("CONHECA formatos:", sorted({re.sub(r"[a-z]", "x", e.split("@")[0])[:3] + "...@" + e.split("@")[1] for e in ems})[:10], flush=True)
for sl in ["alexandre-amaro", "goura"]:
    p = html.unescape(S.get(f"https://www.assembleia.pr.leg.br/deputados/perfil/{sl}", timeout=60).text); time.sleep(1)
    print("PERFIL", sl, "emails:", len(set(EMAIL.findall(p))), "| palavras:", [w for w in ("gabinete", "e-mail", "email", "telefone", "contato") if w in p.lower()], "| links:", sorted(set(re.findall(r'href="(/[^"]*(?:contato|gabinete)[^"]*)"', p)))[:5], flush=True)
