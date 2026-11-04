/* Páginas institucionais: #/metodologia (como cada número é calculado) e #/privacidade (LGPD). */
(function css() {
  const s = document.createElement("style");
  s.textContent = `.doc h2{margin:6px 0 0}.doc p,.doc li{line-height:1.6;max-width:72ch}.doc ul{margin:0;padding-left:20px;display:grid;gap:6px}
  .doc dl{display:grid;gap:12px;margin:0}.doc dt{font-family:var(--f-display);font-weight:700;text-transform:uppercase;letter-spacing:.03em;font-size:.95rem}.doc dd{margin:2px 0 0;color:var(--ink);line-height:1.55;max-width:72ch}
  .doc dd small{color:var(--muted)}`;
  document.head.append(s);
})();

function metodologia() {
  setNav("mais"); document.title = "Como calculamos · Fiscaliza Brasil";
  const item = (t, d) => `<div><dt>${t}</dt><dd>${d}</dd></div>`;
  M.innerHTML = `<section class="card glass doc"><span class="kick">Transparência</span><h1>Como calculamos cada número</h1><span class="fx"></span>
     <p class="muted" style="margin:0">O Fiscaliza Brasil não dá nota, não classifica ninguém como "bom" ou "ruim" e não diz em quem votar. Mostramos dados oficiais e explicamos aqui, sem letra miúda, como cada número é feito. Achou um erro? Use o botão "Reportar erro" na página ou a aba COLABORE.</p></section>
   <section class="card glass doc"><h2>Políticos e votações</h2><dl>
     ${item("Presença nas votações", "Quantas votações nominais do Plenário o parlamentar registrou voto (sim, não, abstenção, obstrução etc.), dividido pelo total de votações desde que ele começou a votar no mandato atual. <small>Não é a mesma coisa que a presença oficial nas sessões, que a Câmara e o Senado calculam por dia.</small>")}
     ${item("Votou com o partido / contra o partido", "Na Câmara, usamos a <b>orientação oficial</b> que o líder do partido (ou da federação ou bloco) registrou em cada votação, e o partido em que o deputado estava <b>no dia</b> da votação. Quando o partido liberou a bancada ou não orientou, vale o voto da maioria dos seus deputados naquele dia. No Senado, que não publica orientação, vale o voto da maioria da bancada. Verde: o parlamentar votou igual ao partido; vermelho: votou diferente. Abstenções e ausências não entram na conta.")}
     ${item("Ranking de fidelidade", "Ordena deputados e senadores pela porcentagem de votos junto com o partido, do menor para o maior. Só entra quem tem pelo menos 30 votos em que o partido teve posição.")}
     ${item("Votou com o governo (Câmara)", "Compara a posição da bancada com a orientação do governo registrada pela Câmara em cada votação.")}
     ${item("Custo do mandato", "Soma o salário (subsídio de R$ 46.366,19 por mês, Decreto Legislativo 172/2022), os gastos reais da cota parlamentar publicados pela Câmara e pelo Senado e os valores máximos da verba de gabinete (R$ 165.806,07) e do auxílio-moradia (R$ 4.253) na Câmara. <small>A verba de gabinete paga os assessores; mostramos o teto porque o gasto individual não é publicado de forma completa.</small>")}
     ${item("Projetos e discursos", "Listas oficiais da Câmara e do Senado, com o resumo (ementa) e os assuntos que a própria Casa publica.")}
     ${item("Patrimônio, votos e campanha", "O que o candidato declarou à Justiça Eleitoral no registro da candidatura, os votos recebidos e a prestação de contas de campanha, todos do TSE. Patrimônio é o declarado pelo próprio candidato, sem correção pela inflação.")}
   </dl></section>
   <section class="card glass doc"><h2>Notícias e assuntos em alta</h2><dl>
     ${item("Acontece agora", "Manchetes dos feeds públicos (RSS) de 16 veículos de diferentes linhas editoriais, com link para a matéria no site de cada um. O Fiscaliza Brasil não escreve nem edita as manchetes.")}
     ${item("Em alta", "Um assunto fica em alta quando vários veículos publicam sobre ele ao mesmo tempo (comparamos as palavras das manchetes) e quando é muito clicado aqui. \"Polêmica\" aparece quando a própria manchete usa palavras como polêmica, ataque ou crítica.")}
     ${item("Em alta no Brasil e No X", "Os termos mais buscados no Brasil vêm do Google Trends. A coluna do X mostra uma lista pública de contas escolhida pelo Fiscaliza Brasil, com veículos e jornalistas de linhas diferentes.")}
   </dl></section>
   <section class="card glass doc"><h2>Economia e instituições</h2><dl>
     ${item("Impostômetro", "Arrecadação federal publicada pela Receita Federal, por ano, estado e tipo de tributo. Não inclui impostos estaduais (ICMS) e municipais (ISS, IPTU).")}
     ${item("Governos lado a lado", "Indicadores oficiais do Banco Central e do IBGE (inflação, PIB, juros, dólar, desemprego, dívida pública), separados por mandato presidencial. Os números dependem também do cenário mundial e de decisões tomadas antes de cada governo.")}
     ${item("Pauta do Congresso e Agenda do STF", "Calendários oficiais publicados pela Câmara, pelo Senado e pelo Supremo Tribunal Federal.")}
     ${item("Partidos", "A descrição de cada partido é um resumo do Fiscaliza Brasil a partir do estatuto e do programa registrados no TSE. O selo mostra a sigla, o número e as cores, e não é a logomarca oficial.")}
     ${item("Dicionário político", "Textos escritos pelo Fiscaliza Brasil em linguagem simples, cada um com a fonte oficial para conferir.")}
   </dl></section>
   <section class="card glass doc"><h2>De onde vêm os dados</h2>
     <ul><li>${FONTE_CAM}</li><li>${FONTE_SEN}</li><li><a href="https://dadosabertos.tse.jus.br/" target="_blank" rel="noopener">TSE · Dados Abertos</a></li><li><a href="https://portal.stf.jus.br/" target="_blank" rel="noopener">Supremo Tribunal Federal</a></li><li><a href="https://www3.bcb.gov.br/sgspub" target="_blank" rel="noopener">Banco Central · SGS</a> e IBGE</li><li><a href="https://www.gov.br/receitafederal/dados" target="_blank" rel="noopener">Receita Federal · Dados Abertos</a></li><li><a href="https://portaldatransparencia.gov.br/" target="_blank" rel="noopener">Portal da Transparência (CGU)</a></li></ul>
     <p class="muted small" style="margin:0">Fotos: TSE, Câmara e Senado, guardadas em cache pelo Fiscaliza Brasil para carregar mais rápido.</p></section>`;
}

function privacidade() {
  setNav("mais"); document.title = "Privacidade · Fiscaliza Brasil";
  M.innerHTML = `<section class="card glass doc"><span class="kick">Privacidade</span><h1>Política de privacidade</h1><span class="fx"></span>
     <p class="muted" style="margin:0">Atualizada em 4 de novembro de 2026. O Fiscaliza Brasil é uma plataforma independente mantida por Abraão Nery (<a href="https://www.instagram.com/oabraaonery/" target="_blank" rel="noopener">@oabraaonery</a>), responsável pelo tratamento dos dados descritos aqui, nos termos da Lei Geral de Proteção de Dados (Lei 13.709/2018).</p></section>
   <section class="card glass doc"><h2>Você pode usar o site sem se identificar</h2>
     <p style="margin:0">Para ver políticos, partidos, votações e notícias não é preciso criar conta nem informar nenhum dado.</p></section>
   <section class="card glass doc"><h2>O que guardamos e por quê</h2><dl>
     <div><dt>Contador de acessos</dt><dd>Um código aleatório de sessão, criado no seu navegador, para contar acessos e mostrar quantas pessoas estão no site agora. Não identifica você e é apagado do servidor em até 15 minutos.</dd></div>
     <div><dt>Cliques nas manchetes</dt><dd>Endereço, título e veículo da notícia clicada e a data, para montar as "mais clicadas". Não guardamos quem clicou.</dd></div>
     <div><dt>Reportar erro e COLABORE</dt><dd>A mensagem que você escreve e, se quiser, nome e contato, só para responder. Não publicamos nem compartilhamos.</dd></div>
     <div><dt>ACOMPANHAR sem entrar</dt><dd>A lista fica guardada apenas no seu aparelho (no navegador). Não vai para o nosso servidor.</dd></div>
     <div><dt>ACOMPANHAR com e-mail</dt><dd>Se você escolher entrar, guardamos o seu e-mail e a lista do que você acompanha, para mostrar a lista em todos os seus aparelhos. Base legal: o seu consentimento. Você pode sair ou apagar a conta a qualquer momento na própria página ACOMPANHANDO, e os dados são apagados.</dd></div>
     <div><dt>Doações por Pix</dt><dd>O pagamento acontece no aplicativo do seu banco. O site não recebe nem guarda dados de pagamento. Como em qualquer Pix, o recebedor vê o nome de quem enviou no extrato; não divulgamos doadores.</dd></div>
   </dl></section>
   <section class="card glass doc"><h2>Serviços que usamos</h2>
     <ul><li><b>Cloudflare</b>: hospedagem do site e cache das fotos.</li><li><b>Supabase</b> (servidores em São Paulo): banco de dados e login por e-mail.</li><li><b>Google Fonts</b> e <b>jsDelivr</b>: fontes e bibliotecas do site, que recebem o endereço de IP do seu navegador ao carregar.</li><li><b>X (Twitter)</b>: só na coluna "No X agora", que é carregada pelo próprio X e segue a política de privacidade dele.</li></ul>
     <p style="margin:0">Não vendemos dados, não usamos anúncios e não usamos cookies de rastreamento.</p></section>
   <section class="card glass doc"><h2>Seus direitos</h2>
     <p style="margin:0">Você pode pedir para confirmar, ver, corrigir ou apagar os seus dados e retirar o consentimento quando quiser (art. 18 da LGPD). Peça pela aba <a href="#/colabore">COLABORE</a> ou pelo Instagram <a href="https://www.instagram.com/oabraaonery/" target="_blank" rel="noopener">@oabraaonery</a>.</p>
     <p class="muted small" style="margin:0">Os dados sobre políticos mostrados no site são públicos e vêm de fontes oficiais. Veja <a href="#/metodologia">Como calculamos</a>.</p></section>`;
}
