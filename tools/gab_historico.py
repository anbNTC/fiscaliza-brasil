"""Histórico dos gabinetes: a cada coleta, compara quem está em cada gabinete com a coleta anterior e anota quem entrou e quem saiu.
Fontes já coletadas: gab/{UF}.json (Câmara), gab/senado.json (Senado) e gabm/{ue}.json (vereadores, portais Elotech).
Saída: site/data/gab/hist/{chave}.json {"desde": primeira data registrada, "ult": {político: [nomes]}, "ev": {político: [[data, "+"|"-", nome, cargo]]}}
A primeira coleta só grava a situação inicial (sem eventos)."""
import json, datetime
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "site" / "data"; H = D / "gab" / "hist"; H.mkdir(parents=True, exist_ok=True)
HOJE = datetime.date.today().isoformat(); MAX = 300

def fontes():
    for f in sorted((D / "gab").glob("??.json")): yield "c" + f.stem, json.load(open(f)).get("dep") or {}
    if (D / "gab" / "senado.json").exists(): yield "senado", json.load(open(D / "gab" / "senado.json")).get("dep") or {}
    for f in sorted((D / "gabm").glob("*.json")): yield "m" + f.stem, json.load(open(f)).get("dep") or {}

def main():
    tot = 0
    for chave, dep in fontes():
        p = H / f"{chave}.json"
        try: X = json.load(open(p))
        except Exception: X = {"desde": HOJE, "ult": {}, "ev": {}}
        for k, rows in dep.items():
            agora = {r[0]: (r[1] if len(r) > 1 else "") for r in rows}
            antes = set(X["ult"].get(k, [])) if k in X["ult"] else None
            if antes is not None:
                ev = X["ev"].setdefault(k, [])
                for n in sorted(set(agora) - antes): ev.append([HOJE, "+", n, agora[n]]); tot += 1
                for n in sorted(antes - set(agora)): ev.append([HOJE, "-", n, ""]); tot += 1
                X["ev"][k] = ev[-MAX:]
            X["ult"][k] = sorted(agora)
        # quem deixou de aparecer por inteiro (gabinete fechado): todos saem
        for k in [k for k in X["ult"] if k not in dep]:
            if X["ult"][k]:
                X["ev"].setdefault(k, []).extend([HOJE, "-", n, ""] for n in X["ult"][k]); tot += len(X["ult"][k])
            X["ult"][k] = []
        json.dump(X, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print("histórico de gabinetes:", tot, "entradas e saídas novas")

if __name__ == "__main__":
    main()
