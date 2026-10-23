# Posts automáticos · Leandro Cruz Eletricista

Este repositório guarda as artes (cards e Reels) dos posts do Instagram **@leandrocruz.eletrica** e o manual da rotina semanal que publica no Instagram e no Google Meu Negócio pelo Metricool.

Quem lê este arquivo é o Claude rodando a tarefa agendada. Siga o passo a passo abaixo do começo ao fim sem pedir aprovação: o Leandro pediu publicação 100% automática.

## Dados fixos

- Leandro Cruz, eletricista residencial em **Santa Teresa (ES)**, atende também cidades vizinhas (Santa Maria de Jetibá, Itarana, São Roque do Canaã, Itaguaçu, Fundão e região).
- WhatsApp: **(27) 99855-6375**. Instagram: @leandrocruz.eletrica.
- Metricool: brand/blogId **7610648**, fuso **America/Sao_Paulo**. Redes: Instagram e Google Meu Negócio ("gmb"). Plano **Free**: limite de **20 posts agendados por mês**.
- Imagens e vídeos: publicados neste repositório público; o Metricool lê pelo link
  `https://raw.githubusercontent.com/leandro07eletrica-cloud/posts-eletrica/main/<pasta>/<arquivo>`
- Pasta do Google Drive para fotos reais de serviço: **"Posts Leandro Elétrica"** (id `1qIC-Fu-1xT4H8fV1AGQWT8ZODJzxlDU1`).

## Serviços que o Leandro quer vender (prioridade)

1. Falta de energia e diagnóstico de pane
2. Fuga de corrente (conta alta, choquinho, DR desarmando)
3. Instalação e troca de quadro de distribuição (QDC), disjuntores, DR e DPS
4. Padrão de entrada e alimentação do padrão até a casa
5. Chuveiro, tomadas, iluminação, manutenção em geral

## Tom e regras de texto

- Escreva como se fosse o próprio Leandro falando, em primeira pessoa: humano, direto, profissional, sem exagero de venda.
- **Nunca use travessão (—) como separador de lista.** Use listas numeradas "1." ou frases normais.
- Sempre com palavras-chave de SEO local: eletricista, eletricista em Santa Teresa, Santa Teresa ES, região serrana do ES, além do termo técnico do tema (quadro de distribuição, fuga de corrente, padrão de entrada etc.).
- Informação técnica correta e prudente. Nunca ensine o leitor a mexer em parte energizada; a mensagem é "reconheça o sinal e chame um eletricista". Nada de promessa de preço ou garantia.
- Sem emoji em excesso (no máximo 1 ou 2 por legenda, opcional).
- **Instagram:** legenda de 700 a 1.200 caracteres, abre com a pergunta/gancho, lista curta, fecha com chamada para o WhatsApp e 7 a 10 hashtags (sempre inclua #eletricista #eletricistasantateresa #santateresaes #eletricistaes).
- **Google Meu Negócio:** texto de 500 a 1.200 caracteres, sem hashtags, mencionando "eletricista em Santa Teresa (ES)" e "cidades vizinhas", fecha com "Orçamento pelo WhatsApp: (27) 99855-6375".

## Calendário semanal

A tarefa roda toda **segunda de manhã** e agenda a semana:

| Dia | Horário | Instagram | Google Meu Negócio |
|---|---|---|---|
| Segunda | 18:30 | **Card** (POST com imagem) | Texto do mesmo tema + imagem do card |
| Quinta | 18:30 | **Reels** (vídeo animado com música) | Texto do mesmo tema + capa do Reels |

São 4 posts por semana. **Controle do limite:** some no `historico.md` quantos posts já foram agendados no mês de cada data. Se agendar os 4 fizer o mês passar de **19**, corte primeiro o texto do Google Meu Negócio de quinta; se ainda passar, corte o de segunda. Nunca passe de 19 no mês (deixa 1 de folga para algo que o Leandro peça).

## Como escolher os temas

1. Leia `historico.md` e **não repita** um tema das últimas 6 semanas.
2. Alterne entre os serviços prioritários; pelo menos 1 dos 2 temas da semana deve ser dos itens 1 a 4.
3. Pense na época do ano no Espírito Santo: verão (nov a mar) é tempo de chuva forte, raio e queda de energia, ar-condicionado e conta alta; inverno (jun a ago) é chuveiro no talo e disjuntor caindo.
4. Banco de ideias (use e invente outros no mesmo espírito):
   - Casa antiga sem DR: por que o DR salva vidas
   - Quadro de distribuição velho, com fusível ou desorganizado: sinais de que é hora de trocar
   - DPS: protege seus aparelhos dos raios
   - Tomada esquentando ou escurecida
   - Luz piscando sozinha
   - Benjamim e extensão: o perigo da gambiarra
   - Chuveiro com cheiro de queimado
   - Padrão de entrada: o que a concessionária exige (EDP ES) e por que fazer certo
   - Fiação antiga de casa reformada
   - Faltou energia só na sua casa: o que conferir antes de ligar para a concessionária
   - Ar-condicionado precisa de circuito exclusivo
   - Aterramento: para que serve
5. **Fotos reais têm prioridade.** Antes de criar o card de segunda, procure na pasta do Drive arquivos de imagem novos (posteriores à última execução registrada no histórico). Se houver foto real de serviço, use-a no post de segunda no lugar do card: legenda de "serviço realizado" baseada no que dá para ver na foto, sem inventar detalhes que não aparecem. Para isso, baixe o arquivo (Drive `download_file_content`), salve em `fotos/AAAA-MM-DD-tema.jpg`, faça commit e use o link raw. Se não conseguir baixar, siga com o card normal e avise no resumo.

## Passo a passo da execução

1. **Repositório:** se este repositório não estiver no ambiente, anexe com `add_repo` (owner `leandro07eletrica-cloud`, repo `posts-eletrica`, access `push`) e clone. Rode `git pull` antes de começar.
2. **Situação:** chame o Metricool `getScheduledPosts` (brandId 7610648) para a semana atual. Se já houver post agendado para segunda ou quinta desta semana, não duplique aquele dia.
3. **Datas:** segunda e quinta da semana corrente, 18:30 America/Sao_Paulo. Se a segunda 18:30 já passou, use terça 18:30.
4. **Specs:** escreva `specs/AAAA-MM-DD-tema.json` para o card e para o Reels, no formato de `specs/exemplo-card.json` e `specs/exemplo-reel.json` (veja o cabeçalho de `gerar.py`). Títulos curtos (2 ou 3 linhas de até ~18 caracteres), 3 itens de no máximo ~60 caracteres. Varie `musica` entre 0 e 3.
5. **Gerar:** `python3 gerar.py specs/<card>.json specs/<reel>.json`. Abra o PNG do card e o PNG de capa do Reels (`reels/<arquivo>-capa.png`) com a ferramenta de leitura de imagem e confira: nada cortado, nada sobreposto ao rodapé, texto em português correto. Se algo estiver ruim, encurte o texto do spec e gere de novo (no máximo 2 tentativas).
6. **Publicar arquivos:** `git add` de specs, cards e reels; commit com mensagem curta; `git push origin main`.
7. **Agendar no Metricool** com `createScheduledPost`, `draft: false`, `autoPublish: true`:
   - Segunda, Instagram: `instagramData.type = "POST"`, `media` = link raw do PNG, `mediaAltText` descrevendo o card.
   - Quinta, Instagram: `instagramData.type = "REEL"`, `showReelOnFeed: true`, `media` = link raw do MP4, `videoCoverMilliseconds` = 500 ms antes do fim do vídeo.
   - Cada dia, Google Meu Negócio: `providers [{"network":"gmb"}]`, `gmbData.type = "publication"`, texto **com imagem**: na segunda, `media` = o mesmo PNG do card (ou a foto real); na quinta, `media` = a capa do Reels (`reels/<arquivo>-capa.png`), porque post de texto do Google não aceita vídeo. Nunca mande post do Google sem imagem.
   - `isAiGenerated: false` nos cards e Reels (são artes gráficas, não imagem realista gerada por IA). Se um dia usar imagem realista gerada por IA, marque `true`.
   - Se o Metricool recusar por limite do plano, não insista: registre no histórico e avise no resumo.
8. **Histórico:** acrescente as linhas da semana em `historico.md` (data, rede, formato, tema, link do Metricool) e atualize a contagem do mês. Commit e push.
9. **Resumo final** (é o que chega no celular do Leandro), curto e em português, sem jargão técnico:
   - "Posts da semana agendados ✅" e a lista: dia, horário, rede, tema.
   - Se usou foto dele, diga qual.
   - Qualquer problema em uma frase, com o que ele precisa fazer (se precisar).

## Se algo falhar

- Metricool sem acesso / conector desligado: não gere nada, avise no resumo que é preciso reconectar o Metricool no Claude.
- Push recusado no GitHub: avise que o app do Claude no GitHub precisa ser reinstalado para o repositório posts-eletrica.
- Erro na geração de vídeo: agende só o card de segunda e os textos do Google, e avise.
