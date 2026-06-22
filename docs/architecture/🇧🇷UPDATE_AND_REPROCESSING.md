# 🔄 Atualização de Dados e Reprocessamento — Documento Técnico
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

> Este documento detalha duas perguntas frequentes sobre o comportamento do
> sistema em produção: **(1)** com que frequência os dados são atualizados, e
> **(2)** se cada atualização exige reprocessar o pipeline inteiro do zero.
> Ambas têm respostas diretas que impactam como o projeto deve ser operado
> e apresentado.

<br><br>


## 📋 Sumário

1. [Resumo Executivo](#resumo-executivo)
2. [Sob Demanda vs. Periódica — Dois Conceitos Diferentes](#sob-demanda-vs-periódica--dois-conceitos-diferentes)
3. [Estado Atual do Sistema](#estado-atual-do-sistema)
4. [Como Ativar Atualização Periódica (Cron)](#como-ativar-atualização-periódica-cron)
5. [Reprocessamento Completo vs. Incremental](#reprocessamento-completo-vs-incremental)
6. [Por Que Cada Camada Resiste (ou Não) a Processamento Incremental](#por-que-cada-camada-resiste-ou-não-a-processamento-incremental)
7. [Custo de Tempo por Execução](#custo-de-tempo-por-execução)
8. [O Que Seria Necessário para Processamento Incremental Real](#o-que-seria-necessário-para-processamento-incremental-real)
9. [Recomendação e Trade-offs](#recomendação-e-trade-offs)
10. [Ver Também](#ver-também)

<br><br>

## Resumo Executivo

| Pergunta | Resposta direta |
|---|---|
| Existe um intervalo fixo de atualização hoje? | **Não.** O gatilho é manual (`workflow_dispatch`) — atualiza quando alguém clica, não em horário programado. |
| Cada atualização reprocessa tudo do zero? | **Sim.** Não há modo incremental. NB01 recoleta as 21 fontes inteiras; NB02–NB07 reprocessam o corpus completo. |
| Isso é uma limitação técnica não resolvida ou uma escolha deliberada? | **Escolha deliberada**, com trade-offs documentados abaixo — não é um bug, é uma característica da arquitetura batch adotada. |
| É possível mudar isso? | Sim, em ambas as dimensões — adicionar agendamento (`cron`) é simples; tornar o processamento incremental é uma reformulação arquitetural não-trivial (detalhada na seção 6). |

<br><br>

## Sob Demanda vs. Periódica — Dois Conceitos Diferentes

É comum confundir estes dois conceitos porque ambos envolvem "rodar de novo
o pipeline" — mas eles respondem perguntas diferentes: **quem decide quando**
a atualização acontece.

| Conceito | Quem decide o "quando" | Mecanismo no GitHub Actions | Está ativo neste projeto? |
|---|---|---|---|
| **Sob demanda** (*on-demand*) | Uma pessoa, manualmente, no momento que escolher | `on: workflow_dispatch` | ✅ Sim |
| **Periódica / agendada** (*scheduled*) | Um relógio, em intervalos fixos, sem intervenção humana | `on: schedule: - cron: "..."` | ❌ Não (desligado intencionalmente) |

Os dois mecanismos **podem coexistir no mesmo workflow** — não são mutuamente
exclusivos. É perfeitamente possível ter um botão manual *e* um agendamento
automático ao mesmo tempo; a decisão tomada neste projeto foi manter **apenas**
o gatilho manual por enquanto, adiando o agendamento.

<br><br>

## Estado Atual do Sistema

```
                    ┌─────────────────────────────┐
                    │   Alguém clica "Run workflow"│
                    │   na aba Actions do GitHub    │
                    └──────────────┬───────────────┘
                                   │ (sem isso, nada acontece)
                                   ▼
            ┌──────────────────────────────────────────┐
            │  GitHub Actions executa, em sequência:     │
            │  NB00 → NB01 → NB02 → NB03 → NB04 →        │
            │  NB05 → NB06 → NB07                         │
            │  (20-45 minutos, dependendo da resposta      │
            │   das 21 fontes monitoradas)                │
            └──────────────────┬───────────────────────────┘
                               ▼
            ┌──────────────────────────────────────────┐
            │  git commit + git push (novo Gold)          │
            └──────────────────┬───────────────────────────┘
                               ▼
            ┌─────────────────────┐      ┌──────────────────────────┐
            │  Render redeploya     │      │  Streamlit Cloud redeploya │
            │  automaticamente      │      │  automaticamente            │
            │  (detecta o push)      │      │  (detecta o push)            │
            └─────────────────────┘      └──────────────────────────┘
                               │                          │
                               ▼                          ▼
                    Dashboard e API agora servem os dados do momento do clique
```

**Consequência prática:** se ninguém clicar no botão por uma semana, os
dados servidos continuam sendo os da última execução, sem nenhum aviso de
"dados antigos" além do campo `generated_at` exposto em `/summary` e na
sidebar do dashboard.

<br><br>

## Como Ativar Atualização Periódica (Cron)

Para transformar o gatilho manual em automático, edite
`.github/workflows/atualizar_dados.yml` e adicione um bloco `schedule`:

```yaml
on:
  workflow_dispatch:
    inputs:
      motivo:
        description: "Motivo da atualização"
        required: false
  schedule:
    - cron: "0 6 * * *"     # todo dia às 06:00 UTC (03:00 em Brasília)
```

### Sintaxe do cron (5 campos)

```
┌───────────── minuto (0-59)
│ ┌─────────── hora (0-23)
│ │ ┌───────── dia do mês (1-31)
│ │ │ ┌─────── mês (1-12)
│ │ │ │ ┌───── dia da semana (0-6, domingo=0)
│ │ │ │ │
* * * * *
```

| Quero atualizar... | Expressão cron |
|---|---|
| Uma vez por dia, às 6h UTC | `0 6 * * *` |
| A cada 6 horas | `0 */6 * * *` |
| A cada 12 horas | `0 */12 * * *` |
| Toda segunda-feira às 8h UTC | `0 8 * * 1` |
| Duas vezes ao dia (6h e 18h UTC) | `0 6,18 * * *` |

> ⚠️ **Importante sobre fuso horário:** o GitHub Actions usa UTC. Brasília
> está em UTC-3 (ou UTC-2 no horário de verão, quando aplicável). Para
> "rodar às 6h da manhã no Brasil", use `cron: "0 9 * * *"` (9h UTC = 6h
> Brasília, fora do horário de verão).

> ⚠️ **Importante sobre confiabilidade:** o GitHub não garante execução no
> segundo exato — em horários de pico, pode haver atraso de alguns minutos.
> Isso é aceitável para este caso de uso (não é um sistema de trading de
> alta frequência).

<br><br>

## Reprocessamento Completo vs. Incremental

Esta é a distinção mais importante deste documento, porque tem impacto
direto em **tempo de execução** e em **custo** (minutos de CI/CD, requests
às fontes externas).

### Definições

| Termo | Significado |
|---|---|
| **Reprocessamento completo** (*full refresh*) | A cada execução, todo o pipeline roda do zero: todas as fontes são consultadas novamente, todo o corpus é limpo, vetorizado e analisado de novo — independentemente do que já existia antes. |
| **Processamento incremental** (*incremental update*) | A cada execução, apenas os dados **novos** desde a última execução são processados; resultados antigos são reaproveitados/mesclados, não recalculados. |

### O que este projeto faz hoje

**Reprocessamento completo, em todas as 8 etapas, sem exceção.**

| Notebook | O que é refeito a cada execução |
|---|---|
| NB01 | Todas as 21 fontes são consultadas de novo, do início — não há controle de "buscar só o que é mais novo que a última coleta" |
| NB02 | Todo o Bronze é relido e limpo de novo (ainda que o conteúdo de artigos antigos não tenha mudado) |
| NB03 | A contagem de palavras (MapReduce) é recalculada para o corpus inteiro |
| NB04 | TF-IDF, BM25 e os embeddings FAISS são **inteiramente retreinados/reconstruídos** sobre o corpus completo |
| NB05 | O sentimento é recalculado para todos os artigos, incluindo os que já tinham sido analisados antes |
| NB06 | As métricas de Marketing Intelligence por FII são recalculadas do zero |
| NB07 | Os datasets finais do dashboard são inteiramente regenerados |

<br><br>

## Por Que Cada Camada Resiste (ou Não) a Processamento Incremental

Nem todas as camadas têm a mesma dificuldade de se tornarem incrementais.
Esta seção detalha, camada por camada, **por que** o reprocessamento
completo foi a escolha mais segura — e onde haveria mais ou menos
dificuldade técnica em mudar isso.

### 🟢 Camadas relativamente fáceis de tornar incrementais

| Camada | Por quê é viável | O que mudaria |
|---|---|---|
| **NB01 — Ingestão** | Feeds RSS já retornam itens ordenados por data; é possível guardar o `published_at` mais recente já coletado por fonte e pedir só itens posteriores | Adicionar uma tabela de "checkpoint" (`last_collected_at` por fonte) e filtrar antes de salvar |
| **NB05 — Sentimento** | A análise de sentimento é **por documento**, independente — o sentimento do artigo A não depende do artigo B | Rodar a função de sentimento só nos `article_id` novos, e fazer `UNION` com o resultado anterior |
| **FAISS (Camada 3 do NB04)** | Índices FAISS suportam **adição incremental nativa** via `index.add()` — não é necessário reconstruir o índice inteiro para adicionar novos vetores | Adicionar só os embeddings dos novos artigos ao índice existente, sem recriar do zero |

### 🔴 Camadas estruturalmente difíceis de tornar incrementais

| Camada | Por que é difícil | Detalhe técnico |
|---|---|---|
| **TF-IDF (Camada 1 do NB04)** | O **IDF** (Inverse Document Frequency) de **cada termo já existente** muda quando um novo documento entra no corpus — não é só "adicionar uma linha", é recalcular os pesos de toda a matriz | `IDF(t) = log((N+1)/(df(t)+1)) + 1` depende de `N` (total de documentos) e `df(t)` (em quantos documentos o termo aparece) — ambos mudam globalmente a cada novo artigo |
| **BM25 (Camada 2 do NB04)** | O `avgdl` (comprimento médio de documento no corpus) muda a cada novo artigo, afetando a normalização de **todos** os scores anteriores, não só os novos | A fórmula BM25 usa `avgdl` no denominador para todo `f(qi,D)` — um valor global recalculado a cada execução |
| **NB03 — MapReduce Word Count** | A contagem global de palavras é uma agregação cumulativa — tecnicamente *poderia* ser incremental (somar ao total existente), mas o `negative_ctx_ratio` depende de recalcular a janela de contexto sobre o corpus completo para manter consistência estatística | Seria necessário re-arquitetar como uma agregação incremental verdadeira (ex: `reduceByKey` com estado persistido entre execuções, não recriado a cada rodada) |
| **NB06 — Marketing Intelligence** | O `mi_score` de cada FII depende de médias (`sentiment_avg`, `relevance_avg`) sobre **todos** os artigos relacionados àquele FII — adicionar um artigo novo muda a média de todos os artigos antigos também | Seria necessário guardar somas e contagens parciais (não só a média final) para permitir recálculo incremental de médias |

### A conclusão prática desta análise

A camada que **mais se beneficiaria** de processamento incremental sem
sacrificar precisão é o **FAISS** (Camada 3) — tecnicamente já suporta isso
nativamente. As camadas que **mais resistem** são exatamente as que fazem
parte do núcleo acadêmico do projeto — **TF-IDF e BM25** — porque a própria
matemática delas é definida em relação ao corpus inteiro, não a documentos
isolados.

Isso significa que uma versão "parcialmente incremental" do pipeline
(ex: só NB01 e NB05 incrementais, NB04 e NB06 continuando full-refresh)
é tecnicamente viável e seria o passo intermediário mais natural — mas
ainda exigiria reescrever a lógica de checkpoint em pelo menos dois
notebooks, o que está fora do escopo de uma simples configuração.

<br><br>

## Custo de Tempo por Execução

| Etapa | Tempo aproximado | Depende de quê |
|---|---|---|
| NB00 | 2-5 min | Primeira execução baixa dependências |
| NB01 | 15-30 min | **Maior variável** — tempo de resposta das 21 fontes externas |
| NB02 | 5 min | Tamanho do corpus coletado |
| NB03 | 5 min | Tamanho do corpus |
| NB04 | 10-20 min | Treino de TF-IDF/BM25 + geração de embeddings (FAISS) |
| NB05 | 10 min | Tamanho do corpus |
| NB06 | 15 min | 15 FIIs × N queries de retrieval cada |
| NB07 | 5 min | Consolidação final |
| **Total** | **~70-90 min** | — |

**Ponto-chave:** este tempo é **praticamente o mesmo** independentemente de
você ter rodado a última atualização há 1 hora ou há 1 mês — porque tudo é
reprocessado do zero. Não há "atualização rápida" disponível hoje.

---

## O Que Seria Necessário para Processamento Incremental Real

Para além das mudanças pontuais por camada já descritas, uma arquitetura
verdadeiramente incremental exigiria:

| Componente novo | Função |
|---|---|
| **Tabela de checkpoint** (ex: `data/control/last_run_state.json`) | Guardar, por fonte, o timestamp do último artigo coletado |
| **Lógica de merge no NB02** | Em vez de `df = pd.read_parquet(...)`, fazer `df_novo = ler_apenas_novos(); df_total = pd.concat([df_existente, df_novo])` |
| **Persistência de estatísticas intermediárias (NB03, NB06)** | Guardar somas/contagens parciais, não só os resultados finais, para permitir recálculo de médias sem reler tudo |
| **Estratégia de refit periódico para TF-IDF/BM25** | Mesmo num cenário incremental, esses dois modelos precisariam ser **retreinados por completo** em intervalos (ex: semanalmente), com os artigos novos sendo servidos com scores aproximados/desatualizados entre um refit e outro |
| **Versionamento de schema** | Garantir que adicionar uma coluna nova num notebook não quebre o merge com dados antigos de execuções anteriores |

> 📌 Esta lista é deliberadamente mais simples que a arquitetura de
> *streaming* (Kafka, Spark Structured Streaming, banco transacional)
> detalhada no `MANUAL_COMPLETO.md` — processamento incremental em **batch**
> é um meio-termo entre "tudo do zero sempre" (o que temos) e "tempo real
> via streaming" (o que seria um projeto bem maior). Ver seção
> ["Ver Também"](#ver-também) abaixo.

<br><br>

## Recomendação e Trade-offs

| Cenário | Recomendação |
|---|---|
| Entrega acadêmica / demonstração | Manter como está — reprocessamento completo sob demanda é simples de explicar e de auditar |
| Uso recorrente, mas ainda de baixo volume | Adicionar `schedule` (cron) ao workflow atual, mantendo reprocessamento completo — aceitável até a coleta ultrapassar ~1h de execução |
| Evolução para produto real, alto volume de fontes/artigos | Priorizar incrementalidade em NB01 e NB05 primeiro (mais fáceis, maior ganho), aceitar que NB04/NB06 continuem full-refresh periódico |
| Necessidade de latência de minutos/segundos | Nenhuma das opções acima resolve — seria necessário streaming de verdade (ver `COMPLETE_MANUAL.md`) |

<br><br>

## Ver Também

- **`COMPLETE_MANUAL.md`**, seção **"Parte 5 — Automação e Atualização em
  Tempo Real"** — explica a diferença entre batch e streaming, e o que
  seria necessário para um sistema de tempo real de verdade (Kafka, Spark
  Structured Streaming, banco transacional, WebSocket).
- **`docs/methodology/MAPREDUCE_PATTERN.md`** — detalha a implementação do
  MapReduce usado no NB03, relevante para entender por que sua agregação
  atual não é trivialmente incremental.
- **`docs/methodology/BM25_FOUNDATION.md`** — detalha a fórmula matemática
  do BM25 e por que `avgdl` é um valor global do corpus, não por documento.
- **`.github/workflows/atualizar_dados.yml`** — arquivo onde o gatilho
  manual está configurado e onde o `schedule` (cron) pode ser adicionado.

<br><br>

*Atualização de Dados e Reprocessamento · Investor Intelligence Platform FIIs Brasil*
