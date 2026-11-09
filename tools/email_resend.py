"""Envio de e-mail pelo Resend (API). A chave fica só no segredo RESEND_API_KEY do GitHub, nunca no repositório."""
import os, json, sys, requests
REMETENTE = "Fiscaliza Brasil <nao-responda@fiscalizaja.com.br>"

def envia(para, assunto, html, texto=None, cabecalhos=None):
    k = os.environ.get("RESEND_API_KEY")
    if not k: print("sem RESEND_API_KEY: e-mail não enviado"); return False
    corpo = {"from": REMETENTE, "to": [para] if isinstance(para, str) else para, "subject": assunto, "html": html}
    if texto: corpo["text"] = texto
    if cabecalhos: corpo["headers"] = cabecalhos
    r = requests.post("https://api.resend.com/emails", headers={"Authorization": "Bearer " + k, "Content-Type": "application/json"}, data=json.dumps(corpo), timeout=30)
    if r.status_code >= 300: print("Resend", r.status_code, r.text[:200]); return False
    return True

if __name__ == "__main__":
    # aviso de coleta: ETAPAS='{"emendas":"failure",...}'  (só envia se alguma falhou)
    et = json.loads(os.environ.get("ETAPAS", "{}")); ruins = {k: v for k, v in et.items() if v not in ("success", "skipped", "")}
    para = os.environ.get("ALERTA_EMAIL")
    if not ruins: print("todas as etapas ok"); sys.exit(0)
    if not para: print("etapas com problema, mas sem ALERTA_EMAIL:", ruins); sys.exit(0)
    run = os.environ.get("RUN_URL", "")
    nomes = {"orient": "Câmara · orientações", "emendas": "Emendas federais", "assembleias": "Assembleias (SAPL)", "alesp": "ALESP", "alesc": "ALESC", "alba": "ALBA", "alepe": "Alepe", "ales": "Ales",
             "alrs": "ALRS", "emest": "Emendas estaduais", "camaras": "Câmaras Municipais", "vm": "TSE · votos por cidade", "camp": "TSE · doadores", "calc": "Cálculos", "pautas": "Pautas"}
    linhas = "".join(f"<li><b>{nomes.get(k, k)}</b>: {'falhou' if v == 'failure' else v}</li>" for k, v in ruins.items())
    html = f"<h2>Coleta do Fiscaliza Brasil com problema</h2><p>Na coleta de hoje, estas etapas não terminaram bem:</p><ul>{linhas}</ul><p>O resto do site foi atualizado normalmente; essas partes ficam com os dados do dia anterior.</p><p><a href='{run}'>Ver o registro da coleta no GitHub</a></p>"
    print("aviso enviado" if envia(para, f"⚠️ Coleta com problema: {', '.join(nomes.get(k, k) for k in ruins)}", html) else "falha ao enviar aviso")
