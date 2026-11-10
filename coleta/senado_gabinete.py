"""Quem trabalha no gabinete de cada senador e quanto recebeu no último mês publicado (Senado Federal · Dados Abertos Administrativos).
Fontes: adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/servidores/ativos (lotação de cada servidor)
        adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/remuneracoes/{ano}/{mes} (remuneração nominal, folha normal)
Saída: site/data/gab/senado.json {"mes": "AAAA-MM", "dep": {id do senador: [[nome, cargo, ano de admissão, bruto, líquido, lotação]]}}
Lotações ligadas ao senador: "Gabinete do Senador X" e os escritórios de apoio no estado, quando o nome do senador aparece na lotação."""
import json, re, time, datetime, unicodedata
from collections import defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "gab"; OUT.mkdir(exist_ok=True)
API = "https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^A-Z ]", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper())).strip()
num = lambda s: float(str(s or "0").replace(".", "").replace(",", ".") or 0)

def get(u):
    for k in range(4):
        try:
            r = requests.get(u, headers=H, timeout=180)
            if r.ok: return r.json()
            if r.status_code == 404: return None
        except Exception as e: print(u, repr(e)[:100], flush=True)
        time.sleep(5 * (k + 1))

def main():
    A = get(f"{API}/servidores/ativos") or []
    if len(A) < 3000: raise RuntimeError(f"lista de servidores do Senado incompleta ({len(A)})")
    hoje = datetime.date.today(); R = None; mes = None
    for k in range(1, 5):  # último mês com folha publicada
        d = (hoje.replace(day=1) - datetime.timedelta(days=28 * k)); R = get(f"{API}/remuneracoes/{d.year}/{d.month}")
        if R: mes = f"{d.year}-{d.month:02d}"; break
    pag = defaultdict(lambda: [0.0, 0.0])
    for x in R or []:
        if (x.get("tipo_folha") or "").lower() != "normal": continue
        p = pag[norm(x["nome"])]
        p[0] += num(x.get("remuneracao_basica")) + num(x.get("vantagens_pessoais")) + num(x.get("funcao_comissionada")) + num(x.get("outras_eventuais"))
        p[1] += num(x.get("remuneracao_liquida"))
    BR = json.load(open(D / "br.json"))
    sen = [(str(s[0]), norm(s[1]), norm(s[2])) for s in BR["sen"]]
    def dono(lot):
        n = norm(lot)
        if not re.search(r"GABINETE D[OA] SENADOR|ESCRITORIO", n): return None
        nome = re.sub(r"^.*?SENADOR[A]? ", "", n)
        for sid, a, b in sen:
            if nome and (nome == a or nome in a or a in nome or nome in b): return sid
    out = defaultdict(list); semdono = defaultdict(int)
    for x in A:
        lot = (x.get("lotacao") or {}).get("nome") or ""
        if x.get("vinculo") == "PARLAMENTAR": continue
        sid = dono(lot)
        if not sid:
            if re.search("SENADOR", norm(lot)): semdono[lot] += 1
            continue
        p = pag.get(norm(x["nome"]))
        cargo = ((x.get("funcao") or {}).get("nome") or (x.get("cargo") or {}).get("nome") or "").title()
        out[sid].append([x["nome"].title(), cargo, x.get("ano_admissao"), round(p[0], 2) if p else None, round(p[1], 2) if p else None, lot])
    for v in out.values(): v.sort(key=lambda r: -(r[3] or 0))
    json.dump({"fonte": "Senado Federal · Dados Abertos Administrativos (servidores ativos e remuneração nominal)", "url": "https://www12.senado.leg.br/dados-abertos/conjuntos?portal=Administrativo&grupo=gestao-de-pessoas",
               "gerado": hoje.isoformat(), "mes": mes, "dep": out}, open(OUT / "senado.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({"senadores": len(out), "pessoas": sum(len(v) for v in out.values()), "com_salario": sum(1 for v in out.values() for r in v if r[3]), "mes": mes,
                      "lotacoes_sem_dono": sorted(semdono.items(), key=lambda z: -z[1])[:8]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
