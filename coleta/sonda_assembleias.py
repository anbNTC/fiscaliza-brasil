"""Sonda 8: chama /api/sonda-br a partir do runner do GitHub (EUA) para ver em que data center a Cloudflare roda e se ainda alcança as Assembleias."""
import json, requests
from pathlib import Path
O = Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda"; O.mkdir(parents=True, exist_ok=True)
r = requests.get("https://fiscalizaja.pages.dev/api/sonda-br", timeout=120)
j = r.json(); print(json.dumps({"local": j.get("local"), "pais": j.get("pais"), "R": [{"u": x["u"], "st": x.get("st"), "erro": x.get("erro")} for x in j["R"]]}, indent=1))
(O / "sonda8.json").write_text(json.dumps(j, ensure_ascii=False, indent=1))
