"""Sonda 3: amostra completa de cada endpoint do SAPL (para escrever o coletor)."""
import json
from pathlib import Path
import requests
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0)", "accept": "application/json"}
b = "https://sapl.al.pb.leg.br/api"
E = ["parlamentares/parlamentar/?page_size=1&ativo=True", "parlamentares/filiacao/?page_size=1", "parlamentares/mandato/?page_size=1", "parlamentares/legislatura/?page_size=1",
     "materia/materialegislativa/?page_size=1&ano=2025", "materia/autoria/?page_size=1", "base/autor/?page_size=1&tipo=1", "materia/tipomaterialegislativa/?page_size=50",
     "sessao/votoparlamentar/?page_size=1", "sessao/registrovotacao/?page_size=1", "sessao/sessaoplenaria/?page_size=1", "sessao/ordemdia/?page_size=1", "parlamentares/partido/?page_size=1",
     "materia/materialegislativa/?page_size=1&ano=2025&o=-data_apresentacao", "sessao/votoparlamentar/?page_size=1&o=-id", "sessao/registrovotacao/?page_size=1&o=-id"]
R = {}
for e in E:
    try: R[e] = requests.get(f"{b}/{e}", headers=H, timeout=25).json()
    except Exception as x: R[e] = str(x)
json.dump(R, open(Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda_assembleias.json", "w"), ensure_ascii=False, indent=1)
