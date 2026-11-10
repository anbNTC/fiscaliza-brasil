"""Sonda (temporária): testa os coletores de gabinete."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import camara_verba_gabinete as V, senado_gabinete as SG
for a in (2025, 2026): print(a, V.um(220683, a))
SG.main()
