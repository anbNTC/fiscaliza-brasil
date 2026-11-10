"""Procura portais de transparência Elotech (eloweb.net) das cidades brasileiras e quais têm a entidade Câmara Municipal.
Tenta, para cada cidade, endereços no padrão usado pela Elotech (cm + nome, camara + nome, nome). Imprime a lista em JSON
para colar em coleta/elotech_portais.json."""
import json, re, unicodedata, concurrent.futures as cf
from pathlib import Path
import requests
D = Path(__file__).resolve().parents[1] / "site" / "data"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
slug = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())

def testa(host):
    try:
        r = requests.get(f"https://{host}/portaltransparencia-api/api/entidades/", headers=H, timeout=12)
        if r.ok and r.text.startswith("["):
            return [{"id": e.get("id"), "nome": e.get("nome"), "tipo": e.get("tipo"), "cidade": e.get("cidade"), "uf": e.get("uf")} for e in r.json()]
    except Exception: pass

def main():
    alvos = []
    for f in sorted((D / "uf").glob("*.json")):
        uf = f.stem
        for ue, m in (json.load(open(f)).get("mun") or {}).items():
            s = slug(m[0])
            for h in (f"cm{s}", f"camara{s}", f"cm{s}{uf.lower()}", s, f"pm{s}"):
                alvos.append((h + ".eloweb.net", uf, ue, m[0]))
    print(len(alvos), "endereços a testar", flush=True)
    achou = {}
    with cf.ThreadPoolExecutor(48) as ex:
        fut = {ex.submit(testa, a[0]): a for a in alvos}
        for f in cf.as_completed(fut):
            r = f.result(); host, uf, ue, nome = fut[f]
            if not r: continue
            cam = [e for e in r if (e.get("tipo") == "L" or "CAMARA" in (e.get("nome") or "").upper())]
            # a Câmara tem de ser desta cidade (há cidades com o mesmo nome em outros estados)
            cam = [e for e in cam if (e.get("uf") or "").upper() == uf and slug(e.get("cidade") or "") == slug(nome)]
            if cam: achou[host] = {"host": host, "uf": uf, "ue": ue, "cidade": nome, "ent": cam[0]["id"]}
    # um portal por cidade (prefere o da Câmara)
    por = {}
    for h, x in sorted(achou.items()):
        if x["ue"] not in por or h.startswith("cm"): por[x["ue"]] = x
    print("ACHADOS", len(por))
    for x in sorted(por.values(), key=lambda z: (z["uf"], z["cidade"])): print("PORTAL " + json.dumps({"host": x["host"], "uf": x["uf"], "ue": x["ue"], "cidade": x["cidade"], "ent": x["ent"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
