# 📘 Manual Completo de Execução e Deploy
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Para quem é este manual:** qualquer pessoa que precise rodar este projeto —
desde quem nunca abriu um terminal até quem já é engenheiro de dados e só
quer o comando certo. As seções "🎓 Explicando" são para quem está
começando; quem já sabe pode pular direto para os blocos de código.

---

## 📋 Sumário

1. [TL;DR — Para Quem Já Sabe](#1-tldr--para-quem-já-sabe)
2. [Visão Geral da Arquitetura](#2-visão-geral-da-arquitetura)
3. [Parte 1 — Preparando o Ambiente Local](#3-parte-1--preparando-o-ambiente-local)
4. [Parte 2 — Executando os Notebooks (NB00→NB07)](#4-parte-2--executando-os-notebooks-nb00nb07)
5. [Parte 3 — Testando Localmente (API + Dashboard)](#5-parte-3--testando-localmente-api--dashboard)
6. [Parte 4 — Deploy em Produção](#6-parte-4--deploy-em-produção)
7. [Parte 5 — Automação e Atualização em Tempo Real](#7-parte-5--automação-e-atualização-em-tempo-real)
8. [Parte 6 — Troubleshooting Consolidado](#8-parte-6--troubleshooting-consolidado)
9. [Cheat Sheet de Comandos](#9-cheat-sheet-de-comandos)

---

## 1. TL;DR — Para Quem Já Sabe

```bash
# Ambiente
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Pipeline completo (ordem obrigatória)
jupyter nbconvert --to notebook --execute --inplace notebooks/NB0{0,1,2,3,4,5,6,7}_*.ipynb

# Pré-flight check
python scripts/preflight_check.py

# Commit dos dados Gold (necessário — Render/Streamlit Cloud são stateless)
git add -f data/gold/ data/external/ data/silver/
git commit -m "data refresh" && git push

# Local — API
uvicorn api.app:app --reload --port 8000

# Local — Dashboard (lê Parquet local, API_BASE_URL vazia)
streamlit run dashboard/Home.py

# Produção — Dashboard consumindo API
API_BASE_URL="https://SUA-API.onrender.com" streamlit run dashboard/Home.py
```

**Deploy:** Render via `render.yaml` (Blueprint) → Streamlit Cloud apontando
`API_BASE_URL` nos Secrets → atualizar `ALLOWED_ORIGINS` no Render com a URL
final do Streamlit. Atualização de dados é **manual**, via GitHub Actions
`workflow_dispatch` (botão "Run workflow"), não cron. Detalhes na Parte 7.

---

## 2. Visão Geral da Arquitetura

### 🎓 Explicando

Pense neste projeto como uma linha de produção em 3 estágios:

1. **Fábrica de dados** (os 8 notebooks Jupyter, NB00→NB07) — roda na sua
   máquina (ou no GitHub Actions), processa notícias e gera arquivos prontos.
2. **Depósito** (pastas `data/gold/`, dentro do próprio repositório Git) —
   onde os arquivos prontos ficam guardados.
3. **Vitrine** (API no Render + Dashboard no Streamlit Cloud) — onde quem
   acessa de fora vê o resultado, sem precisar saber rodar Python.

```
┌─────────────────────────────────────────────────────────────┐
│  SUA MÁQUINA (ou GitHub Actions)                            │
│  Jupyter: NB00 → NB01 → ... → NB07                          │
│  Gera: data/gold/*.parquet, *.pkl, *.npz, *.faiss            │
└───────────────────────┬───────────────────────────────────────┘
                        │ git push
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  GITHUB (repositório)                                        │
│  Guarda o código E os dados Gold (commitados)                │
└───────────┬───────────────────────────────┬───────────────────┘
            │ auto-deploy                  │ auto-deploy
            ▼                              ▼
┌───────────────────────┐      ┌───────────────────────────┐
│  RENDER               │      │  STREAMLIT COMMUNITY CLOUD │
│  api/app.py            │◄────│  dashboard/Home.py         │
│  Lê data/gold/ do repo  │ HTTP│  Chama a API via requests   │
└───────────────────────┘      └───────────────────────────┘
```

**Ponto-chave que costuma confundir:** os notebooks **não rodam** dentro do
Render ou do Streamlit Cloud. Essas duas plataformas só **servem** o que já
foi processado e guardado no Git. Quem processa é você, na sua máquina (ou
via GitHub Actions, na Parte 7).

---

## 3. Parte 1 — Preparando o Ambiente Local

### 3.1 — O que você precisa instalar

| Ferramenta | Para quê | Versão mínima |
|---|---|---|
| Python | Rodar os notebooks, a API e o dashboard | 3.10+ (recomendado 3.11) |
| Java (JDK) | PySpark depende disso internamente | 11+ |
| Git | Clonar o repositório, fazer commits | qualquer versão recente |

### 🎓 Explicando: o que é "terminal"?

Terminal (ou "prompt de comando", "shell", "console") é uma janela de texto
onde você digita comandos em vez de clicar em ícones. Todo comando deste
manual deve ser digitado ali, seguido de Enter.

- **Windows:** abra o "PowerShell" ou "Prompt de Comando" (busque na barra
  de pesquisa do Windows).
- **Mac:** abra o app "Terminal" (Spotlight → digite "Terminal").
- **Linux:** geralmente `Ctrl+Alt+T`.

Quando você ver um bloco assim:
```bash
python --version
```
significa: digite exatamente isso (sem o `$` se houver) e pressione Enter.

### 3.2 — Verificando o que já está instalado

```bash
python3 --version      # deve mostrar 3.10 ou mais
java -version           # deve mostrar 11 ou mais
git --version           # qualquer versão
```

Se algum desses comandos der erro ("comando não encontrado"), instale:

**Python:**
- Windows/Mac: baixe em [python.org/downloads](https://www.python.org/downloads/)
- Linux (Ubuntu/Debian): `sudo apt install python3.11 python3.11-venv`

**Java (JDK 11):**
- Windows: baixe o "Temurin 11" em [adoptium.net](https://adoptium.net/)
- Mac: `brew install openjdk@11`
- Linux: `sudo apt install openjdk-11-jdk`

**Git:**
- Windows: [git-scm.com/download/win](https://git-scm.com/download/win)
- Mac: já vem instalado, ou `brew install git`
- Linux: `sudo apt install git`

### 3.3 — Clonando o projeto

### 🎓 Explicando: o que é "clonar"?

"Clonar" significa baixar uma cópia completa do projeto (código + histórico)
do GitHub para o seu computador.

```bash
git clone <URL-DO-REPOSITORIO>
cd <nome-da-pasta-do-projeto>
```

> 📌 A `<URL-DO-REPOSITORIO>` será adicionada aqui quando você compartilhar o
> link definitivo (ver seção "Repositório e Links" do README principal).

### 3.4 — Criando o ambiente virtual

### 🎓 Explicando: por que um "ambiente virtual"?

Um ambiente virtual é uma "caixa isolada" só para as bibliotecas Python
deste projeto — assim elas não brigam com outras versões instaladas no seu
computador para outros projetos.

```bash
# Criar o ambiente (uma vez só)
python3 -m venv .venv

# Ativar o ambiente (toda vez que for trabalhar no projeto)
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows (PowerShell ou CMD)
```

Quando ativado, o início da linha do terminal muda para mostrar `(.venv)` —
é assim que você sabe que está "dentro da caixa" certa.

> ⚠️ Você precisa **reativar** o ambiente virtual toda vez que abrir um novo
> terminal. Se os comandos começarem a dar erro de "módulo não encontrado",
> o primeiro passo é checar se `(.venv)` aparece no início da linha.

### 3.5 — Instalando as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Isso vai demorar entre 2 e 8 minutos na primeira vez (instala PySpark,
scikit-learn, Streamlit, FastAPI e — se você for usar a Camada 3 de busca
semântica — `sentence-transformers` e `faiss-cpu`, que são mais pesados).

### 3.6 — Configurando variáveis de ambiente (.env)

```bash
cp .env.example .env
```

Abra o arquivo `.env` num editor de texto (Notepad, VS Code, qualquer um) e
preencha:

| Variável | Obrigatória? | Onde conseguir |
|---|---|---|
| `GROQ_API_KEY` | Não (mas sem ela o chatbot roda em "modo demo") | [console.groq.com](https://console.groq.com) — gratuito |
| `REDDIT_CLIENT_ID` / `SECRET` | Não (NB01 tem fallback automático) | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |

> 🔒 **Nunca** compartilhe ou comite o arquivo `.env` — ele já está protegido
> no `.gitignore`. Use sempre `.env.example` como modelo público.

---

## 4. Parte 2 — Executando os Notebooks (NB00→NB07)

### 🎓 Explicando: por que a ordem importa?

Cada notebook **lê o resultado** do anterior. NB04 não funciona sem o Silver
que o NB02 gerou; NB07 não funciona sem os resultados de NB03, NB04, NB05 e
NB06. É como montar um móvel seguindo o manual — pular um passo trava o
próximo.

### 4.1 — Abrindo o Jupyter

```bash
jupyter lab notebooks/
```

Isso abre uma aba no seu navegador com a lista de notebooks. Clique duas
vezes em `NB00_setup.ipynb` para abrir o primeiro.

### 🎓 Explicando: como rodar um notebook

Dentro do Jupyter, cada notebook é dividido em "células". Para rodar uma
célula: clique nela e pressione `Shift + Enter` (vai para a próxima
automaticamente). Para rodar **todas as células de uma vez**, use o menu
**Run → Run All Cells**.

### 4.2 — Tabela de execução (ordem obrigatória)

| # | Notebook | O que faz | Duração estimada | Atenção |
|---|---|---|---|---|
| 1 | `NB00_setup.ipynb` | Instala dependências, cria `config/settings.py`, `api/app.py`, `dashboard/Home.py`, `groq_client.py` | ~2-5 min | Primeira execução baixa pacotes — pode demorar mais |
| 2 | `NB01_bronze_ingestion.ipynb` | Coleta ao vivo das 21 fontes (RSS + scraping + Google News) | ~15-30 min | Depende da sua internet; algumas fontes podem falhar (normal, tem fallback) |
| 3 | `NB02_bronze_to_silver.ipynb` | Limpa e normaliza o texto coletado | ~5 min | — |
| 4 | `NB03_word_count_mapreduce.ipynb` | Conta palavras via PySpark (MapReduce) | ~5 min | — |
| 5 | `NB04_tfidf_bm25.ipynb` | Constrói os 3 índices de busca (TF-IDF, BM25, FAISS) | ~10-20 min | Camada FAISS baixa um modelo de ~120MB na primeira vez |
| 6 | `NB05_contextual_sentiment.ipynb` | Calcula sentimento via léxico FII PT-BR | ~10 min | — |
| 7 | `NB06_marketing_intelligence.ipynb` | Gera métricas por FII (MI Score) | ~15 min | — |
| 8 | `NB07_dashboard_dataset.ipynb` | Consolida tudo para o dashboard/API | ~5 min | Última etapa — gera os arquivos que a produção vai usar |

**Tempo total estimado:** 1h a 1h30 na primeira execução completa.

### 4.3 — Como saber se um notebook rodou certo

No final de cada notebook há uma célula de validação que imprime algo como:

```
OK  dashboard_articles.parquet
OK  dashboard_fii_signals.parquet
...
🎉 8/8 checks — NB0X COMPLETO
```

Se aparecer `XX` (erro) em vez de `OK`, **não avance** para o próximo
notebook — primeiro resolva o problema (veja a Parte 8, Troubleshooting).

### 4.4 — Executando via linha de comando (sem abrir o Jupyter visualmente)

Útil se você já confia no pipeline e só quer reprocessar rápido:

```bash
for nb in notebooks/NB0{0,1,2,3,4,5,6,7}_*.ipynb; do
  echo "Executando $nb..."
  jupyter nbconvert --to notebook --execute --inplace "$nb"
done
```

---

## 5. Parte 3 — Testando Localmente (API + Dashboard)

### 5.1 — Rodando a API localmente

```bash
uvicorn api.app:app --reload --port 8000
```

Abra no navegador: [http://localhost:8000/docs](http://localhost:8000/docs)
— isso é o **Swagger UI**, uma página automática que lista todos os
endpoints e permite testá-los clicando, sem precisar escrever código.

### 🎓 Explicando: o que é uma "API"?

API aqui significa um pequeno servidor que responde perguntas em formato
JSON (um formato de texto estruturado) quando alguém acessa um endereço
específico. Por exemplo, acessar `http://localhost:8000/health` no navegador
mostra algo como:

```json
{"status": "ok", "version": "1.0.0", "data_available": true}
```

### 5.2 — Rodando o Dashboard localmente

Em **outro** terminal (deixe a API rodando no primeiro):

```bash
source .venv/bin/activate   # se ainda não estiver ativado neste terminal
streamlit run dashboard/Home.py
```

Abre automaticamente em [http://localhost:8501](http://localhost:8501).

Por padrão (sem `API_BASE_URL` definida), o dashboard lê os arquivos Parquet
direto da pasta `data/gold/` — não precisa nem da API rodando para isso.

### 5.3 — Testando o Dashboard consumindo a API local

```bash
API_BASE_URL="http://localhost:8000" streamlit run dashboard/Home.py
```

Isso simula exatamente o comportamento de produção, mas tudo na sua máquina
— útil para detectar problemas antes de fazer o deploy de verdade.

---

## 6. Parte 4 — Deploy em Produção

> Esta seção resume os dois guias dedicados: `DEPLOY_RENDER.md` (API) e
> `DEPLOY_STREAMLIT.md` (Dashboard). Leia-os para o passo a passo completo
> com capturas de tela de cada configuração. Aqui está a visão de conjunto
> e a ordem correta.

### 6.0 — Qual `requirements*.txt` Usar em Cada Cenário

Antes de instalar qualquer coisa, é importante saber que este projeto tem
**4 arquivos de dependências diferentes** — usar o errado no lugar errado
não quebra nada localmente, mas torna o deploy mais lento ou arriscado.

```
fii-intelligence-platform/
├── requirements.txt              ← Notebooks (local, completo, ~56 pacotes)
├── requirements-dev.txt          ← + Jupyter/testes (soma ao acima)
├── requirements-api.txt          ← Deploy da API no Render (~11 pacotes)
└── dashboard/
    ├── Home.py
    └── requirements.txt          ← Deploy do Dashboard no Streamlit Cloud (~7 pacotes)
```

| Cenário | Comando |
|---|---|
| Rodar os notebooks NB00–NB07 | `pip install -r requirements.txt` |
| Desenvolver + testar + lint | `pip install -r requirements.txt -r requirements-dev.txt` |
| Testar a API localmente (ambiente leve) | `pip install -r requirements-api.txt` |
| Testar o Dashboard localmente (ambiente leve) | `pip install -r dashboard/requirements.txt` |
| Deploy da API no Render | Automático — `render.yaml` já aponta para `requirements-api.txt` |
| Deploy do Dashboard no Streamlit Cloud | Automático — Streamlit Cloud detecta `dashboard/requirements.txt` sozinho |

### 🎓 Explicando: por que o dashboard tem um `requirements.txt` próprio?

O Streamlit Community Cloud **não tem** um campo na interface para você
apontar manualmente um arquivo de dependências diferente — ele sempre
procura primeiro **na mesma pasta do arquivo de entrada do app**. Como o
nosso app começa em `dashboard/Home.py`, colocar um `requirements.txt`
dentro da pasta `dashboard/` faz o Streamlit Cloud usá-lo automaticamente,
em vez de cair no `requirements.txt` da raiz (pesado, feito para os
notebooks com PySpark/Torch/Selenium, que o dashboard não usa em produção).

> 📖 **Saiba mais:** explicação completa, incluindo a citação da
> documentação oficial do Streamlit que confirma esse comportamento, e a
> lista de pacotes do `requirements.txt` principal que existem como
> referência futura mas não são usados pelo código atual — em
> [`docs/architecture/REQUIREMENTS_GUIA.md`](docs/architecture/REQUIREMENTS_GUIA.md).

---

### 6.1 — Por que a ordem importa: API primeiro, Dashboard depois

O dashboard em produção precisa de uma URL de API já funcionando para
apontar (`API_BASE_URL`). Fazer ao contrário significa configurar o
dashboard duas vezes.

### 6.2 — Checklist antes de qualquer deploy

```bash
python scripts/preflight_check.py
```

Esse script confere automaticamente:
- Se todos os arquivos Gold necessários existem
- Se eles estão **commitados no Git** (não bloqueados pelo `.gitignore`)
- Se `.env` não está sendo versionado por acidente
- Se o tamanho dos arquivos está dentro do limite do GitHub

Resolva todo item marcado como `FAIL` antes de continuar.

### 6.3 — Commitando os dados Gold

```bash
git add -f data/gold/dashboard/*.parquet data/gold/dashboard/*.json
git add -f data/gold/tfidf_bm25/*.pkl data/gold/tfidf_bm25/*.npz data/gold/tfidf_bm25/*.parquet
git commit -m "chore: dados Gold para deploy"
git push
```

> ⚠️ Se você ativou a Camada 3 (FAISS), também precisa commitar
> `embeddings.npy`, `faiss_index.faiss` e `embedding_config.json`.

### 6.4 — Deploy da API (Render)

Resumo (detalhes completos em `DEPLOY_RENDER.md`):

1. Crie conta no [Render](https://render.com)
2. **New → Blueprint** → conecte o repositório → Render detecta `render.yaml`
3. Configure manualmente o secret `GROQ_API_KEY` (não vai pelo Blueprint)
4. Aguarde o build (~3-6 min) e teste: `curl https://SUA-API.onrender.com/health`

### 6.5 — Deploy do Dashboard (Streamlit Cloud)

Resumo (detalhes completos em `DEPLOY_STREAMLIT.md`):

1. Crie conta no [Streamlit Community Cloud](https://share.streamlit.io)
2. **New app** → repositório → arquivo principal `dashboard/Home.py`
3. Em **Secrets**, adicione:
   ```toml
   API_BASE_URL = "https://SUA-API.onrender.com"
   ```
4. Deploy (~2-5 min) e confira o indicador 🟢 na sidebar do dashboard publicado

### 6.6 — Fechando o ciclo (CORS)

Volte ao Render e atualize:
```
ALLOWED_ORIGINS=https://SEU-APP.streamlit.app
```

---

## 7. Parte 5 — Automação e Atualização em Tempo Real

Esta é provavelmente a pergunta mais importante para entender o que este
sistema **é** e o que ele **não é**.

### 7.1 — Como funciona HOJE

```
Você clica "Run workflow" no GitHub
        ↓
GitHub Actions executa NB00 → NB07 (servidor do GitHub, não o seu)
        ↓
Novo Gold é commitado automaticamente no repositório
        ↓
Render detecta o push → refaz o deploy da API automaticamente
Streamlit Cloud detecta o push → refaz o deploy do dashboard automaticamente
        ↓
Dashboard e API agora servem os dados novos
```

**O gatilho é manual (`workflow_dispatch`), não agendado.** Isso foi uma
decisão deliberada, não uma limitação técnica — ver a justificativa abaixo.

### 7.2 — Qual é a frequência de atualização, na prática?

**A frequência é "sempre que você decidir clicar".** Não existe um número
fixo como "atualiza a cada X horas" — porque não configuramos um agendamento
(`cron`). Cada execução do workflow processa as notícias publicadas **até o
momento exato em que você clicou**, e isso fica congelado até a próxima vez
que alguém disparar o workflow de novo.

### Como disparar manualmente

1. Vá até a aba **Actions** do repositório no GitHub
2. Clique em **"Atualizar Dados FII (Manual)"** na lista de workflows
3. Clique no botão **"Run workflow"** (canto superior direito)
4. (Opcional) escreva um motivo no campo de texto
5. Clique em **"Run workflow"** de novo para confirmar

A execução leva entre 20 e 45 minutos (a parte mais longa é o NB01,
coletando das fontes em tempo real). Acompanhe o progresso na própria aba
Actions — cada notebook aparece como uma etapa.

### 7.3 — Por que não automatizamos com um cron (agendamento fixo)?

| Motivo | Explicação |
|---|---|
| NB01 é frágil por natureza | Faz scraping em tempo real de 20+ sites — qualquer um deles pode mudar de layout, ficar fora do ar, ou bloquear a requisição num dia específico |
| Falha silenciosa é pior que falha visível | Se um cron roda de madrugada e falha parcialmente, o dashboard fica servindo dado incompleto sem ninguém saber até notar manualmente |
| Controle sobre o momento da atualização | Numa apresentação acadêmica, você quer poder atualizar minutos antes — não depender de um horário fixo que pode ou não ter coincidido |

### 7.4 — Como ativar atualização agendada (se você quiser, mais adiante)

Depois de rodar o workflow manual algumas vezes e confiar que ele é estável,
você pode adicionar um agendamento. Edite
`.github/workflows/atualizar_dados.yml` e adicione, junto ao
`workflow_dispatch`:

```yaml
on:
  workflow_dispatch:
    inputs:
      motivo:
        description: "Motivo da atualização"
        required: false
  schedule:
    - cron: "0 6 * * *"   # todos os dias às 06:00 UTC (03:00 horário de Brasília)
```

> 🎓 **Explicando "cron":** é uma notação de 5 campos (minuto, hora, dia do
> mês, mês, dia da semana) usada para agendar tarefas. `"0 6 * * *"` significa
> "minuto 0, hora 6, qualquer dia, qualquer mês, qualquer dia da semana" —
> ou seja, todo dia às 6h UTC. Para rodar de 6 em 6 horas, use `"0 */6 * * *"`.

### 7.5 — O Que Seria Necessário para Tempo Real "de Verdade" (Streaming)

Esta seção é **educacional** — explica a diferença entre o que construímos
(processamento em lote / *batch*, sob demanda) e o que seria um sistema de
**streaming** de verdade, e por que optamos pelo primeiro neste projeto.

### 🎓 Explicando: Batch vs. Streaming

| | **Batch (o que temos)** | **Streaming (tempo real de verdade)** |
|---|---|---|
| Como processa | Processa um lote inteiro de uma vez, do início ao fim, e termina | Processa cada evento (cada notícia nova) no instante em que ela chega, continuamente, sem nunca "terminar" |
| Analogia | Lavar uma pilha de roupa inteira de uma vez | Uma esteira que lava cada peça assim que ela cai na esteira |
| Quando os dados ficam disponíveis | Só depois que o processamento inteiro termina (minutos) | Segundos após o evento acontecer |
| Infraestrutura | Pode "dormir" entre execuções (como o nosso GitHub Actions) | Precisa estar **sempre ligado**, 24/7 |

### O que mudaria na arquitetura

```
ARQUITETURA ATUAL (Batch sob demanda)
┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│ Você clica   │───▶│ NB01→NB07    │───▶│ Parquet no  │
│ "Run workflow"│    │ (20-45 min)  │    │ Git          │
└──────────────┘    └──────────────┘    └─────────────┘


ARQUITETURA DE STREAMING (o que SERIA necessário)
┌─────────────┐   ┌──────────────────┐   ┌────────────────────┐
│ RSS/Scraper │──▶│ Message Broker    │──▶│ Spark Structured    │
│ (sempre   │   │ (Kafka / Kinesis /  │   │ Streaming           │
│ rodando)    │   │ Pub/Sub — sempre  │   │ (processa cada      │
│             │   │ rodando)           │   │ evento, sempre      │
│             │   │                    │   │ rodando)             │
└─────────────┘   └──────────────────┘   └─────────┬──────────┘
                                                     ▼
                                          ┌────────────────────┐
                                          │ Banco de dados      │
                                          │ (Postgres/Delta Lake│
                                          │ — não Parquet         │
                                          │ estático)             │
                                          └─────────┬──────────┘
                                                     ▼
                                          ┌────────────────────┐
                                          │ Dashboard com        │
                                          │ WebSocket/SSE         │
                                          │ (atualiza sozinho,    │
                                          │ sem precisar recarregar)│
                                          └────────────────────┘
```

### Componentes que precisariam ser adicionados/trocados

| Componente atual | Substituiria por | Por quê |
|---|---|---|
| NB01 executado sob demanda | Um serviço sempre ativo (ex: container rodando 24/7) que verifica as fontes constantemente | Streaming exige um processo contínuo, não uma execução pontual |
| Nenhum message broker | Apache Kafka, AWS Kinesis, ou Google Pub/Sub | Para desacoplar "quem coleta" de "quem processa", em alta frequência |
| PySpark em modo batch (`spark.read.parquet`) | Spark Structured Streaming (`spark.readStream`) | É um modo diferente de execução do próprio Spark, pensado para fluxos contínuos |
| Parquet estático em `data/gold/` | Banco de dados transacional (Postgres) ou Delta Lake/Iceberg | Parquet puro não foi desenhado para receber escritas incrementais constantes com segurança (ACID) |
| Streamlit com `st.cache_data(ttl=300)` (recarrega a cada 5 min, sob ação do usuário) | WebSocket ou Server-Sent Events (SSE) empurrando dados para o navegador | Para a tela atualizar sozinha, sem o usuário precisar recarregar a página |
| Render free / Streamlit Cloud free | Infraestrutura sempre ligada (ex: AWS ECS, GCP Cloud Run com min-instances, ou um VPS dedicado) | Tiers free hibernam por inatividade — incompatível com "sempre processando" |

### Por que não fizemos isso neste projeto

1. **Custo:** message broker + processamento contínuo + banco de dados
   sempre ativo não cabem em tiers gratuitos — exigiria créditos de cloud
   pagos (AWS/GCP/Azure).
2. **Complexidade vs. objetivo acadêmico:** o requisito original do curso era
   demonstrar MapReduce, TF-IDF, BM25 e arquitetura Medallion — todos
   conceitos de processamento em lote. Streaming é um paradigma diferente,
   normalmente ensinado em disciplinas específicas de "Sistemas de Dados em
   Tempo Real".
3. **Natureza da fonte de dados:** notícias sobre FIIs não mudam segundo a
   segundo como, por exemplo, cotações de bolsa. Atualizar algumas vezes ao
   dia já captura a dinâmica real do domínio — streaming traria complexidade
   sem ganho proporcional de valor.

### Quando faria sentido evoluir para streaming?

Se este projeto evoluísse para um produto comercial real, monitorando
sinais de mercado que mudam por minuto (não por dia), streaming passaria a
se justificar. Para o estágio atual — inteligência de marketing baseada em
cobertura editorial — atualização em lote, mesmo que só diária ou sob
demanda, já é o padrão usado por ferramentas reais de social listening e
media monitoring no mercado.

---

## 8. Parte 6 — Troubleshooting Consolidado

| Sintoma | Onde acontece | Causa provável | Solução |
|---|---|---|---|
| `ModuleNotFoundError` | Qualquer notebook | Ambiente virtual não ativado, ou `pip install` não rodou | `source .venv/bin/activate` e repita `pip install -r requirements.txt` |
| `java: command not found` | NB00-NB07 (qualquer um com Spark) | Java não instalado | Ver seção 3.2 |
| Notebook trava em "Running" pra sempre | NB01 | Alguma fonte está demorando demais a responder | Aguarde — há timeout de 20s por fonte; ou interrompa e rode de novo |
| `FileNotFoundError: silver_articles.parquet` | NB03, NB04, NB05 | NB02 não foi executado, ou falhou | Volte e re-execute NB02 |
| API local retorna 404 em `/articles` | Teste local da API | NB07 não foi executado, ou `data/gold/dashboard/` está vazio | Execute NB07 |
| Render mostra "Application failed to respond" | Deploy no Render | `data/gold/` não foi commitado ao Git | Rode `python scripts/preflight_check.py` e corrija os `FAIL` |
| Dashboard no Streamlit Cloud mostra 🔴 "API indisponível" | Deploy no Streamlit | Render em cold-start (spin down), ou `API_BASE_URL` errada nos Secrets | Aguarde 30-50s e recarregue; confira a URL nos Secrets |
| Erro de CORS no console do navegador | Dashboard em produção | `ALLOWED_ORIGINS` no Render não inclui a URL do Streamlit | Atualize a variável no Render (seção 6.6) |
| GitHub Actions falha no step do NB01 | Workflow manual | Alguma fonte bloqueou requisições do servidor do GitHub (IP diferente do seu) | Normal e esperado às vezes — o pipeline tem fallback (Google News RSS) e continua com as demais fontes |
| `faiss-cpu` falha ao instalar | `pip install -r requirements.txt` | Geralmente falta de compilador C++ no sistema (raro, mais comum em Windows antigo) | Use `pip install faiss-cpu --only-binary :all:` ou ambiente WSL2 no Windows |

---

## 9. Cheat Sheet de Comandos

```bash
# ── Ambiente (notebooks completos) ────────────────────────
python3 -m venv .venv
source .venv/bin/activate              # Linux/Mac
.venv\Scripts\activate                 # Windows
pip install -r requirements.txt
cp .env.example .env

# ── Ambiente leve (testar só a API ou só o Dashboard) ──────
pip install -r requirements-api.txt          # API isolada
pip install -r dashboard/requirements.txt    # Dashboard isolado

# ── Notebooks ─────────────────────────────────────────────
jupyter lab notebooks/                                  # interface visual
jupyter nbconvert --to notebook --execute --inplace notebooks/NB00_setup.ipynb   # linha de comando, um por vez

# ── Validação ─────────────────────────────────────────────
python scripts/preflight_check.py

# ── Local: API ────────────────────────────────────────────
uvicorn api.app:app --reload --port 8000
curl http://localhost:8000/health

# ── Local: Dashboard ──────────────────────────────────────
streamlit run dashboard/Home.py                                    # modo local (Parquet)
API_BASE_URL="http://localhost:8000" streamlit run dashboard/Home.py  # modo API local

# ── Git: commitando dados Gold ────────────────────────────
git add -f data/gold/ data/external/ data/silver/
git commit -m "data refresh"
git push

# ── Produção: testando endpoints ──────────────────────────
curl https://SUA-API.onrender.com/health
curl https://SUA-API.onrender.com/articles?limit=5
curl -X POST "https://SUA-API.onrender.com/query?question=Qual+FII+paga+mais+dividendo"

# ── Automação: disparar atualização manual ────────────────
# (via interface do GitHub — aba Actions → Run workflow)
# ou via GitHub CLI, se instalado:
gh workflow run "Atualizar Dados FII (Manual)" -f motivo="Atualização pré-apresentação"
```

---

*Manual Completo v1.0.0 · Investor Intelligence Platform FIIs Brasil · PUC-SP FACEI*
