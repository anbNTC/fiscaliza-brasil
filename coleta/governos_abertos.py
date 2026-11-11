"""Gabinete do governador e do vice nos estados que publicam a folha dos servidores com nome e lotação em dados abertos (CSV mensal).
Uma entrada por estado em GOV abaixo: onde está o conjunto de dados (CKAN) e como reconhecer quem trabalha com o governador e com o vice.
A equipe vai para a ficha de quem ocupa o cargo hoje (achado pelo nome do próprio governador ou vice na folha), por isso funciona
mesmo quando o vice assumiu o governo (ex.: Minas Gerais em 2026).
Saída: site/data/gabg/{UF}.json com {"dep": {"0": [...], "1": [...]}} (0 = cabeça da chapa eleita em 2022, 1 = vice da chapa)."""
import csv, io, json, re, sys, datetime, unicodedata
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from prefeituras_abertas import recente, baixa, num, H, texto, get

D = Path(__file__).resolve().parents[1] / "site" / "data"
sa = lambda x: unicodedata.normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().upper().strip()
GOV = [
    {"uf": "MG", "ckan": "https://dados.mg.gov.br", "pacote": "remuneracao-servidores-ativos", "pagina": "https://dados.mg.gov.br/dataset/remuneracao-servidores-ativos",
     "fonte": "Governo de Minas Gerais · dados abertos (remuneração dos servidores do Executivo)",
     "nome": "nome", "cargo": ["cargo_comissao", "cargo_efetivo"], "orgao": "orgao_exercicio", "unid": "unidade_exercicio", "bruto": "remuneracao", "liq": "remuneracao_liquida",
     "gov": r"^GOVERNADORIA$", "vice": r"VICE-?GOVERNADOR"},
    {"uf": "SC", "ckan": "https://dados.sc.gov.br", "pacote": "remuneracao-servidores", "pagina": "https://dados.sc.gov.br/dataset/remuneracao-servidores",
     "fonte": "Governo de Santa Catarina · dados abertos (remuneração dos servidores)",
     "nome": "Nome", "cargo": ["Cargo"], "orgao": "OrgaoExercicio", "unid": "UnidadeExercicio", "bruto": "ValorBruto", "liq": None,
     "gov": r"GABINETE DO GOVERNADOR", "vice": r"GABINETE DO VICE-?GOVERNADOR"},
    {"uf": "PE", "ckan": "https://dados.pe.gov.br", "pacote": "remuneracao-de-servidores", "pagina": "https://dados.pe.gov.br/dataset/remuneracao-de-servidores", "br": True,
     "fonte": "Governo de Pernambuco · dados abertos (remuneração dos servidores)",
     "nome": "r_nome", "cargo": ["r_funcao", "r_cargo"], "orgao": "r_instituicao", "unid": None, "bruto": "r_total_vantagens", "liq": "*liquid",
     "gov": r"^GOVERNADORIA DO ESTADO$", "vice": r"^VICE-?GOVERNADORIA"},
]
CHEFE = re.compile(r"^(VICE[- ]?)?GOVERNADOR(A)?( DO ESTADO)?$")

def um(c, BR):
    j = get(f'{c["ckan"]}/api/3/action/package_show?id={c["pacote"]}', br=c.get("br"))
    r = recente([x for x in j["result"]["resources"] if not re.search(r"inativ|pension|estagi", (x.get("name") or "") + (x.get("url") or ""), re.I)])
    if not r: return "sem arquivo"
    b = baixa(r["url"], c.get("br"))
    if not b: return "arquivo indisponível"
    t = texto(b); del b
    sep = ";" if t[:3000].count(";") > t[:3000].count(",") else ","
    rd = csv.DictReader(io.StringIO(t), delimiter=sep)
    if c.get("liq", "") and c["liq"].startswith("*"): c = dict(c, liq=next((k for k in rd.fieldnames or [] if c["liq"][1:] in k.lower()), None))
    equipe = {"gov": [], "vice": []}; chefes = {}; comp = ""
    for row in rd:
        o = sa(row.get(c["orgao"])); u = sa(row.get(c["unid"])) if c.get("unid") else ""; cg = " / ".join(x for x in (sa(row.get(k)) for k in c["cargo"]) if x)
        if not comp: comp = row.get("mes_ano") or ""
        if any(CHEFE.search(x) for x in cg.split(" / ")): chefes["vice" if re.search(r"(^| / )VICE", cg) else "gov"] = sa(row.get(c["nome"])); continue
        lugar = o + " | " + u
        k = "vice" if re.search(c["vice"], lugar) else "gov" if re.search(c["gov"], u) or re.search(c["gov"], o) else None
        if not k: continue
        cargo = (cg.split(" / ")[0] or "").capitalize()
        lin = [sa(row.get(c["nome"])).title(), cargo + (" · " + u.title() if u else ""), "", round(num(row.get(c["bruto"])), 2)]
        if c.get("liq"): lin.append(round(num(row.get(c["liq"])), 2))
        equipe[k].append(lin)
    # de quem é cada equipe: procura o nome do governador/vice da folha na chapa eleita em 2022
    chapa = BR["ufs"][c["uf"]]["gov"]; dep = {}
    for k, idx0 in (("gov", "0"), ("vice", "1")):
        if not equipe[k]: continue
        idx = idx0
        if chefes.get(k):
            for i, P in enumerate(chapa):
                if sa(P[1]) == chefes[k] or sa(P[0]) in chefes[k]: idx = str(i)
        dep[idx] = sorted(equipe[k], key=lambda x: -x[3])
    m = re.search(r"(20\d\d)[-_](\d\d)", r.get("url") or "") or re.search(r"(\d\d)/(20\d\d)", comp)
    competencia = (f"{m.group(2)}/{m.group(1)}" if m.group(1).startswith("20") else f"{m.group(1)}/{m.group(2)}") if m else comp
    obs = (f"Remuneração bruta{' e líquida' if c.get('liq') else ''} de {competencia}, como publicada pelo governo do estado em dados abertos. "
           "Só servidores lotados na unidade do governador ou no gabinete do vice; não inclui as secretarias.")
    if chefes.get("gov") and dep and "0" not in dep and any(sa(P[1]) == chefes["gov"] for P in chapa[1:]):
        obs += " O vice eleito em 2022 assumiu o governo; a equipe do governador aparece na ficha dele."
    if dep:
        json.dump({"fonte": c["fonte"], "url": c["pagina"], "competencia": competencia, "gerado": datetime.date.today().isoformat(), "obs": obs, "dep": dep},
                  open(D / "gabg" / f"{c['uf']}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return {"arquivo": r.get("name"), "chefes": chefes, "equipes": {k: len(v) for k, v in dep.items()}}

def main():
    (D / "gabg").mkdir(exist_ok=True); BR = json.load(open(D / "br.json"))
    for c in GOV:
        try: print(c["uf"], um(c, BR), flush=True)
        except Exception as e: print(c["uf"], "falhou:", repr(e)[:200], flush=True)

if __name__ == "__main__":
    main()
