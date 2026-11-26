"""Sonda temporária: estrutura das páginas do Câmara sem Papel em Sorocaba (tipo, autor, produção)."""
import sys, re, html
sys.path.insert(0, "coleta")
from assembleias_sapl import H
from saida_br import get
B = "https://sorocaba.camarasempapel.com.br/spl/"
t = html.unescape(get(B + "consulta-tipo.aspx", headers=H, timeout=90).text)
i = t.find("Projeto de Lei"); print("TIPOHTML", re.sub(r"\s+", " ", t[max(0, i - 700):i + 900]), flush=True)
print("TIPOLINKS", sorted(set(re.findall(r"""href=["'](consulta-producao[^"']*)["']""", t)))[:12], flush=True)
a = html.unescape(get(B + "consulta-autor.aspx", headers=H, timeout=90).text)
ls = sorted(set(re.findall(r"""href=["'](consulta-producao[^"']*)["']""", a))); print("AUTLINKS", len(ls), ls[:6], flush=True)
j = a.find(ls[0]) if ls else 0; print("AUTHTML", re.sub(r"\s+", " ", a[max(0, j - 900):j + 300]), flush=True)
