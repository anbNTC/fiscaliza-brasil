"""Votos de cada candidato a deputado federal, deputado estadual e senador em cada cidade (TSE, 2022 e 2026).
Fonte: TSE · Dados Abertos, arquivo "votacao_candidato_munzona_{ano}.zip" (votação nominal por município e zona).
Saída: site/data/vm/{UF}.json
  {"fonte", "url", "gerado", "anos": {"2022": {"F": [cand], "E": [cand], "S": [cand]}, ...},
   "mun": {código TSE da cidade: {"2022": {"F": [[i, votos] x10, total], "E": [...], "S": [...]}}}}
  cand = [nome de urna, nome civil, partido, eleito (1/0), sq_candidato]
Um ano já gravado não é baixado de novo (os resultados não mudam), salvo com REFAZ=1."""
import csv, io, json, os, sys, zipfile, datetime, tempfile
from collections import defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "vm"; OUT.mkdir(exist_ok=True)
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{ano}.zip"
ANOS = [int(a) for a in os.environ.get("ANOS", "2022 2026").split()]
CARGO = {"DEPUTADO FEDERAL": "F", "DEPUTADO ESTADUAL": "E", "DEPUTADO DISTRITAL": "E", "SENADOR": "S"}
TOP = {"F": 10, "E": 10, "S": 5}
ELEITO = {"ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "ELEITO POR MEDIA"}
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}

def baixa(ano):
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with requests.get(URL.format(ano=ano), headers=H, stream=True, timeout=(30, 900)) as r:
        if r.status_code != 200: print(ano, "TSE respondeu", r.status_code, flush=True); return None
        for b in r.iter_content(1 << 20): tmp.write(b)
    tmp.close(); print(ano, "baixado:", round(os.path.getsize(tmp.name) / 1e6), "MB", flush=True); return tmp.name

def um_ano(ano, saida):
    f = baixa(ano)
    if not f: return False
    z = zipfile.ZipFile(f); feitos = 0
    for nm in z.namelist():
        uf = nm.rsplit("_", 1)[-1].split(".")[0].upper()
        if not nm.lower().endswith(".csv") or len(uf) != 2 or uf == "BR" or uf == "ZZ": continue
        cand = {"F": {}, "E": {}, "S": {}}; votos = defaultdict(lambda: defaultdict(int))
        with z.open(nm) as fh:
            for r in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";"):
                c = CARGO.get((r.get("DS_CARGO") or "").upper())
                if not c or r.get("NR_TURNO", "1") != "1": continue
                sq = r["SQ_CANDIDATO"]
                if sq not in cand[c]: cand[c][sq] = [r["NM_URNA_CANDIDATO"], r["NM_CANDIDATO"], r["SG_PARTIDO"], 1 if (r.get("DS_SIT_TOT_TURNO") or "").upper() in ELEITO else 0, sq]
                try: q = int(r["QT_VOTOS_NOMINAIS"])
                except (ValueError, KeyError): q = 0
                votos[(r["CD_MUNICIPIO"], c)][sq] += q
        S = saida.setdefault(uf, {"anos": {}, "mun": {}})
        L = {c: sorted(cand[c].values(), key=lambda x: x[0]) for c in cand}; pos = {c: {x[4]: i for i, x in enumerate(L[c])} for c in L}
        S["anos"][str(ano)] = L
        for (mun, c), vs in votos.items():
            top = sorted(vs.items(), key=lambda x: -x[1])[:TOP[c]]
            S["mun"].setdefault(mun, {}).setdefault(str(ano), {})[c] = [[[pos[c][sq], v] for sq, v in top], sum(vs.values())]
        feitos += 1
    os.unlink(f); print(ano, feitos, "estados", flush=True); return feitos > 0

def main():
    saida = {}
    for f in OUT.glob("*.json"):
        try: x = json.load(open(f)); saida[f.stem] = {"anos": x["anos"], "mun": x["mun"]}
        except Exception: pass
    feito = {a for a in ANOS if saida and all(str(a) in s["anos"] for s in saida.values())}
    for a in ANOS:
        if a in feito and os.environ.get("REFAZ") != "1": print(a, "já gravado"); continue
        # o ano novo substitui o antigo só se vier inteiro
        for s in saida.values():
            s["anos"].pop(str(a), None)
            for m in s["mun"].values(): m.pop(str(a), None)
        try: um_ano(a, saida)
        except Exception as e: print(a, "falhou:", repr(e), flush=True)
    for uf, s in saida.items():
        out = {"fonte": "TSE · Dados Abertos, votação nominal por município e zona (1º turno)", "url": "https://dadosabertos.tse.jus.br/dataset/?tags=Resultados",
               "gerado": datetime.date.today().isoformat(), "anos": s["anos"], "mun": s["mun"]}
        json.dump(out, open(OUT / f"{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({uf: {"anos": sorted(s["anos"]), "cidades": len(s["mun"]), "kb": round((OUT / f"{uf}.json").stat().st_size / 1024)} for uf, s in sorted(saida.items())}))

if __name__ == "__main__":
    main()
