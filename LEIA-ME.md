# Fiscaliza Brasil · site

## O que tem na pasta

| Arquivo | Endereço no site | Quem acessa |
|---|---|---|
| `index.html` | `/` | Público: página inicial com FISCALIZE e VOTO DISTRITAL |
| `fiscalize.html` | `/fiscalize` | Público |
| `distrital.html` | `/distrital` | Público |
| `links.html` | `/links` | Público: links da bio do @oabraaonery |
| `fiscalize.html` + `cracha.js` | `/fiscalize` | Público: app do Brasil inteiro (mapa, estado, cidade, ficha) |
| `parana.html` | `/parana` | Público: ficha completa do Paraná (orientação de bancada, emendas, ALEP, CMC) |
| `data/` | (apoio) | Dados de cada estado, deputados, senadores, votações e patrimônio |
| `painel.html` | `/painel` | Só você, com e-mail e senha (links da bio e reportes de erro) |
| `links.js`, `links.css` | (apoio) | Desenho da página de links, usado também na prévia do painel |
| `config.js` | (apoio) | Endereço e chave pública do Supabase |
| `schema.sql` | (não vai para o site) | Cria as tabelas e permissões no Supabase |

## 1. Supabase (banco de dados e login)

1. Em supabase.com/dashboard, clique em **New project**. Nome: `Fiscaliza Brasil`. Região: **South America (São Paulo)**. Guarde a senha do banco.
2. **Authentication › Users › Add user › Create new user**: seu e-mail e uma senha forte, com **Auto Confirm User** marcado.
3. **Authentication › Sign In / Providers**: desligue **Allow new users to sign up**, para ninguém mais criar conta.
4. **SQL Editor › New query**: cole todo o `schema.sql` e clique em **Run**. Ele cria as tabelas, os botões iniciais, o espaço das fotos e coloca o seu usuário como administrador.
5. **Project Settings › API** (ou o botão **Connect**): copie o **Project URL** e a chave **anon / publishable** para o `config.js`. Não use a chave `service_role` / `secret`.

## 2. Cloudflare Pages (hospedagem)

1. No Cloudflare: **Workers & Pages › Create › Pages › Upload assets**.
2. Nome do projeto: `fiscalizabrasil`. O endereço será `fiscalizabrasil.pages.dev`.
3. Arraste a pasta inteira (sem o `schema.sql` e este LEIA-ME, se quiser) e clique em **Deploy**.
4. Para atualizar depois: no projeto, **Create deployment** e arraste a pasta de novo.

## 3. Instagram

Na bio do @oabraaonery, use `https://fiscalizabrasil.pages.dev/links` (ou o seu domínio, quando estiver ligado).
Para editar os botões: `/painel` › **Links da bio** › **Salvar**.

## 4. Domínio do Registro.br (quando comprar)

1. No Cloudflare, **Add a domain** com o seu domínio (plano Free). Ele mostra dois servidores DNS.
2. No Registro.br, em **DNS › Alterar servidores DNS**, troque pelos dois do Cloudflare. Pode levar algumas horas.
3. No projeto do Pages, **Custom domains › Set up a custom domain**, com o domínio e também `www`.
4. No Supabase, em **Authentication › URL Configuration**, troque o **Site URL** para o domínio novo.

## Observações

- Se o Supabase estiver fora do ar ou pausado, a página `/links` mostra os botões padrão (Fiscaliza Brasil, Fiscalize, Voto Distrital, Instagram) em vez de ficar em branco.
- O plano gratuito do Supabase pausa projetos sem nenhum acesso por 7 dias; as visitas à página de links contam como acesso.
- Para criar uma ferramenta privada nova no painel, acrescente um item em `SECTIONS` no `painel.html` e a rota em `route()`.

- O `schema.sql` também cria a tabela de **reportes de erro** (o público envia pela ficha; você lê em `/painel` › Reportes de erro). Se já rodou o arquivo antes, rode de novo: ele não apaga nada.
- Para atualizar os dados, peça ao Claude para recoletar (Câmara, Senado e TSE) e gerar o zip de novo.

- O arquivo `_worker.js` é o pequeno servidor do **ACONTECE AGORA** (rota `/api/noticias`). Ele precisa estar na raiz da pasta enviada ao Cloudflare Pages; o resto do site continua funcionando igual. Ele lê os feeds RSS públicos dos veículos e guarda o resultado por 5 minutos. Se um veículo mudar ou tirar o feed do ar, ele só some da lista (a tela mostra quais estão fora do ar).
