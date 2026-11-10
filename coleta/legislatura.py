"""Virada de mandato: qual lista de deputados estaduais está em exercício.
Até 31/01/2027 valem os eleitos de 2022 ("de22"); a partir de 1º/02/2027, os eleitos de 2026 ("de26").
Os arquivos das Assembleias guardam "ano" para o site saber a que lista as chaves se referem."""
import datetime
POSSE_LEG = datetime.date(2027, 2, 1)

def lista_est(U, hoje=None):
    hoje = hoje or datetime.date.today()
    if hoje >= POSSE_LEG and U.get("de26"): return U["de26"], "26"
    return U.get("de22", []), "22"
