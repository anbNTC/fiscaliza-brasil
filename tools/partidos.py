"""Gera data/partidos.json: os 30 partidos registrados no TSE, a descrição de cada um (a partir do que o próprio partido declara no estatuto e no programa)
e como a bancada vota na Câmara e no Senado.

Critério de "seguiu o partido": em cada votação nominal, a posição do partido é o voto da maioria dos seus parlamentares que votaram Sim ou Não
(só quando pelo menos 3 votaram e a maioria tem mais de 50%). O voto de cada parlamentar é comparado com essa posição.
Partido de cada parlamentar = partido atual (Câmara e Senado, dados abertos)."""
import json
from collections import Counter, defaultdict
from pathlib import Path

D = Path(__file__).resolve().parents[1] / 'site' / 'data'
BR = json.load(open(D / 'br.json'))
VC = json.load(open(D / 'camara_votacoes.json'))
VS = json.load(open(D / 'senado_votacoes.json'))

# sigla, número, nome, federação, cores, a que se propõe (resumo do programa e do estatuto, nas palavras do Fiscaliza Brasil)
P = [
 ("PL", 22, "Partido Liberal", "", ["#1B3F8F", "#F2C200"], "Defende a economia de mercado, a redução do tamanho do Estado e dos impostos, valores conservadores ligados à família e aos costumes e uma segurança pública com punições mais duras.", ["Livre mercado e menos impostos", "Família e valores conservadores", "Segurança pública mais rigorosa"]),
 ("PT", 13, "Partido dos Trabalhadores", "Brasil da Esperança (PT, PCdoB e PV)", ["#C8102E", "#8E0B20"], "Defende o socialismo democrático, a redução das desigualdades, a ampliação de programas sociais e dos direitos dos trabalhadores, com o Estado atuando na economia e nos serviços públicos.", ["Redução das desigualdades", "Programas sociais e direitos trabalhistas", "Estado atuante na economia"]),
 ("UNIÃO", 44, "União Brasil", "União Progressista (União e PP)", ["#0B3D91", "#F5C400"], "Nasceu em 2022 da fusão do DEM com o PSL. Defende a economia de mercado, a responsabilidade fiscal, a redução da burocracia e o fortalecimento dos municípios.", ["Economia de mercado", "Responsabilidade fiscal", "Menos burocracia"]),
 ("PSD", 55, "Partido Social Democrático", "", ["#005CA9", "#F7A600"], "Fundado em 2011, apresenta-se como partido de centro. Defende a economia de mercado com responsabilidade social e o fortalecimento dos municípios.", ["Centro político", "Mercado com responsabilidade social", "Municipalismo"]),
 ("PP", 11, "Progressistas", "União Progressista (União e PP)", ["#0055A5", "#6CB33F"], "Defende a livre iniciativa, a redução da carga de impostos, o agronegócio e valores conservadores ligados à família.", ["Livre iniciativa", "Menos impostos", "Agronegócio"]),
 ("REPUBLICANOS", 10, "Republicanos", "", ["#0A4DA2", "#5BB4E5"], "Defende valores cristãos e da família, a liberdade religiosa, a economia de mercado e o empreendedorismo.", ["Valores cristãos e família", "Liberdade religiosa", "Empreendedorismo"]),
 ("MDB", 15, "Movimento Democrático Brasileiro", "", ["#00843D", "#F2C200"], "Partido com origem na oposição ao regime militar. Defende a democracia, a moderação política, a economia de mercado combinada com políticas sociais e tem forte presença nos municípios.", ["Democracia e moderação", "Mercado com políticas sociais", "Presença municipal"]),
 ("PODE", 20, "Podemos", "", ["#2BA84A", "#0B7A3E"], "Defende a democracia direta, com mais participação popular nas decisões, consultas públicas e uso de tecnologia, além do combate à corrupção.", ["Democracia direta", "Participação popular", "Combate à corrupção"]),
 ("PSDB", 45, "Partido da Social Democracia Brasileira", "PSDB Cidadania", ["#0080C6", "#FFD100"], "Defende a social-democracia, a responsabilidade fiscal, a modernização do Estado, inclusive com privatizações e parcerias, e políticas sociais.", ["Social-democracia", "Responsabilidade fiscal", "Modernização do Estado"]),
 ("PSB", 40, "Partido Socialista Brasileiro", "", ["#E5332A", "#F6A01A"], "Defende o socialismo democrático, a justiça social, o desenvolvimento sustentável e a soberania nacional.", ["Justiça social", "Desenvolvimento sustentável", "Soberania nacional"]),
 ("PSOL", 50, "Partido Socialismo e Liberdade", "PSOL-Rede", ["#FDC500", "#C8102E"], "Defende o socialismo com liberdade, a taxação das grandes fortunas, os direitos de trabalhadores, mulheres, população negra e LGBT+ e a proteção do meio ambiente. Opõe-se a privatizações.", ["Taxação de grandes fortunas", "Direitos e minorias", "Contra privatizações"]),
 ("PCdoB", 65, "Partido Comunista do Brasil", "Brasil da Esperança (PT, PCdoB e PV)", ["#D7262E", "#F2C200"], "Defende o socialismo, a soberania nacional, um projeto de desenvolvimento com valorização do trabalho e a ampliação dos direitos sociais.", ["Socialismo", "Soberania nacional", "Valorização do trabalho"]),
 ("PDT", 12, "Partido Democrático Trabalhista", "", ["#E2231A", "#0F4C9C"], "Defende o trabalhismo, a educação pública em tempo integral, os direitos dos trabalhadores e um projeto nacional de desenvolvimento.", ["Trabalhismo", "Educação em tempo integral", "Projeto nacional"]),
 ("PV", 43, "Partido Verde", "Brasil da Esperança (PT, PCdoB e PV)", ["#1E9E3E", "#F2C200"], "Defende a ecologia política, o desenvolvimento sustentável, a proteção do meio ambiente e dos animais e as liberdades individuais.", ["Meio ambiente", "Desenvolvimento sustentável", "Liberdades individuais"]),
 ("NOVO", 30, "Partido Novo", "", ["#F37021", "#1E2A44"], "Defende o liberalismo econômico, a redução do tamanho do Estado, dos impostos e dos privilégios do setor público e a abertura da economia.", ["Liberalismo econômico", "Estado menor", "Fim de privilégios"]),
 ("AVANTE", 70, "Avante", "", ["#E5007D", "#2D2E83"], "Apresenta-se como partido de centro, voltado à participação popular, ao trabalho e ao empreendedorismo.", ["Centro político", "Participação popular", "Empreendedorismo"]),
 ("SOLIDARIEDADE", 77, "Solidariedade", "Renovação Solidária (PRD e Solidariedade)", ["#F58220", "#0B4EA2"], "Ligado ao movimento sindical, defende os direitos dos trabalhadores, a geração de empregos e a valorização do trabalho.", ["Direitos dos trabalhadores", "Geração de empregos", "Movimento sindical"]),
 ("CIDADANIA", 23, "Cidadania", "PSDB Cidadania", ["#E4007C", "#00A0DF"], "Sucessor do antigo PPS. Defende a democracia, a ética na política, a responsabilidade fiscal e políticas sociais, com propostas reformistas.", ["Democracia e ética", "Responsabilidade fiscal", "Reformas"]),
 ("REDE", 18, "Rede Sustentabilidade", "PSOL-Rede", ["#00A19A", "#F28C00"], "Defende a sustentabilidade, a ética na política, a democracia participativa e a justiça social.", ["Sustentabilidade", "Ética na política", "Democracia participativa"]),
 ("PRD", 25, "Partido Renovação Democrática", "Renovação Solidária (PRD e Solidariedade)", ["#003F87", "#F2C200"], "Nasceu em 2023 da fusão do PTB com o Patriota. Defende valores conservadores, a família, o trabalho, o empreendedorismo e a economia de mercado.", ["Valores conservadores", "Família e trabalho", "Economia de mercado"]),
 ("MISSÃO", 14, "Missão", "", ["#111111", "#F2C200"], "Registrado em 2025, ligado ao Movimento Brasil Livre (MBL). Defende o liberalismo econômico, a redução do Estado e de privilégios, o combate à corrupção e a renovação política.", ["Liberalismo econômico", "Combate à corrupção", "Renovação política"]),
 ("AGIR", 36, "Agir", "", ["#00A3E0", "#1D1D1B"], "Antigo PTC. Defende a participação social, a família e o desenvolvimento humano, apresentando-se como partido de centro.", ["Participação social", "Família", "Desenvolvimento humano"]),
 ("MOBILIZA", 33, "Mobiliza", "", ["#E30613", "#1D1D1B"], "Antigo PMN. Defende a mobilização popular, o municipalismo e o desenvolvimento nacional.", ["Mobilização popular", "Municipalismo", "Desenvolvimento nacional"]),
 ("DC", 27, "Democracia Cristã", "", ["#0057A8", "#F2C200"], "Defende os princípios da doutrina social cristã: a dignidade da pessoa humana, a família e o bem comum.", ["Doutrina social cristã", "Família", "Bem comum"]),
 ("PRTB", 28, "Partido Renovador Trabalhista Brasileiro", "", ["#0B7A3E", "#F2C200"], "Defende valores conservadores e nacionalistas, a família e a economia de mercado.", ["Valores conservadores", "Nacionalismo", "Economia de mercado"]),
 ("PMB", 35, "Partido da Mulher Brasileira", "", ["#8E2C8C", "#F28DB2"], "Defende a participação das mulheres na política e políticas voltadas à mulher e à família.", ["Mulheres na política", "Políticas para a mulher", "Família"]),
 ("PSTU", 16, "Partido Socialista dos Trabalhadores Unificado", "", ["#D7262E", "#1D1D1B"], "Partido de orientação trotskista. Defende a revolução socialista, o controle da economia pelos trabalhadores e o não pagamento da dívida pública.", ["Revolução socialista", "Controle pelos trabalhadores", "Não pagamento da dívida"]),
 ("PCB", 21, "Partido Comunista Brasileiro", "", ["#C8102E", "#F2C200"], "Defende o socialismo e o comunismo, com base no marxismo-leninismo, e a organização da classe trabalhadora.", ["Socialismo e comunismo", "Marxismo-leninismo", "Organização dos trabalhadores"]),
 ("PCO", 29, "Partido da Causa Operária", "", ["#B5121B", "#1D1D1B"], "Defende o socialismo revolucionário e a organização independente dos trabalhadores.", ["Socialismo revolucionário", "Organização operária", "Independência de classe"]),
 ("UP", 80, "Unidade Popular", "", ["#E30613", "#F2C200"], "Defende o socialismo, o poder popular e as reformas urbana e agrária.", ["Socialismo", "Poder popular", "Reformas urbana e agrária"]),
]
assert len(P) == 30 and len({p[1] for p in P}) == 30

# parlamentares por partido (rótulos iguais aos da Câmara e do Senado)
ALIAS = {"S/Partido": None}
dep_v = {}
for f in (D / 'c').glob('*.json'):
    for k, v in json.load(open(f)).items(): dep_v[k] = v
sen_v = {}
for f in (D / 's').glob('*.json'):
    for k, v in json.load(open(f)).items(): sen_v[k] = v
mem = defaultdict(list)  # sigla -> [(casa, id, nome, uf, foto, vstring)]
for d in BR['dep']:
    mem[d[2]].append(("C", str(d[0]), d[1], d[3], d[4], dep_v.get(str(d[0]), {}).get('v', '')))
for s in BR['sen']:
    if ALIAS.get(s[3], s[3]): mem[s[3]].append(("S", str(s[0]), s[1], s[4], s[5], sen_v.get(str(s[0]), {}).get('v', '')))

def posicoes(membros, n):
    out = []
    for i in range(n):
        c = Counter(m[5][i] for m in membros if len(m[5]) > i and m[5][i] in "SN")
        t = c["S"] + c["N"]
        if t >= 3 and max(c["S"], c["N"]) * 2 > t: out.append("S" if c["S"] > c["N"] else "N")
        else: out.append("-")
    return "".join(out)

# ---------- Câmara: orientação oficial e partido no dia da votação (coleta/camara_orient.py) ----------
import re, unicodedata
nz = lambda x: re.sub(r"[^A-Z]", "", unicodedata.normalize("NFKD", x or "").encode("ascii", "ignore").decode().upper())
ALI = {"REPUBLICANOS": {"REPUBLICANOS", "REP"}, "UNIÃO": {"UNIAO"}, "PODE": {"PODE", "PODEMOS"}, "SOLIDARIEDADE": {"SOLIDARIEDADE", "SOLIDARIED", "SD"}, "CIDADANIA": {"CIDADANIA", "CID"}, "MISSÃO": {"MISSAO"}, "AVANTE": {"AVANTE", "AVANT"}}
def chaves(sig): return ALI.get(sig, set()) | {nz(sig)}
def orientacao(o, sig):
    ks = chaves(sig); fed = bl = None
    for rot, v in o.items():
        r = rot.strip(); rn = nz(r)
        if rn in ks: return v
        if re.match(r"(?i)^(fdr|fed)", r) and ks & {nz(t) for t in re.split(r"[-/ ]+", r[3:]) if t}: fed = v
        elif re.match(r"(?i)^bl", r) and ks & {nz(t) for t in re.findall(r"[A-Z][a-z]*", r[2:])}: bl = v
        elif re.search(r"[-/]", r) and ks & {nz(t) for t in re.split(r"[-/ ]+", r) if t}: fed = v
    return fed or bl
ORI = {}
_f = D / "camara_orient.json"
if _f.exists():
    ORI = json.load(open(_f)).get("v", {})
VID = [v[0] for v in VC]
cur = {str(d[0]): d[2] for d in BR["dep"]}
def partido_no_dia(k, i):
    x = ORI.get(VID[i]); return (x and x["p"].get(k)) or cur.get(k)
# maioria por partido no dia (para quando não há orientação: liberou a bancada ou o partido não orientou)
MAI = []
for i in range(len(VC)):
    x = ORI.get(VID[i]); cnt = defaultdict(Counter)
    for k, v in dep_v.items():
        s_ = v.get("v", "");
        if len(s_) > i and s_[i] in "SN": cnt[partido_no_dia(k, i)][s_[i]] += 1
    MAI.append({p: ("S" if c["S"] > c["N"] else "N") for p, c in cnt.items() if c["S"] + c["N"] >= 3 and max(c["S"], c["N"]) * 2 > c["S"] + c["N"]})
def posicao_c(sig, i):
    x = ORI.get(VID[i])
    if x:
        o = orientacao(x["o"], sig)
        if o in ("S", "N"): return o, "of"
        if o == "L": return "-", "lib"
    m = MAI[i].get(sig); return (m, "mai") if m else ("-", "")
FP = {}  # id deputado -> string g/r/- por votação
for k, v in dep_v.items():
    s_ = v.get("v", ""); out = []
    for i, c in enumerate(s_):
        if c in "SN":
            p, _ = posicao_c(partido_no_dia(k, i), i); out.append("-" if p not in "SN" else ("g" if c == p else "r"))
        else: out.append("-")
    FP[k] = "".join(out)
nof = sum(1 for i in range(len(VC)) if VID[i] in ORI)
print(f"orientações oficiais disponíveis para {nof} de {len(VC)} votações da Câmara")

cam, sen, stat = {}, {}, {}
for sig, num, nome, fed, cor, desc, bul in P:
    ms = mem.get(sig, [])
    mc = [m for m in ms if m[0] == "C"]; mS = [m for m in ms if m[0] == "S"]
    pc = "".join(posicao_c(sig, i)[0] for i in range(len(VC))) if mc else ""; ps = posicoes(mS, len(VS)) if mS else ""
    if mc: cam[sig] = pc
    if mS: sen[sig] = ps
    membros = []
    tot_a = tot_c = 0
    for m in ms:
        pos = pc if m[0] == "C" else ps; a = c = 0
        if m[0] == "C":
            f_ = FP.get(m[1], ""); a = f_.count("g"); c = f_.count("r")
        else:
            for i, x in enumerate(m[5]):
                if x in "SN" and i < len(pos) and pos[i] in "SN":
                    if x == pos[i]: a += 1
                    else: c += 1
        tot_a += a; tot_c += c
        membros.append([m[0], m[1], m[2], m[3], m[4], a, c])
    membros.sort(key=lambda x: (x[6] / (x[5] + x[6]) if x[5] + x[6] else 0), reverse=True)
    # governo (Câmara): índice 8 = orientação do governo
    g_a = g_t = 0
    for i, x in enumerate(pc):
        og = (VC[i][8] or "")[:1].upper()
        if x in "SN" and og in "SN": g_t += 1; g_a += x == og
    # votações recentes da Câmara com posição do partido
    rec = []
    for i in range(len(VC) - 1, -1, -1):
        if len(rec) >= 15: break
        if not pc or pc[i] not in "SN": continue
        com = [m[2] for m in mc if len(FP.get(m[1], "")) > i and FP[m[1]][i] == "g"]
        contra = [m[2] for m in mc if len(FP.get(m[1], "")) > i and FP[m[1]][i] == "r"]
        rec.append([i, pc[i], len(com), contra, posicao_c(sig, i)[1]])
    rec_s = []
    for i in range(len(VS) - 1, -1, -1):
        if len(rec_s) >= 10: break
        if not ps or ps[i] not in "SN": continue
        com = [m[2] for m in mS if len(m[5]) > i and m[5][i] == ps[i]]
        contra = [m[2] for m in mS if len(m[5]) > i and m[5][i] in "SN" and m[5][i] != ps[i]]
        rec_s.append([i, ps[i], len(com), contra])
    stat[sig] = {"dep": len(mc), "sen": len(mS), "a": tot_a, "c": tot_c, "coes": round(100 * tot_a / (tot_a + tot_c), 1) if tot_a + tot_c else None,
                 "gov": round(100 * g_a / g_t, 1) if g_t else None, "membros": membros, "rec": rec, "recS": rec_s}

# grava a cor de cada voto (g = com o partido, r = contra) na ficha de cada deputado
for f in (D / "c").glob("*.json"):
    j = json.load(open(f)); mud = False
    for k in j:
        if k in FP and j[k].get("fp") != FP[k]: j[k]["fp"] = FP[k]; mud = True
    if mud: json.dump(j, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
out = {"oficial": nof, "gerado": BR.get("gerado"), "fonte_estatutos": "https://www.tse.jus.br/partidos/partidos-registrados-no-tse",
       "partidos": [{"s": p[0], "n": p[1], "nome": p[2], "fed": p[3], "cor": p[4], "desc": p[5], "def": p[6]} for p in P],
       "cam": cam, "sen": sen, "stat": stat}
json.dump(out, open(D / 'partidos.json', 'w'), ensure_ascii=False, separators=(',', ':'))
for p in P:
    s = stat[p[0]]; print(f"{p[0]:14} dep {s['dep']:3} sen {s['sen']:2} coesão {s['coes']} gov {s['gov']}")
print((D / 'partidos.json').stat().st_size // 1024, "KB")
