"""Sonda temporária: endereço da especificação no Swagger da Paraíba e parâmetros do endpoint de servidores."""
import sys, json, re, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://api.dadosabertos.codata.pb.gov.br"
t = requests.get(B + "/swagger/", headers=H, timeout=30).text
i = t.find("SwaggerUIBundle"); print("JS", re.sub(r"\s+", " ", t[i:i + 700]), flush=True)
for u in re.findall(r'url[s]?\s*:\s*["\']([^"\']+)["\']', t[i:i + 2000]) + ["/apispec_1.json", "/apispec.json", "/swagger.yaml", "/api/v1/swagger.json"]:
    r = requests.get(u if u.startswith("http") else B + u, headers=H, timeout=30)
    print("TRY", u, r.status_code, len(r.text), flush=True)
    if r.ok and r.text.lstrip()[:1] == "{":
        for k, v in r.json().get("paths", {}).items():
            if "servidor" in k: print("PATH", k, json.dumps([p.get("name") for m in v.values() if isinstance(m, dict) for p in m.get("parameters", [])], ensure_ascii=False), flush=True)
        break
