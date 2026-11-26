"""Sonda temporária: emendas estaduais de Alagoas (portal da transparência) e outros estados."""
import sys, re, html, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
def pg(u):
    try:
        r = requests.get(u, headers=H, timeout=40)
        if r.ok: return r
    except Exception: pass
    return gbr(u, headers=H, timeout=60)
r = pg("https://transparencia.al.gov.br/despesa/emendas-parlamentares-estaduais/")
t = html.unescape(r.text if r is not None else "")
print("AL", r.status_code if r is not None else None, len(t), flush=True)
print("ALLINKS", sorted(set(re.findall(r'(?:href|data-url|action)="([^"]*(?:csv|json|export|ajax|api|emenda)[^"]*)"', t, re.I)))[:25], flush=True)
print("ALJS", sorted(set(re.findall(r'["\'](/[\w/-]*(?:json|ajax|api|lista|dados)[\w/?=&.-]*)["\']', t)))[:25], flush=True)
print("ALTXT", re.sub(r"\s+", " ", re.sub(r"<(script|style)[\s\S]*?</\1>|<[^>]+>", " ", t))[:1500], flush=True)
