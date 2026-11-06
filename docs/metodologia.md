# 3 METODOLOGIA

## 3.1 Tipo e Natureza da Pesquisa

A presente pesquisa classifica-se como aplicada, de natureza extensionista e com abordagem quali-quantitativa. A investigação não se restringe à produção de conhecimento teórico: converte os resultados em uma ferramenta computacional de uso direto pela comunidade, materializando o compromisso social que fundamenta a extensão universitária e os Objetivos de Desenvolvimento Sustentável (ODS) 3 e 10. Quanto aos objetivos, a pesquisa é exploratória e descritiva; quanto ao procedimento técnico, adota o desenvolvimento experimental de software, conduzido de forma iterativa e incremental.

A dimensão qualitativa manifesta-se na análise do contexto de acesso a medicamentos, na modelagem da jornada econômica do paciente e na inspeção funcional e heurística da interface. A dimensão quantitativa expressa-se na mensuração da economia financeira potencial obtida nos cenários de teste, na verificação da aderência dos preços praticados ao teto regulatório da CMED e nos indicadores de cobertura e acurácia do mecanismo de normalização de medicamentos. A combinação das duas abordagens permite não apenas demonstrar a viabilidade técnica do Cura Custo, mas também evidenciar seu potencial de impacto socioeconômico junto à população.

## 3.2 Etapas do Projeto

O desenvolvimento foi organizado em oito etapas encadeadas, nas quais cada fase fornece insumos para a seguinte:

1. **Levantamento de requisitos e definição do escopo** — identificação das necessidades informacionais do paciente, mapeamento das bases públicas disponíveis e análise das lacunas de sistemas correlatos, notadamente o protótipo PharmaPrice (DUARTE; MORAES, 2026).
2. **Obtenção e tratamento das bases públicas** — download, leitura e higienização da planilha oficial de preços da CMED/ANVISA e da Relação Nacional de Medicamentos Essenciais (RENAME).
3. **Construção do catálogo normalizado de medicamentos** — estruturação de uma base local que relaciona nome comercial, princípio ativo segundo a Denominação Comum Brasileira (DCB), apresentação, laboratório, tipo de produto (referência, genérico ou similar) e preço-teto aplicável à Unidade Federativa (Mato Grosso do Sul).
4. **Implementação dos coletores automatizados** — desenvolvimento dos módulos de *Web Scraping* em Python responsáveis pela captura de preços reais nas redes farmacêuticas selecionadas.
5. **Desenvolvimento do motor de otimização de receitas** — implementação das regras de priorização da gratuidade no SUS/Farmácia Popular e de seleção das alternativas genéricas ou similares de menor custo.
6. **Construção da interface web** — elaboração do fluxo de entrada da receita médica e do relatório comparativo consolidado utilizando o framework Streamlit.
7. **Verificação funcional e validação por cenários** — execução de baterias de testes a partir de prescrições simuladas representativas de tratamentos contínuos e preparação da demonstração extensionista para a Mostra Científica.
8. **Análise dos resultados e síntese** — consolidação dos dados quantitativos e qualitativos, identificação de limitações técnicas e proposição de trabalhos futuros.

## 3.3 Fontes de Dados e Procedimentos de Coleta

### 3.3.1 Base Regulatória de Preços (CMED/ANVISA)

A base regulatória é obtida a partir das planilhas públicas de Preço Máximo ao Consumidor (PMC) disponibilizadas pela Câmara de Regulação do Mercado de Medicamentos (CMED), vinculada à ANVISA (BRASIL, 1999; DUARTE; MORAES, 2026). Esses arquivos reúnem substância ativa, produto comercial, apresentação, laboratório, código GGREM, tipo de produto (referência, genérico ou similar, quando aplicável na base regulatória) e o teto tarifário por Unidade Federativa, considerando as diferentes alíquotas estaduais de ICMS — selecionando-se, para o recorte deste projeto em Mato Grosso do Sul, a coluna correspondente à alíquota interna vigente no estado (17% na tabela padrão da CMED, observadas eventuais desonerações específicas registradas na planilha). O tratamento desses dados é feito com a biblioteca `pandas`, que realiza a leitura, a padronização de colunas e a limpeza de registros inconsistentes, resultando em um catálogo local armazenado em banco SQLite. Esse catálogo cumpre dupla função: serve como referência normativa de teto legal e como fonte primária para o mapeamento entre nomes comerciais e princípios ativos.

### 3.3.2 Base de Gratuidade (RENAME e Programa Farmácia Popular)

A verificação de gratuidade apoia-se na RENAME, que lista os medicamentos essenciais disponibilizados pela rede pública, e na relação de itens do Programa Farmácia Popular do Brasil. O cruzamento é feito pelo princípio ativo (DCB) e pela apresentação, de modo que o sistema possa, antes de qualquer consulta de preço no varejo, orientar o usuário sobre a possibilidade de retirada gratuita. Essa etapa é central para o caráter assistencial do projeto, pois direciona prioritariamente as famílias de menor renda à rede pública, em consonância com as evidências da PNAUM de que cerca de 50% a 52,8% dos medicamentos genéricos utilizados pelas classes econômicas C, D e E são obtidos gratuitamente no SUS (BERTOLDI et al., 2016).

### 3.3.3 Coleta Automatizada de Preços no Varejo (Web Scraping)

Para os medicamentos que exigem aquisição privada, a coleta de preços é realizada por *Web Scraping*, técnica que converte conteúdo HTML em registros estruturados e passíveis de processamento analítico (MITCHELL, 2019; GRACIANO; RAMALHO, 2023). Foram selecionadas duas redes com presença nacional e forte cobertura física e digital no município de Campo Grande/MS: Drogasil (grupo RD Saúde) e Pague Menos. A escolha justifica-se pela representatividade comercial de ambas no mercado local e pela disponibilidade de catálogo e preços em seus portais de comércio eletrônico.

A coleta adota estratégia híbrida em Python: utiliza-se `requests` em conjunto com `BeautifulSoup` para páginas ou endpoints cujo conteúdo é entregue de forma estática e, como alternativa para páginas que renderizam preços dinamicamente via JavaScript e requisições assíncronas (Ajax), emprega-se a automação de navegador via `Selenium WebDriver` em modo *headless* (MITCHELL, 2019). Os resultados são normalizados em uma estrutura comum contendo nome do produto, princípio ativo, apresentação, laboratório, preço praticado, rede farmacêutica e data/hora (*timestamp*) da coleta.

Para garantir estabilidade operacional e uso responsável, o coletor observa diretrizes de boas práticas de raspagem (MITCHELL, 2019), aplicando intervalos de espera entre requisições (*throttling*), cabeçalhos de identificação (*User-Agent*) e armazenamento em *cache* local no SQLite com tempo de expiração configurável, reduzindo a carga sobre os servidores consultados. Adicionalmente, considerando que grandes portais do varejo farmacêutico empregam mecanismos de proteção automatizada (*Web Application Firewalls*, Cloudflare e bloqueios dinâmicos) que podem recusar conexões em tempo real, a arquitetura implementa um mecanismo de contingência (*fallback*): na hipótese de indisponibilidade temporária ou bloqueio da requisição ao vivo, o sistema recorre automaticamente à última cotação válida registrada no *cache* local (ou a snapshots previamente coletados das mesmas redes), sinalizando na interface a data e a hora de referência daquele preço. A dispersão de preços entre redes, documentada na literatura nacional (SOUZA; PARANHOS; HASENCLEVER, 2021), reforça a necessidade dessa comparação sistematizada em vez da busca manual pelo paciente.

## 3.4 Tecnologias e Ferramentas

O sistema é integralmente desenvolvido em linguagem Python, escolhida pelo ecossistema maduro para coleta e tratamento de dados (MITCHELL, 2019; GRACIANO; RAMALHO, 2023) e pela produtividade no desenvolvimento de aplicações web. A interface é construída com o framework **Streamlit**, que permite gerar painéis interativos e relatórios visuais responsivos com baixo custo de implementação, adequados à demonstração em Mostra Científica e à operação intuitiva por usuários não técnicos. O armazenamento utiliza **SQLite**, banco de dados relacional leve e embarcado que dispensa infraestrutura de servidor dedicado. Para a coleta, empregam-se `requests`, `BeautifulSoup` e `Selenium WebDriver`; para o tratamento tabular e higienização das bases oficiais, `pandas`; e, para o mapeamento entre nomes comerciais e princípios ativos, técnicas de correspondência aproximada de cadeias de caracteres (*fuzzy matching*), que toleram variações de grafia, acentuação e abreviações presentes na digitação das receitas.

## 3.5 Procedimentos de Desenvolvimento

O desenvolvimento segue uma arquitetura modular em cinco camadas, com separação de responsabilidades, de modo a facilitar a manutenção, os testes e a expansão futura:

- **Camada de dados** — responsável pela ingestão das bases CMED e RENAME, pela persistência em SQLite e pelo gerenciamento do catálogo normalizado e do *cache* de cotações.
- **Camada de coleta** — composta pelos módulos de *Web Scraping* da Drogasil e da Pague Menos, isolados por uma interface comum de saída e dotados de tratamento de exceções e *fallback* para *cache*, permitindo adicionar novas farmácias sem alterar o núcleo do sistema.
- **Camada de regras de negócio** — concentra a verificação de gratuidade (RENAME/Farmácia Popular), a validação do preço praticado frente ao PMC estadual (17%) e a lógica de correspondência Nome Comercial → DCB.
- **Camada de otimização** — implementa o algoritmo que, para a cesta de medicamentos da receita, seleciona a combinação de menor custo global, priorizando itens gratuitos na rede pública e, quando há aquisição privada, a alternativa genérica ou similar de menor preço verificado.
- **Camada de apresentação** — interface web em Streamlit que recebe os itens da receita, exibe o progresso da consulta e gera o relatório comparativo consolidado com percentuais de economia e alertas regulatórios.

## 3.6 Procedimentos de Avaliação e Validação

Por não envolver recrutamento de participantes nem coleta de dados pessoais ou clínicos de seres humanos, a validação desta etapa do projeto não demanda submissão a Comitê de Ética em Pesquisa (CEP); caso a investigação evolua em trabalhos futuros para testes de usabilidade com pacientes reais, o protocolo será submetido previamente à apreciação ética competente, em conformidade com a Resolução CNS nº 510/2016. Assim, a verificação do sistema é conduzida em ambiente controlado pela própria equipe de desenvolvimento, combinando **avaliação empírica por cenários simulados** e **inspeção funcional/heurística da interface**.

Para a avaliação quantitativa, são elaborados cenários de teste baseados em prescrições médicas padronizadas de tratamentos contínuos de alta prevalência na atenção básica brasileira (como hipertensão arterial sistêmica, diabetes mellitus tipo 2 e dislipidemias, cujos fármacos figuram entre os mais utilizados na PNAUM segundo Bertoldi et al., 2016). Os indicadores quantitativos aferidos sobre esses cenários são:

- **Economia potencial total e percentual** — diferença financeira entre o custo de aquisição integral dos medicamentos de referência prescritos e o custo da rota otimizada indicada pelo Cura Custo (integrando gratuidade via RENAME/Farmácia Popular e genéricos de menor preço);
- **Aderência ao PMC** — verificação da exatidão do cálculo do teto estadual e acionamento correto dos alertas diante de ofertas com preço superior ao limite da CMED;
- **Cobertura do catálogo e acurácia do mapeamento Nome → DCB** — proporção de itens das receitas de teste corretamente normalizados para seu princípio ativo e precisão na listagem de seus equivalentes;
- **Desempenho e resiliência da coleta** — tempo médio de execução da consulta (em coleta direta e via recuperação de *cache*) e taxa de sucesso dos coletores frente às proteções dos portais consultados.

A avaliação qualitativa consiste na inspeção funcional do fluxo de telas no Streamlit, verificando a clareza visual dos alertas de teto legal, a distinção imediata entre itens gratuitos e pagos e a compreensibilidade do resumo de economia. Por fim, as funcionalidades entregues são confrontadas sistematicamente com o protótipo PharmaPrice (DUARTE; MORAES, 2026), documentando as lacunas supridas pelo Cura Custo.

## 3.7 Aspectos Éticos e Legais

O projeto observa os princípios de finalidade, adequação, necessidade (minimização) e segurança estabelecidos pela Lei Geral de Proteção de Dados Pessoais — LGPD, Lei nº 13.709/2018 (BRASIL, 2018). Reconhecendo que informações relativas a prescrições medicamentosas podem configurar dados pessoais sensíveis referentes à saúde quando vinculadas a uma pessoa natural (art. 5º, inciso II, da LGPD), a arquitetura do Cura Custo adota a privacidade desde a concepção (*privacy by design*): o sistema não exige cadastro ou identificação do usuário, processa a lista de medicamentos exclusivamente em memória volátil durante a sessão ativa, não registra *logs* contendo as combinações de fármacos pesquisadas e descarta os dados de entrada imediatamente após a emissão do relatório em tela.

Na camada de coleta, o *Web Scraping* restringe-se estritamente a dados públicos de preços de produtos, sem captura de informações pessoais, operando com limitação de taxa de requisições (*rate limiting*) e uso prioritário de *cache* para não impactar a disponibilidade dos portais consultados (MITCHELL, 2019). Por fim, em conformidade com a legislação sanitária vigente (BRASIL, 1999), o sistema exibe aviso explícito em sua interface e nos relatórios gerados destacando que a ferramenta possui caráter exclusivamente informativo e educativo sobre preços e políticas públicas de acesso, não substituindo a prescrição médica nem a orientação farmacêutica presencial quanto à intercambialidade segura de medicamentos.
