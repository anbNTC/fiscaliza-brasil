"""Senado · projetos e discursos de cada senador em exercício, refeitos todo dia (desde 2023).
Projetos: legis.senado.leg.br/dadosabertos/processo?codigoParlamentarAutor= (autor ou coautor).
Discursos: legis.senado.leg.br/dadosabertos/senador/{código}/discursos.json (por ano).
Grava em s/{UF}.json os campos "au" ({"c": tipo -> nº, "l": [[identificação, ementa, data, situação, "Sim"/"Não" autor principal, autoria]]})
e "disc" ({"n", "ano": {ano: n}, "tipos": {tipo: n}, "kw": [[assunto, n]]}). Se a fonte falhar, o campo antigo fica."""
import json, re, sys, time, datetime, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
S = requests.Session(); S.headers.update(H)
HOJE = datetime.date.today()
LISTA = {"PL", "PLP", "PEC", "PDL", "PRS"}
norm = lambda s: unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper()
GENERICO = {"DISCURSO", "COMENTARIO", "DEFESA", "REGISTRO", "CRITICA", "ANALISE", "ATUACAO", "GOVERNO FEDERAL", "BRASIL", "SENADO", "SENADO FEDERAL", "PROJETO DE LEI",
            "ALTERACAO", "LEI FEDERAL", "IMPORTANCIA", "APOIO", "SOLICITACAO", "NECESSIDADE", "PAIS", "ANUNCIO", "APRESENTACAO", "AUTORIA", "ORADOR", "PARTICIPAÇÃO", "PARTICIPACAO",
            "CRIACAO", "OBJETIVO", "DISCUSSAO", "AUTORIZACAO", "PAUTA", "VOTACAO", "APROVACAO", "REQUERIMENTO", "SESSAO", "PLENARIO", "SENADOR", "ELOGIO", "HOMENAGEM",
            "ENCAMINHAMENTO", "ORIENTACAO", "BANCADA", "PARECER", "RELATOR", "EMENDA", "INCLUSAO", "PRAZO", "PEDIDO", "AGRADECIMENTO", "QUESTAO DE ORDEM", "MATERIA", "ACORDO",
            "REFERENCIA", "PROPOSTA", "TEXTO", "LEI", "AMPLIACAO", "MELHORIA", "GARANTIA", "ACESSO", "REDUCAO", "AUMENTO", "PROGRAMA", "POLITICAS PUBLICAS", "INFORMACAO"}

def get(u):
    for k in range(4):
        try:
            r = S.get(u, timeout=180)
            if r.status_code == 404: return None
            if r.ok: return r.json()
        except Exception as e: print(u, repr(e)[:100], flush=True)
        time.sleep(5 * (k + 1))
    raise RuntimeError("Senado não respondeu: " + u)

def projetos(cod, nome):
    L = get(f"https://legis.senado.leg.br/dadosabertos/processo?codigoParlamentarAutor={cod}&dataInicioApresentacao=2023-02-01") or []
    c = Counter(); l = []; vis = set(); n0 = norm(nome)
    for x in L:
        ident = (x.get("identificacao") or "").strip()
        if not ident or ident in vis: continue
        vis.add(ident); sg = ident.split(" ")[0]; c[sg] += 1
        if sg in LISTA:
            aut = (x.get("autoria") or "").strip(); primeiro = norm(aut.split(",")[0])
            l.append([ident, (x.get("ementa") or "").strip()[:200], (x.get("dataApresentacao") or "")[:10], (x.get("situacaoAtual") or "").upper(),
                      "Sim" if n0 and n0 in primeiro else "Não", aut[:200]])
    l.sort(key=lambda p: p[2])
    return {"c": dict(c), "l": l}

def discursos(cod):
    tipos = Counter(); anos = Counter(); kw = Counter(); n = 0
    for ano in range(2023, HOJE.year + 1):
        fim = min(datetime.date(ano, 12, 31), HOJE)
        j = get(f"https://legis.senado.leg.br/dadosabertos/senador/{cod}/discursos.json?dataInicio={ano}0101&dataFim={fim:%Y%m%d}") or {}
        P = (((j.get("DiscursosParlamentar") or {}).get("Parlamentar") or {}).get("Pronunciamentos") or {}).get("Pronunciamento") or []
        if isinstance(P, dict): P = [P]
        for p in P:
            if (p.get("SiglaCasaPronunciamento") or "SF") != "SF": continue
            n += 1; anos[str(ano)] += 1; tipos[((p.get("TipoUsoPalavra") or {}).get("Descricao") or "Outros").strip()] += 1
            for t in re.split(r"[,.\n]", p.get("Indexacao") or ""):
                t = t.strip()
                if 3 < len(t) < 40 and norm(t) not in GENERICO and not re.search(r"PROJETO|PROPOSTA DE EMENDA|MEDIDA PROVISORIA|\(", norm(t)): kw[t.title()] += 1
        time.sleep(0.3)
    return {"n": n, "ano": dict(anos), "tipos": dict(tipos.most_common()), "kw": [[k, v] for k, v in kw.most_common(12)]}

def main():
    BR = json.load(open(D / "br.json")); por_uf = defaultdict(dict); erros = 0
    for s in BR["sen"]:
        cod = str(s[0])
        try: por_uf[s[4]][cod] = {"au": projetos(cod, s[1])}
        except Exception as e: print(s[1], "projetos:", repr(e)[:120]); erros += 1; por_uf[s[4]][cod] = {}
        try: por_uf[s[4]][cod]["disc"] = discursos(cod)
        except Exception as e: print(s[1], "discursos:", repr(e)[:120]); erros += 1
        time.sleep(0.3)
    n = 0
    for uf, novos in por_uf.items():
        p = D / "s" / f"{uf}.json"
        try: X = json.load(open(p))
        except Exception: X = {}
        for k, v in novos.items():
            if v: X.setdefault(k, {}).update(v); n += 1
        json.dump(X, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({"senadores": n, "erros": erros}))
    if erros > 20: sys.exit(1)

if __name__ == "__main__":
    main()
