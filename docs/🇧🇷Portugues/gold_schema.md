# Gold Layer Schema — Datasets Analíticos
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Camada:** Gold · **Localização:** `data/gold/` · **Gerado por:** NB03–NB07

---

## Visão Geral dos Subdiretórios

```
data/gold/
├── word_count/               ← NB03: MapReduce
├── tfidf_bm25/               ← NB04: Índices de busca
├── sentiment/                ← NB05: Análise de sentimento
├── marketing_intelligence/   ← NB06: MI por FII
└── dashboard/                ← NB07: Datasets prontos para consumo
```

---

## 1. Word Count (`data/gold/word_count/`)

### `global_word_count.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `term` | str | Token normalizado (NFD, lowercase) |
| `count` | int | Frequência total no corpus |
| `rank` | int | Posição no ranking global (1 = mais frequente) |

### `source_word_count.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `source_label` | str | Nome comercial da fonte |
| `term` | str | Token normalizado |
| `count` | int | Frequência nesta fonte |

### `tofu_frequency.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `term` | str | Termo TOFU do léxico de marketing |
| `count` | int | Frequência global |
| `rank` | int | Rank global |
| `tofu_rank` | int | Rank dentro do vocabulário TOFU |
| `n_sources` | int | Número de fontes em que aparece |

### `negative_context.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `term` | str | Termo de risco monitorado |
| `global_count` | int | Frequência total no corpus |
| `negative_ctx_ratio` | float | Razão de co-ocorrência com palavras negativas (janela ±5) |
| `risk_level` | str | `high` · `medium` · `low` |
| `n_docs_with_term` | int | Número de documentos contendo o termo |

---

## 2. TF-IDF + BM25 (`data/gold/tfidf_bm25/`)

### `tfidf_vectorizer.pkl` (pickle)
Objeto `sklearn.TfidfVectorizer` treinado.
- `ngram_range=(1,2)` · `max_features=50_000` · `sublinear_tf=True` · `min_df=2`

### `tfidf_matrix.npz` (scipy sparse)
Matriz TF-IDF: shape `(N_docs × V_vocab)`. Formato CSR comprimido.

### `bm25_index.pkl` (pickle)
Objeto `rank_bm25.BM25Okapi` treinado. `k1=1.5` · `b=0.75`.

### `corpus_tokens.pkl` (pickle)
`List[List[str]]` — corpus tokenizado. Necessário para reconstrução/busca BM25.

### `doc_index_map.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `doc_index` | int | Índice posicional no corpus (0-based) |
| `article_id` | str | SHA-256 — FK para Silver |
| `source` | str | Domínio da fonte |
| `title` | str | Título do artigo |

### `document_relevance.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `query` | str | Query de busca usada |
| `query_index` | int | Índice da query na lista de queries predefinidas |
| `rank` | int | Posição no ranking para esta query |
| `article_id` | str | FK para Silver |
| `source` | str | Fonte do artigo |
| `title` | str | Título |
| `score_tfidf` | float | Score coseno TF-IDF [0.0, 1.0] |
| `score_bm25` | float | Score BM25 bruto |
| `score_hybrid` | float | 0.4×TF-IDF_norm + 0.6×BM25_norm |

---

## 3. Sentiment (`data/gold/sentiment/`)

### `articles_sentiment.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `article_id` | str | FK para Silver |
| `source` | str | Fonte |
| `source_type` | str | Tipo de fonte |
| `source_label` | str | Nome comercial |
| `title` | str | Título |
| `url` | str | URL |
| `published_dt` | str | Data normalizada |
| `collected_at` | str | Data de coleta |
| `polarity_score` | float | Score [-1.0, +1.0] pelo léxico FII PT-BR |
| `sentiment_label` | str | `positivo` · `neutro` · `negativo` |
| `n_pos_terms` | int | Termos positivos encontrados |
| `n_neg_terms` | int | Termos negativos encontrados |
| `flag_dividendo` | bool | Sinal de dividendo/provento presente |
| `flag_oportunidade` | bool | Sinal de oportunidade/compra presente |
| `flag_risco` | bool | Sinal de risco presente |
| `flag_crise` | bool | Sinal de crise/queda presente |
| `flag_vacancia` | bool | Sinal de vacância presente |
| `flag_inadimplencia` | bool | Sinal de inadimplência presente |
| `score_dividendo` | float | Intensidade [0.0, 1.0] |
| `score_oportunidade` | float | Intensidade [0.0, 1.0] |
| `score_risco` | float | Intensidade [0.0, 1.0] |
| `score_crise` | float | Intensidade [0.0, 1.0] |

### `sentiment_by_source.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `source_label` | str | Nome comercial da fonte |
| `n_articles` | int | Total de artigos nesta fonte |
| `avg_polarity` | float | Média de `polarity_score` |
| `pct_positivo` | float | % de artigos positivos |
| `pct_negativo` | float | % de artigos negativos |
| `pct_neutro` | float | % de artigos neutros |
| `n_dividendo` | int | Artigos com `flag_dividendo=True` |
| `n_risco` | int | Artigos com `flag_risco=True` |
| `n_crise` | int | Artigos com `flag_crise=True` |

### `sentiment_by_month.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `pub_month` | str | Mês de publicação (Period "YYYY-MM") |
| `n_articles` | int | Total de artigos neste mês |
| `avg_polarity` | float | Média de `polarity_score` |
| `pct_pos` | float | % positivos |
| `pct_neg` | float | % negativos |

---

## 4. Marketing Intelligence (`data/gold/marketing_intelligence/`)

### `mi_signals.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `ticker` | str | Código B3 do FII (ex: `HGLG11`) |
| `full_name` | str | Nome completo do fundo |
| `segment` | str | Segmento: `logistica` · `shopping` · `laje` · `papel` · `hibrido` · `varejo` |
| `mentions` | int | Total de documentos relevantes |
| `sentiment_avg` | float | Média de `polarity_score` nos docs relevantes |
| `relevance_avg` | float | Média de `score_hybrid` |
| `pct_positivo` | float | % docs positivos |
| `pct_negativo` | float | % docs negativos |
| `n_dividendo` | int | Docs com `flag_dividendo=True` |
| `n_oportunidade` | int | Docs com `flag_oportunidade=True` |
| `n_risco` | int | Docs com `flag_risco=True` |
| `n_crise` | int | Docs com `flag_crise=True` |
| `n_vacancia` | int | Docs com `flag_vacancia=True` |
| `n_inadimplencia` | int | Docs com `flag_inadimplencia=True` |
| `risk_score` | float | `(n_risco + 2·n_crise + 2·n_vacancia + 2·n_inadimpl) / mentions` |
| `opportunity_score` | float | `(n_dividendo + n_oportunidade) / mentions` |
| `mi_score` | float | `0.5·relevance + 0.3·|sentiment| + 0.2·opportunity` |

### `mi_top_articles.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `ticker` | str | Código B3 |
| `rank` | int | Posição no top-10 deste FII |
| `article_id` | str | FK para Silver |
| `title` | str | Título |
| `url` | str | URL |
| `source` | str | Fonte |
| `published_dt` | str | Data normalizada |
| `sentiment_label` | str | Sentimento |
| `polarity_score` | float | Score de polaridade |
| `score_bm25` | float | Score BM25 |
| `score_tfidf` | float | Score TF-IDF |
| `score_hybrid` | float | Score híbrido |
| `mi_article_score` | float | `0.5·hybrid + 0.3·|polarity| + 0.2·flag_dividendo` |
| `flag_dividendo` | bool | Flag de dividendo |
| `flag_risco` | bool | Flag de risco |
| `flag_crise` | bool | Flag de crise |

### `mi_funnel.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `stage` | str | `TOFU` · `MOFU` · `BOFU` |
| `query` | str | Query de referência usada |
| `article_id` | str | FK para Silver |
| `source` | str | Fonte |
| `source_type` | str | Tipo |
| `score_hybrid` | float | Relevância híbrida |
| `sentiment_label` | str | Sentimento |
| `polarity_score` | float | Score de polaridade |
| `flag_dividendo` | bool | Flag de dividendo |
| `flag_risco` | bool | Flag de risco |

### `mi_source_ranking.parquet`

| Campo | Tipo | Descrição |
|---|---|---|
| `source` | str | Domínio da fonte |
| `n_articles` | int | Artigos nos top-10 de qualquer FII |
| `avg_relevance` | float | Relevância média `score_hybrid` |
| `avg_polarity` | float | Polaridade média |
| `n_dividendo` | int | Artigos com flag_dividendo |
| `n_risco` | int | Artigos com flag_risco |
| `source_mi_score` | float | `0.5·avg_relevance + 0.3·|avg_polarity|` |

---

## 5. Dashboard (`data/gold/dashboard/`)

### `dashboard_articles.parquet` + `.csv`
Catálogo completo de artigos com TODOS os scores consolidados.
Colunas: union de Silver + sentimento + MI scores.
**Tabela central consultada por FastAPI e Streamlit.**

### `dashboard_fii_signals.parquet` + `.csv`
Uma linha por FII. Métricas consolidadas + `sentiment_trend` normalizado [0,1].

### `dashboard_source_stats.parquet` + `.csv`
Uma linha por fonte. Stats de volume, sentimento e sinais por portal.

### `dashboard_funnel_stats.parquet` + `.csv`
Uma linha por estágio TOFU/MOFU/BOFU. Volumetria e sentimento médio.

### `dashboard_word_cloud.parquet` + `.csv`
Top 200 termos. Campos: `term`, `count`, `freq_normalized`, `is_tofu`.

### `api_payload_summary.json`
Resumo estruturado para FastAPI `/health` e cache de primeiro carregamento.

```json
{
  "generated_at": "2026-01-15T10:30:00Z",
  "pipeline_version": "1.0.0",
  "random_seed": 42,
  "totals": { "articles": 1320, "sources": 21, "fii_entities": 15 },
  "sentiment_distribution": { "neutro": 680, "positivo": 420, "negativo": 220 },
  "top_sources": [...],
  "top_fii_by_mi_score": [...],
  "source_types": { "rss": 800, "scraping": 400, "reddit": 120 },
  "data_paths": { ... }
}
```

---

*Gold Layer Schema v1.0.0 · Investor Intelligence Platform FIIs Brasil*
