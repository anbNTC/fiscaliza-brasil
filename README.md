# Fiscaliza Brasil

Plataforma independente para fiscalizar políticos do Brasil com dados oficiais (Câmara, Senado, TSE, STF, Banco Central, Receita Federal, IBGE e Portal da Transparência).

- `site/` – o site publicado no Cloudflare Pages (projeto **fiscalizaja**). `site/_worker.js` serve as rotas `/api/*`, `/img`, `/p/*` e `/partido/*`.
- `site/data/` – dados em JSON usados pelo site.
- `coleta/` – coletores que baixam dados oficiais (rodam toda madrugada no GitHub Actions).
- `tools/` – cálculos feitos sobre os dados (partidos, ranking, resumo da semana, médias da cota).
- `.github/workflows/dados.yml` – rotina diária: coleta, recalcula, grava e publica.
- `.github/workflows/publica.yml` – publica `site/` no Cloudflare a cada mudança.

Desenvolvido por [@oabraaonery](https://www.instagram.com/oabraaonery/).
