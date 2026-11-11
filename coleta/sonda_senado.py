"""Sonda (temporária): compara o coletor novo do Senado com os dados atuais (Flávio Arns, 345)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import senado_perfil as SP
y = json.load(open(SP.D / "s" / "PR.json"))["345"]
au = SP.projetos("345", "Flávio Arns"); di = SP.discursos("345")
print("AU velho", y["au"]["c"], len(y["au"]["l"])); print("AU novo ", au["c"], len(au["l"]), au["l"][0] if au["l"] else None)
print("DISC velho", {k: y["disc"][k] for k in ("n", "ano", "tipos")}, y["disc"]["kw"][:5]); print("DISC novo ", {k: di[k] for k in ("n", "ano", "tipos")}, di["kw"][:5])
