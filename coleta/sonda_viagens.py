"""Sonda (temporária): testa a leitura de benefícios e missões oficiais."""
import sys, os, datetime
sys.path.insert(0, os.path.dirname(__file__))
import camara_verba_gabinete as V
for i in (220683, 178927, 204528):
    pg = []; V.um(i, datetime.date.today().year, pg)
    print(i, V.extras(pg[0]) if pg else "sem página"); print("  missões:", (V.missoes(i) or [])[:5])
