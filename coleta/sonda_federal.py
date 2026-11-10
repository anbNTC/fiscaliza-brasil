"""Sonda (temporária): compara o coletor novo com os dados atuais."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import federal_perfil as F
B = json.load(open(F.D / "br.json")); C = json.load(open(F.D / "c" / "PR.json"))["178927"]; S = json.load(open(F.D / "s" / "PR.json"))["345"]
au = F.projetos_camara({"178927"}).get("178927", {})
print("AU velho", sum(C["au"]["c"].values()), len(C["au"]["l"]), "| novo", sum(au.get("c", {}).values()), len(au.get("l", [])), au.get("l", [None])[0])
co = F.cota_camara({"178927"}).get("178927", {})
print("COTA velha", {a: sum(t.values()) for a, t in C["cota"]["a"].items()}, C["cota"]["f"][:2]); print("COTA nova", {a: sum(t.values()) for a, t in co.get("a", {}).items()}, co.get("f", [])[:2], list(co.get("a", {}).get("2026", {}))[:3])
cs = F.cota_senado(B["sen"]).get("345", {})
print("CEAPS velha", {a: sum(t.values()) for a, t in S["cota"]["a"].items()}, list(S["cota"]["a"]["2024"])[:3]); print("CEAPS nova", {a: sum(t.values()) for a, t in cs.get("a", {}).items()}, list(cs.get("a", {}).get("2024", {}))[:3])
