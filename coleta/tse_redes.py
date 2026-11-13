"""Redes sociais declaradas ao TSE e candidatura de 2026 de cada político que aparece no site.
Fonte: TSE · Dados Abertos, consulta_cand_{ano}.zip (candidaturas) e rede_social_candidato_{ano}.zip (endereços que o próprio
candidato informou no registro). Anos: 2022, 2024 e 2026; vale o ano mais recente que tiver a rede.
Saída:
  site/data/redes/{UF}.json   {"n": {NOME CIVIL: {rede: [perfil...]}}, "c26": {NOME CIVIL: [cargo, resultado, situação]}}
                              deputados, senadores e governadores (eleitos ou em exercício), casados pelo nome civil dentro da UF
  site/data/redes/m{UF}.json  {"s": {SQ 2024: {rede: [perfil...]}}, "c26": {SQ 2024: [cargo, resultado, situação]}}
                              prefeitos, vices e vereadores eleitos em 2024
Rede: ig (Instagram), tt (TikTok), yt (YouTube), x (X/Twitter), fb (Facebook), th (Threads). Só o nome do perfil, não o endereço.
Roda no máximo uma vez por semana (REFAZ=1 força), porque os arquivos são grandes e quase não mudam."""
import csv, io, json, os, re, sys, zipfile, tempfile, datetime, unicodedata
from collections import defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "redes"; OUT.mkdir(exist_ok=True)
C = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand"
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}
ANOS = [2022, 2024, 2026]
normd = lambda s: re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper())).strip()
REDE = [("ig", r"instagram\.com/"), ("tt", r"tiktok\.com/@?"), ("yt", r"youtube\.com/(?:@|c/|user/|channel/)?"), ("x", r"(?:twitter|x)\.com/"),
        ("fb", r"facebook\.com/(?:people/)?"), ("th", r"threads\.(?:net|com)/@?")]
RUIM = {"p", "reel", "reels", "share", "watch", "profile.php", "pages", "groups", "explore", "stories", "home", "intent", "hashtag", "search", "tv", "accounts", "sharer", "channel", "direct", "about", "web", "www", "login", "watch"}

def perfil(u):
    """endereço → (rede, nome do perfil); None se não der para tirar um perfil limpo"""
    u = re.sub(r"\s+", "", str(u or "")).strip("'\" ")
    for k, pad in REDE:
        m = re.search(pad + r"([A-Za-z0-9_.\-]+)", u, re.I)
        if m:
            h = m.group(1).strip(".").lstrip("@")
            if not h or h.lower() in RUIM or len(h) < 2 or len(h) > 60: return None
            return k, (h if k == "yt" and re.match(r"^UC[\w-]{22}$", h) else h.lower())
    return None

def baixa(nome):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with requests.get(f"{C}/{nome}", headers=H, timeout=900, stream=True) as r:
        r.raise_for_status()
        for b in r.iter_content(1 << 20): f.write(b)
    f.close(); return zipfile.ZipFile(f.name)

def linhas(z, uf=None):
    for n in z.namelist():
        if not n.endswith(".csv"): continue
        m = re.search(r"_([A-Z]{2})\.csv$", n)
        if not m or m.group(1) in ("BR",) or (uf and m.group(1) != uf): continue
        with z.open(n) as fh:
            for row in csv.DictReader(io.TextIOWrapper(fh, "latin-1"), delimiter=";"): yield m.group(1), row

def interesse():
    """quem o site mostra: nomes civis por UF (estado/federal) e SQ de 2024 (municípios)"""
    nomes = defaultdict(set); sq24 = defaultdict(set)
    BR = json.load(open(D / "br.json"))
    for d in BR["dep"]: nomes[d[3]].add(normd(d[5]))
    for s in BR["sen"]: nomes[s[4]].add(normd(s[2]))
    for uf, u in BR["ufs"].items():
        for k in ("gov", "gov26"):
            for p in u.get(k) or []:
                if p: nomes[uf].add(normd(p[1]))
    for f in (D / "uf").glob("*.json"):
        U = json.load(open(f)); uf = f.stem
        for k in ("de22", "de26", "df26", "se26"):
            for p in U.get(k) or []: nomes[uf].add(normd(p[1]))
        for m in (U.get("mun") or {}).values():
            for p in [m[1], m[2]] + list(m[3] or []):
                if p and len(p) > 10 and p[10]: sq24[uf].add(str(p[10]))
    for f in (D / "est").glob("*.json"):
        try:
            for e in json.load(open(f)).get("dep", {}).values():
                if e.get("civil"): nomes[f.stem].add(normd(e["civil"]))
        except Exception: pass
    nomes = {uf: {n for n in v if n} for uf, v in nomes.items()}
    return nomes, sq24

def main():
    g = OUT / "_gerado.txt"
    if not os.environ.get("REFAZ") and g.exists() and (datetime.date.today() - datetime.date.fromisoformat(g.read_text().strip())).days < 7:
        print("redes: gravadas há menos de 7 dias, nada a fazer"); return
    nomes, sq24 = interesse()
    redes_n = defaultdict(dict); redes_s = defaultdict(dict)   # [uf][nome] / [uf][sq24] -> {rede: [perfis]} (ano mais novo primeiro)
    nome_sq24 = {}   # (uf, nome civil) -> sq de 2024, para casar a candidatura de 2026 dos prefeitos e vereadores
    c26 = defaultdict(dict); c26m = defaultdict(dict)
    for ano in sorted(ANOS, reverse=True):
        zc = baixa(f"consulta_cand_{ano}.zip"); quem = {}   # sq -> (uf, nome civil, sq24 ou None)
        for uf, r in linhas(zc):
            sq = r.get("SQ_CANDIDATO"); nm = normd(r.get("NM_CANDIDATO"))
            if ano == 2024:
                if sq in sq24.get(uf, ()): quem[sq] = (uf, nm, sq); nome_sq24[(uf, nm)] = sq
            elif nm in nomes.get(uf, ()): quem[sq] = (uf, nm, None)
            if ano == 2026:
                turno = int(r.get("NR_TURNO") or 1)
                v = [str(r.get("DS_CARGO") or "").capitalize(), str(r.get("DS_SIT_TOT_TURNO") or ""), str(r.get("DS_SITUACAO_CANDIDATURA") or ""), turno]
                ant = c26[uf].get(nm)
                if not ant or turno >= ant[3]: c26[uf][nm] = v
        print(ano, "candidaturas casadas:", len(quem), flush=True); del zc
        zr = baixa(f"rede_social_candidato_{ano}.zip"); novo_n = defaultdict(lambda: defaultdict(list)); novo_s = defaultdict(lambda: defaultdict(list))
        for uf, r in linhas(zr):
            q = quem.get(r.get("SQ_CANDIDATO"))
            if not q: continue
            p = perfil(r.get("DS_URL"))
            if not p: continue
            alvo = novo_s[q[0]][q[2]] if q[2] else novo_n[q[0]][q[1]]
            if p not in alvo: alvo.append(p)
        del zr
        for dst, src in ((redes_n, novo_n), (redes_s, novo_s)):
            for uf, pessoas in src.items():
                for k, lst in pessoas.items():
                    atual = dst[uf].setdefault(k, {})
                    for rede, h in lst:
                        if rede not in atual: atual[rede] = []
                        # a rede já veio de um ano mais novo: os perfis antigos só entram se forem diferentes e houver espaço
                        if h.lower() not in (x.lower() for x in atual[rede]) and len(atual[rede]) < 2: atual[rede].append(h)
    # candidatura de 2026 de prefeitos e vereadores (pelo nome civil na mesma UF)
    for uf, cs in c26.items():
        for nm, v in cs.items():
            s = nome_sq24.get((uf, nm))
            if s: c26m[uf][s] = v[:3]
    ufs = set(nomes) | set(sq24)
    for uf in sorted(ufs):
        est = {"n": redes_n.get(uf, {}), "c26": {nm: v[:3] for nm, v in c26.get(uf, {}).items() if nm in nomes.get(uf, ())}}
        json.dump(est, open(OUT / f"{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        json.dump({"s": redes_s.get(uf, {}), "c26": c26m.get(uf, {})}, open(OUT / f"m{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        print(uf, "estado/federal com rede:", len(est["n"]), "| municípios com rede:", len(redes_s.get(uf, {})), "| 2026:", len(est["c26"]), "+", len(c26m.get(uf, {})), flush=True)
    g.write_text(datetime.date.today().isoformat())

if __name__ == "__main__":
    main()
