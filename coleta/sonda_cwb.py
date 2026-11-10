"""Sonda (temporária): paginação da consulta de Curitiba."""
import os, sys
os.environ["DEPURA"] = "1"; sys.path.insert(0, os.path.dirname(__file__))
import prefeitura_curitiba as P
P.main()
