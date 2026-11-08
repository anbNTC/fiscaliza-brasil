"""Acesso pela saída do Brasil (Worker fiscaliza-br, em São Paulo) para Assembleias que só respondem a acessos do país.
Precisa de SAIDA_BR (URL do Worker) e CHAVE_BR no ambiente; sem eles, acessa direto."""
import os, time, requests
URL = os.environ.get("SAIDA_BR", "https://fiscaliza-br.contatoabraaonery.workers.dev"); CHAVE = os.environ.get("CHAVE_BR", "")
S = requests.Session()

def get(u, params=None, tentativas=3, timeout=120, post=None, headers=None):
    if params:
        u = requests.Request("GET", u, params=params).prepare().url
    for k in range(tentativas):
        try:
            h = {"x-chave": CHAVE, **(headers or {})}
            if CHAVE:
                r = S.post(URL, params={"u": u}, data=post, headers=h, timeout=timeout) if post is not None else S.get(URL, params={"u": u}, headers=h, timeout=timeout)
            else:
                r = requests.request("POST" if post is not None else "GET", u, data=post, headers=headers, timeout=timeout)
            if r.status_code < 500 and r.status_code != 429: return r
        except Exception: pass
        time.sleep(3 * (k + 1))
    return None
