"""ALESP (São Paulo): deputados, proposituras e autores, pelos arquivos oficiais de dados abertos (atualizados todo dia).
Saída: site/data/est/SP.json no mesmo formato das Assembleias com SAPL (sem votos: a ALESP não publica votos de plenário)."""
import io, json, re, sys, unicodedata, zipfile, datetime
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
B = "https://www.al.sp.gov.br/repositorioDados"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
norm = lambda s: re.sub(r"[^A-Z ]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()).strip()
DESDE = "2023-03-15"  # início da 20ª legislatura da ALESP

def baixa(path):
    r = requests.get(f"{B}/{path}", headers=H, timeout=300); r.raise_for_status()
    if r.content[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(r.content)); return z.open(z.namelist()[0])
    return io.BytesIO(r.content)

def registros(f):
    """Lê o XML registro a registro: devolve um dict {campo: texto} para cada elemento de 2º nível."""
    prof = 0; atual = None
    for ev, el in ET.iterparse(f, events=("start", "end")):
        if ev == "start":
            prof += 1
            if prof == 2: atual = {}
        else:
            if prof == 3 and atual is not None: atual[el.tag] = (el.text or "").strip()
            if prof == 2: yield atual; el.clear(); atual = None
            prof -= 1

def campo(r, *nomes):
    low = {k.lower(): v for k, v in r.items()}
    for n in nomes:
        if n.lower() in low: return low[n.lower()]
    return ""

def data_iso(s):
    m = re.match(r"(\d{4})-(\d\d)-(\d\d)", s or "") or None
    if m: return m.group(0)
    m = re.match(r"(\d\d)/(\d\d)/(\d{4})", s or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""

def main():
    deps = list(registros(baixa("deputados/deputados.xml")))
    print("campos deputado:", list(deps[0].keys()) if deps else None, flush=True)
    em = [d for d in deps if campo(d, "Situacao") in ("EXE", "") ] or deps
    nat = {}
    try:
        for n in registros(baixa("processo_legislativo/naturezasSpl.xml")):
            nat[campo(n, "idNatureza", "IdNatureza")] = (campo(n, "sgNatureza", "SgNatureza", "Sigla"), campo(n, "nmNatureza", "NmNatureza", "Nome"))
    except Exception as e: print("naturezas:", e, flush=True)
    props = {}
    for p in registros(baixa("processo_legislativo/proposituras.zip")):
        if not props: print("campos propositura:", list(p.keys()), flush=True)
        d = data_iso(campo(p, "DtEntradaSistema", "DtApresentacao", "DtPublicacao"))
        if d >= DESDE: props[campo(p, "IdDocumento")] = (p, d)
    print("proposituras desde", DESDE, ":", len(props), flush=True)
    por = defaultdict(list); n_aut = 0
    for a in registros(baixa("processo_legislativo/documento_autor.zip")):
        if not n_aut: print("campos autor:", list(a.keys()), flush=True)
        n_aut += 1
        i = campo(a, "IdDocumento")
        if i in props: por[(campo(a, "IdAutor"), norm(campo(a, "NomeAutor")))].append(i)
    # liga deputado ALESP -> autor -> deputado do site (TSE 2022)
    U = json.load(open(D / "uf" / "SP.json")); de = U.get("de22", [])
    idx = {}
    for k, x in enumerate(de): idx.setdefault(norm(x[0]), k); idx.setdefault(norm(x[1]), k); idx.setdefault(limpa(x[0]), k)
    toks = [(j, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for j, x in enumerate(de)]
    porid = defaultdict(list); pornome = defaultdict(list)
    for (ia, na), ids in por.items(): porid[ia] += ids; pornome[na] += ids
    dep = {}; sem = []
    for d in em:
        nome = campo(d, "NomeParlamentar", "Nome"); ids = porid.get(campo(d, "IdSPL")) or porid.get(campo(d, "IdDeputado")) or pornome.get(norm(nome)) or []
        ids = sorted(set(ids), key=lambda i: props[i][1], reverse=True)
        def sig(i):
            p = props[i][0]; s = nat.get(campo(p, "IdNatureza"), ("", ""))[0] or campo(p, "SgNatureza", "Natureza")
            return s or "?"
        cont = Counter(sig(i) for i in ids)
        lista = [[f"{sig(i)} {campo(props[i][0], 'NroLegislativo', 'Numero')}/{campo(props[i][0], 'AnoLegislativo', 'Ano')}", re.sub(r"\s+", " ", campo(props[i][0], "Ementa"))[:200], props[i][1], 0]
                 for i in ids if sig(i) in ("PL", "PLC", "PEC", "PDL", "PR", "PRL")][:80]
        k = idx.get(norm(nome))
        if k is None: k = idx.get(limpa(nome))
        if k is None:
            t = set(limpa(nome).split())
            best = sorted(((len(t & q) / max(1, min(len(t), len(q))), len(t & q), j) for j, q in toks), reverse=True)
            if best and best[0][0] >= 0.99 and best[0][1] >= 1 and (len(best) < 2 or best[1][:2] < best[0][:2]): k = best[0][2]
            elif best and best[0][1] >= 2 and best[0][0] >= 0.6 and (len(best) < 2 or best[1][:2] < best[0][:2]): k = best[0][2]
        reg = {"nome": nome, "civil": "", "partido": campo(d, "Partido", "SiglaPartido"), "foto": f"https://www3.al.sp.gov.br/repositorio/deputadoPortal/fotos/{campo(d, 'IdDeputado')}.jpg" if campo(d, "IdDeputado") else "",
               "cont": dict(cont), "props": lista, "votos": {}, "vlist": [], "sapl": f"https://www.al.sp.gov.br/deputado/?matricula={campo(d, 'Matricula') or campo(d, 'IdDeputado')}"}
        if k is None: sem.append(nome); dep["x" + campo(d, "IdDeputado")] = reg
        else: dep[str(k)] = reg
    out = {"fonte": "Assembleia Legislativa de São Paulo (ALESP) · Dados Abertos", "url": "https://www.al.sp.gov.br/dados-abertos/", "gerado": datetime.date.today().isoformat(),
           "legislatura": "20ª legislatura (2023–2027)", "temVotos": False, "dep": dep}
    json.dump(out, open(OUT / "SP.json", "w"), ensure_ascii=False, separators=(",", ":"))
    r = {"deputados": len(em), "ligados": len(em) - len(sem), "proposituras": len(props), "autorias": n_aut, "sem_par": sem[:10]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
