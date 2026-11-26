"""Sonda temporária: tipos e mapa por tipo no Câmara sem Papel (Sorocaba)."""
import sys, re, html
sys.path.insert(0, "coleta")
from assembleias_sapl import H
from saida_br import get
B = "https://sorocaba.camarasempapel.com.br/spl/"
t = html.unescape(get(B + "consulta-tipo.aspx", headers=H, timeout=90).text)
cards = re.findall(r"<div class='card-title[^>]*>([^<]+?)\((\d+)\)<([\s\S]*?)</div></div></div>", t)
print("TIPOS", [(a.strip(), sorted(set(re.findall(r"tipo=(\d+)", c)))[:2]) for a, n, c in cards][:40], flush=True)
a = html.unescape(get(B + "consulta-autor.aspx", headers=H, timeout=90).text)
m = re.search(r"consulta-producao\.aspx\?autor=(\d+)&ano=2025", a); aid = m.group(1)
p = html.unescape(get(B + f"consulta-producao.aspx?autor={aid}&ano=2025", headers=H, timeout=90).text)
i = p.find("MAPA"); print("MAPA", re.sub(r"\s+", " ", re.sub(r"<(script|style|svg)[\s\S]*?</\1>|<[^>]+>", " | ", p[i:i + 5000]))[:1500], flush=True)
print("MAPALINKS", sorted(set(re.findall(r"href='(consulta-producao\.aspx\?[^']*tipo[^']*)'", p)))[:20], flush=True)
