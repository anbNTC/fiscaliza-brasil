"""Sonda temporária: parâmetros do endpoint de servidores na documentação (Swagger) da API da Paraíba."""
import sys, json, re, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://api.dadosabertos.codata.pb.gov.br"
for u in ["/swagger/doc.json", "/swagger.json", "/openapi.json", "/swagger/v1/swagger.json", "/api/v1/openapi.json", "/swagger/", "/docs/swagger.json"]:
    try:
        r = requests.get(B + u, headers=H, timeout=30)
        print("TRY", u, r.status_code, r.headers.get("content-type"), len(r.text), flush=True)
        if r.ok and "json" in r.headers.get("content-type", ""):
            j = r.json(); ps = j.get("paths", {})
            for k, v in ps.items():
                if "servidor" in k: print("PATH", k, json.dumps(v, ensure_ascii=False)[:1500], flush=True)
            break
        if r.ok: print("REFS", re.findall(r'(?:url|src)\s*[:=]\s*["\']([^"\']+)', r.text)[:10], flush=True)
    except Exception as e: print("TRY", u, "falhou", repr(e)[:80])
