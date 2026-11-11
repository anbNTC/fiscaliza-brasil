"""Sonda temporária: testa feeds RSS candidatos, acha o ID de canais do YouTube, perfis do Bluesky e feeds de podcasts."""
import re, json, sys, requests
from concurrent.futures import ThreadPoolExecutor
UA = {"user-agent": "FiscalizaBrasil/1.0 (agregador de manchetes com link para a fonte)", "accept": "application/rss+xml, application/xml, text/xml, */*"}

NAC = {
 "stf": ["https://noticias.stf.jus.br/feed/", "https://portal.stf.jus.br/noticias/rss.asp", "https://portal.stf.jus.br/rss/noticias.asp"],
 "tse": ["https://www.tse.jus.br/comunicacao/noticias/RSS", "https://www.tse.jus.br/rss", "https://www.tse.jus.br/comunicacao/noticias/rss.xml"],
 "tcu": ["https://portal.tcu.gov.br/imprensa/noticias/rss", "https://portal.tcu.gov.br/rss", "https://portal.tcu.gov.br/imprensa/noticias.rss"],
 "cnj": ["https://www.cnj.jus.br/feed/"],
 "agov": ["https://agenciagov.ebc.com.br/noticias/RSS", "https://agenciagov.ebc.com.br/RSS", "https://www.gov.br/secom/pt-br/assuntos/noticias/RSS", "https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/noticias/RSS"],
 "antag": ["https://oantagonista.com.br/feed/", "https://oantagonista.com.br/brasil/feed/"],
 "crusoe": ["https://crusoe.com.br/feed/", "https://crusoe.uol.com.br/feed/"],
 "pleno": ["https://pleno.news/feed", "https://pleno.news/brasil/politica-nacional/feed", "https://pleno.news/feed/"],
 "forum": ["https://revistaforum.com.br/rss/feed.html", "https://revistaforum.com.br/feed/", "https://revistaforum.com.br/rss"],
 "icl": ["https://iclnoticias.com.br/feed/"],
 "publica": ["https://apublica.org/feed/"],
 "bbc": ["https://feeds.bbci.co.uk/portuguese/rss.xml", "https://www.bbc.com/portuguese/index.xml"],
 "dw": ["https://rss.dw.com/xml/rss-br-all", "https://rss.dw.com/rdf/rss-br-all"],
 "nexo": ["https://www.nexojornal.com.br/rss.xml", "https://www.nexojornal.com.br/feed", "https://www.nexojornal.com.br/rss"],
 "valor": ["https://valor.globo.com/rss/valor/politica/", "https://pox.globo.com/rss/valor/", "https://valor.globo.com/rss/valor/"],
 "oglobo": ["https://oglobo.globo.com/rss/politica/", "https://oglobo.globo.com/rss/oglobo"],
 "aosfatos": ["https://www.aosfatos.org/noticias/feed/", "https://www.aosfatos.org/feed/"],
 "lupa": ["https://lupa.uol.com.br/feed", "https://www.agencialupa.org/feed", "https://lupa.uol.com.br/rss"],
 "fatooufake": ["https://g1.globo.com/rss/g1/fato-ou-fake/"],
 "verifica": ["https://www.estadao.com.br/arc/outboundfeeds/feeds/rss/sections/estadao-verifica/"],
 "comprova": ["https://projetocomprova.com.br/feed/"],
}
G1UF = {"AC": "ac/acre", "AL": "al/alagoas", "AP": "ap/amapa", "AM": "am/amazonas", "BA": "ba/bahia", "CE": "ce/ceara", "DF": "df/distrito-federal",
        "ES": "es/espirito-santo", "GO": "go/goias", "MA": "ma/maranhao", "MT": "mt/mato-grosso", "MS": "ms/mato-grosso-do-sul", "MG": "mg/minas-gerais",
        "PA": "pa/para", "PB": "pb/paraiba", "PR": "pr/parana", "PE": "pe/pernambuco", "PI": "pi/piaui", "RJ": "rj/rio-de-janeiro", "RN": "rn/rio-grande-do-norte",
        "RS": "rs/rio-grande-do-sul", "RO": "ro/rondonia", "RR": "rr/roraima", "SC": "sc/santa-catarina", "SP": "sp/sao-paulo", "SE": "se/sergipe", "TO": "to/tocantins"}
AL = {"AC": "al.ac.leg.br", "AL": "al.al.leg.br", "AP": "al.ap.leg.br", "AM": "aleam.gov.br", "BA": "al.ba.gov.br", "CE": "al.ce.gov.br", "DF": "cl.df.gov.br",
      "ES": "al.es.gov.br", "GO": "al.go.leg.br", "MA": "al.ma.leg.br", "MT": "al.mt.gov.br", "MS": "al.ms.gov.br", "MG": "almg.gov.br", "PA": "alepa.pa.gov.br",
      "PB": "al.pb.leg.br", "PR": "assembleia.pr.leg.br", "PE": "alepe.pe.gov.br", "PI": "alepi.pi.gov.br", "RJ": "alerj.rj.gov.br", "RN": "al.rn.leg.br",
      "RS": "al.rs.gov.br", "RO": "al.ro.leg.br", "RR": "al.rr.leg.br", "SC": "alesc.sc.gov.br", "SP": "al.sp.gov.br", "SE": "al.se.leg.br", "TO": "al.to.leg.br"}
JORN = {"AC": ["ac24horas.com"], "AL": ["tnh1.com.br", "cadaminuto.com.br"], "AP": ["selesnafes.com", "diariodoamapa.com.br"], "AM": ["d24am.com", "acritica.com"],
        "BA": ["bahianoticias.com.br", "metro1.com.br", "correio24horas.com.br"], "CE": ["opovo.com.br", "diariodonordeste.verdesmares.com.br"],
        "DF": ["correiobraziliense.com.br", "agenciabrasilia.df.gov.br"], "ES": ["folhavitoria.com.br", "agazeta.com.br"], "GO": ["jornalopcao.com.br", "maisgoias.com.br"],
        "MA": ["oimparcial.com.br", "imirante.com"], "MT": ["midianews.com.br", "olhardireto.com.br"], "MS": ["midiamax.uol.com.br", "campograndenews.com.br", "correiodoestado.com.br"],
        "MG": ["otempo.com.br", "em.com.br"], "PA": ["oliberal.com", "dol.com.br"], "PB": ["jornaldaparaiba.com.br", "clickpb.com.br"],
        "PR": ["bemparana.com.br", "plural.jor.br", "bandab.com.br"], "PE": ["jc.uol.com.br", "diariodepernambuco.com.br"], "PI": ["cidadeverde.com", "portalodia.com"],
        "RJ": ["odia.ig.com.br"], "RN": ["tribunadonorte.com.br", "saibamais.jor.br", "agorarn.com.br"], "RS": ["sul21.com.br", "correiodopovo.com.br", "matinaljornalismo.com.br"],
        "RO": ["rondoniaovivo.com", "tudorondonia.com", "rondoniagora.com"], "RR": ["folhabv.com.br", "roraimaemtempo.com.br"], "SC": ["ndmais.com.br", "nsctotal.com.br"],
        "SP": ["agora.folha.uol.com.br"], "SE": ["infonet.com.br", "f5news.com.br", "jlpolitica.com.br"], "TO": ["conexaoto.com.br", "afnoticias.com.br"]}
YT = ["@tvcamara", "@TVSenado", "@CNNbrasil", "@jovempannews", "@ICLNoticias", "@CanalMyNews", "@GloboNews", "@BandJornalismo", "@Poder360", "@RevistaOeste",
      "@BrasildeFato", "@folha", "@estadao", "@metropoles", "@STFoficial", "@camaradosdeputados", "@uolnoticias", "@cartacapital", "@gazetadopovo", "@tvbrasilgov"]
BSKY = ["Folha de S.Paulo", "Estadão", "g1", "Metrópoles", "CartaCapital", "Brasil de Fato", "Agência Pública", "Aos Fatos", "Poder360", "Intercept Brasil",
        "BBC News Brasil", "Nexo Jornal", "UOL", "Congresso em Foco", "Revista Fórum", "Gazeta do Povo", "O Globo", "Agência Lupa", "ICL Notícias", "Revista Oeste"]
POD = ["O Assunto g1", "Café da Manhã Folha", "Durma com essa Nexo", "Foro de Teresina", "Ao Ponto O Globo", "Estadão Notícias", "Os Pingos nos Is", "Oeste Sem Filtro", "Medo e Delírio em Brasília", "Papo Antagonista"]

def testa(u):
    try:
        r = requests.get(u, headers=UA, timeout=20)
        t = r.text
        n = len(re.findall(r"<item[\s>]", t)) or len(re.findall(r"<entry[\s>]", t))
        ti = re.search(r"<item[\s>][\s\S]*?<title[^>]*>([\s\S]*?)</title>", t) or re.search(r"<entry[\s>][\s\S]*?<title[^>]*>([\s\S]*?)</title>", t)
        d = re.search(r"<(?:pubDate|published|updated|dc:date)>([^<]+)<", t)
        return (u, r.status_code, n, re.sub(r"<!\[CDATA\[|\]\]>", "", ti.group(1))[:70] if ti else "", d.group(1)[:30] if d else "")
    except Exception as e:
        return (u, "ERRO " + type(e).__name__, 0, "", "")

def lote(nome, mapa):
    print("\n#####", nome, flush=True)
    urls = [(k, u) for k, L in mapa.items() for u in L]
    with ThreadPoolExecutor(16) as ex: res = list(ex.map(lambda x: (x[0],) + testa(x[1]), urls))
    for k, u, st, n, ti, d in res:
        if n: print("OK ", k, u, st, n, "|", ti, "|", d)
    ruins = sorted({k for k, *_ in res} - {k for k, u, st, n, *_ in res if n})
    print("SEM FEED:", ruins, flush=True)

lote("nacionais", NAC)
lote("g1 por estado", {uf: [f"https://g1.globo.com/rss/g1/{s}/"] for uf, s in G1UF.items()})
lote("assembleias", {uf: [f"https://www.{h}/feed/", f"https://{h}/feed/", f"https://www.{h}/rss", f"https://www.{h}/noticias/feed/", f"https://www.{h}/noticias/rss"] for uf, h in AL.items()})
lote("jornais por estado", {uf + ":" + h: [f"https://{h}/feed/", f"https://www.{h}/feed/", f"https://www.{h}/rss", f"https://{h}/rss", f"https://www.{h}/rss.xml"] for uf, L in JORN.items() for h in L})

print("\n##### youtube", flush=True)
for h in YT:
    try:
        t = requests.get("https://www.youtube.com/" + h, headers={"user-agent": "Mozilla/5.0", "accept-language": "pt-BR"}, cookies={"CONSENT": "YES+1"}, timeout=20).text
        m = re.search(r'"externalId":"(UC[\w-]{22})"', t) or re.search(r'channel/(UC[\w-]{22})', t)
        nome = re.search(r'<meta property="og:title" content="([^"]+)"', t)
        if m:
            f = testa("https://www.youtube.com/feeds/videos.xml?channel_id=" + m.group(1))
            print(h, m.group(1), nome.group(1) if nome else "", "| feed itens:", f[2], "|", f[3], "|", f[4])
        else: print(h, "sem id")
    except Exception as e: print(h, "ERRO", repr(e)[:80])
    sys.stdout.flush()

print("\n##### bluesky", flush=True)
for q in BSKY:
    try:
        j = requests.get("https://public.api.bsky.app/xrpc/app.bsky.actor.searchActors", params={"q": q, "limit": 4}, timeout=20).json()
        print(q, "→", [(a["handle"], a.get("displayName", "")[:30]) for a in j.get("actors", [])])
    except Exception as e: print(q, "ERRO", repr(e)[:80])
for h in ["folha.com", "estadao.com.br", "g1.globo.com", "metropoles.com", "cartacapital.com.br", "brasildefato.com.br", "apublica.org", "aosfatos.org", "poder360.com.br", "intercept.com.br", "nexojornal.com.br", "uol.com.br"]:
    f = testa(f"https://bsky.app/profile/{h}/rss"); print("rss", h, f[1], f[2], "|", f[3], "|", f[4])

print("\n##### podcasts", flush=True)
for q in POD:
    try:
        j = requests.get("https://itunes.apple.com/search", params={"term": q, "media": "podcast", "country": "BR", "limit": 2}, timeout=20).json()
        for x in j.get("results", []):
            f = testa(x.get("feedUrl", "")) if x.get("feedUrl") else ("", "", 0, "", "")
            print(q, "→", x.get("collectionName"), "|", x.get("artistName"), "|", x.get("feedUrl"), "| itens", f[2], "|", f[4])
    except Exception as e: print(q, "ERRO", repr(e)[:80])

print("\n##### congresso agora", flush=True)
import datetime
h = datetime.date.today().isoformat()
for u in [f"https://dadosabertos.camara.leg.br/api/v2/eventos?dataInicio={h}&dataFim={h}&ordem=ASC&ordenarPor=dataHoraInicio&itens=100",
          f"https://legis.senado.leg.br/dadosabertos/plenario/agenda/dia/{h.replace('-', '')}.json",
          f"https://legis.senado.leg.br/dadosabertos/comissao/agenda/{h.replace('-', '')}.json"]:
    try:
        r = requests.get(u, headers={"accept": "application/json"}, timeout=30); print(u, r.status_code); print(r.text[:2500])
    except Exception as e: print(u, "ERRO", repr(e)[:80])
