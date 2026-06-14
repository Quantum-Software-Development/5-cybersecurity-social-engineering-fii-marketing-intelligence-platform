# CRISP-DM — Mapeamento Completo da Metodologia
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Referência:** Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* SPSS.

---

## Visão Geral do Ciclo CRISP-DM

```
┌─────────────────────────────────────────────┐
│                                             │
│   Business         Data                    │
│  Understanding ──► Understanding            │
│       ▲                │                   │
│       │                ▼                   │
│  Deployment       Data Preparation         │
│       ▲                │                   │
│       │                ▼                   │
│  Evaluation  ◄──── Modeling                │
│                                             │
└─────────────────────────────────────────────┘
```

O CRISP-DM é iterativo — após Deployment pode-se voltar a Business Understanding para refinar objetivos.

---

## Fase 1 — Business Understanding (NB00)

**Objetivos de negócio:**
- Monitorar 21 fontes de conteúdo FII em português
- Identificar termos de alta relevância para estratégia de marketing
- Detectar sinais de risco e oportunidade por fundo

**Critérios de sucesso:**
- Pipeline executável de ponta a ponta
- 21 fontes cobertas com fallbacks
- Reprodutibilidade garantida (RANDOM_SEED=42)
- Governança completa (LGPD, Responsible AI, EU AI Act)

**Artefatos de NB00:**
- `config/settings.py` — parâmetros de negócio (21 fontes, FII_FILTER_TERMS, FII entities)
- `src/utils/logger.py` — auditabilidade operacional
- Documentação de governança

---

## Fase 2 — Data Understanding (NB01)

**Coleta inicial de dados:**
- 21 fontes (6 RSS + 4 RSS supl. + 10 scraping + Reddit)
- Schema Bronze de 17 campos
- Relatório de proveniência

**Exploração de dados:**
- Contagem de artigos por fonte
- Distribuição de `source_type`
- Logs de erros e fallbacks

**Qualidade dos dados identificada:**
- Duplicatas cross-source (mitigadas por `article_id` + `content_hash`)
- Datas ausentes em scraping (tratadas com `published_at=None`)
- Conteúdo de baixa qualidade (filtrado no Silver pelo `word_count`)

**Artefatos de NB01:**
- `data/external/bronze_all_articles.parquet` (frozen)
- `data_collection_report.json`

---

## Fase 3 — Data Preparation (NB02)

**Seleção:** Apenas artigos que passam nos 3 quality gates.

**Limpeza:**
- Remoção de tags HTML, entidades, URLs
- Remoção de boilerplates (rodapés, CTAs)
- Normalização de encoding (NFD)

**Construção:**
- `text_clean` — corpo limpo e processável
- `published_dt` — ISO-8601 UTC normalizado
- `source_label` — mapeamento domínio → nome comercial
- `word_count`, `char_count`, `has_content`

**Formatação:**
- Parquet snappy com schema controlado

**Artefatos de NB02:**
- `data/silver/silver_articles.parquet`
- `data/silver/silver_processing_report.json`

---

## Fase 4 — Modeling (NB03, NB04, NB05)

### NB03 — MapReduce Word Count

**Técnica:** RDD MapReduce distribuído (PySpark)

**Modelos:**
- Frequência global de tokens
- Frequência por fonte (source_label × token)
- `negative_ctx_ratio` — razão de co-ocorrência negativa

**Parâmetros:**
- Tokenizador PT-BR NFD + stopwords NLTK
- Janela de contexto negativo: ±5 tokens

### NB04 — TF-IDF + BM25

**Técnica 1:** TF-IDF Vectorizer (sklearn)
- `ngram_range=(1,2)`, `max_features=50_000`, `sublinear_tf=True`, `min_df=2`

**Técnica 2:** BM25Okapi (rank_bm25)
- `k1=1.5`, `b=0.75`

**Score híbrido:**
- `0.4 × TF-IDF_norm + 0.6 × BM25_norm`

### NB05 — Sentimento Contextual

**Técnica:** Léxico FII PT-BR customizado (70+ termos)
- `polarity_score ∈ [-1.0, +1.0]`
- `sentiment_label ∈ {positivo, neutro, negativo}`
- 6 categorias de signal flags

**Fallback:** TextBlob quando léxico retorna 0.0

---

## Fase 5 — Evaluation (NB06)

**Avaliação de negócio:**
- 15 FIIs com `mi_score` calculado
- Ranking de fontes por `source_mi_score`
- Funil TOFU/MOFU/BOFU documentado

**Métricas de avaliação:**

| Métrica | Cálculo | Objetivo |
|---|---|---|
| `mi_score` | `0.5·relevance + 0.3·|sentiment| + 0.2·opportunity` | Score geral de marketing intelligence por FII |
| `risk_score` | `(risco + 2·crise + 2·vacancia + 2·inadimpl) / mentions` | Alerta de risco reputacional |
| `opportunity_score` | `(dividendo + oportunidade) / mentions` | Sinal de oportunidade de compra |
| `negative_ctx_ratio` | co-ocorrências negativas / total ocorrências | Contexto narrativo de risco |

**Critérios de aceitação para Deployment:**
- `mi_signals.parquet` com 15 FIIs
- `mi_top_articles.parquet` com top-10 por FII
- `mi_funnel.parquet` com 3 estágios documentados
- Dashboard validation HTML sem erros

---

## Fase 6 — Deployment (NB07)

**Planejamento de deployment:**
- FastAPI: `api/app.py`
- Streamlit: `dashboard/Home.py`
- Groq chatbot: `dashboard/chatbot/groq_client.py`

**Monitoramento:**
- Logs estruturados em `logs/`
- `api_payload_summary.json` como health check
- `dashboard_validation.html` como validação automática

**Artefatos finais:**

| Artefato | Consumidor |
|---|---|
| `dashboard_articles.parquet` + `.csv` | FastAPI + Streamlit |
| `dashboard_fii_signals.parquet` + `.csv` | Streamlit (painel FIIs) |
| `dashboard_source_stats.parquet` + `.csv` | Streamlit (painel fontes) |
| `dashboard_funnel_stats.parquet` + `.csv` | Streamlit (painel funil) |
| `dashboard_word_cloud.parquet` + `.csv` | Streamlit (nuvem de palavras) |
| `api_payload_summary.json` | FastAPI `/health` |
| `dashboard_validation.html` | Validação automática |

---

## Mapeamento Notebook → Fase CRISP-DM

| Notebook | Fase CRISP-DM | Entrega Principal |
|---|---|---|
| NB00 | Business Understanding | Infraestrutura + configuração |
| NB01 | Data Understanding | Dataset Bronze frozen |
| NB02 | Data Preparation | Dataset Silver limpo |
| NB03 | Modeling | Word Count MapReduce |
| NB04 | Modeling | Índices TF-IDF + BM25 |
| NB05 | Modeling | Sentimento FII PT-BR |
| NB06 | Evaluation | MI Signals por FII |
| NB07 | Deployment | Dashboard datasets |

---

## Iterações e Lições Aprendidas

| Iteração | Problema identificado | Solução aplicada |
|---|---|---|
| 1 | `published_at` com `datetime.now()` contamina análises temporais | `published_at = None` para scraping |
| 2 | `log_spark_start(logger)` — 1 argumento | `log_spark_start(logger, app_name, version)` — 3 argumentos |
| 3 | `scrape_portal()` chamada antes de ser declarada | Reordenação de células em NB01 |
| 4 | Mismatch de versão PySpark Driver vs Worker | Injeção de `PYSPARK_PYTHON` e `PYSPARK_DRIVER_PYTHON` |
| 5 | NLTK `punkt_tab` quebra com `LookupError` + `OSError` | Tratamento de ambos os tipos de exceção |
| 6 | Word count puro não responde à pergunta de marketing | Adição de TF-IDF + BM25 + sentimento |
| 7 | TextBlob classifica "vacância" como positivo | Léxico FII PT-BR customizado (70+ termos) |

---

*CRISP-DM Mapping v1.0.0 · Investor Intelligence Platform FIIs Brasil*
