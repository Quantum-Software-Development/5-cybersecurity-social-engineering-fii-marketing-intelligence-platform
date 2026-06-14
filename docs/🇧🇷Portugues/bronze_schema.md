# Bronze Schema Contract — 17 Campos
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Camada:** Bronze · **Localização:** `data/external/` · **Formato:** Parquet (snappy)

---

## Regras Fundamentais

| Regra | Descrição |
|---|---|
| **Freeze** | NB01 grava `data/external/`. NB02–NB07 lêem exclusivamente. Nunca sobrescrever. |
| **`published_at = None`** | Conteúdo scraping sem data real → `None`. Nunca preencher com `collected_at`. |
| **`article_id`** | SHA-256(url.strip()) — chave primária determinística e imutável. 64 chars hex. |
| **`content_hash`** | MD5(title + content[:500]) — dedup de conteúdo quase-duplicado. 32 chars hex. |
| **`RANDOM_SEED = 42`** | Todas as operações estocásticas usam esta seed. |

---

## Schema Completo — 17 Campos

| # | Campo | Tipo | Nullable | Origem | Descrição |
|---|---|---|---|---|---|
| 1 | `article_id` | `str` | ❌ | `SHA-256(url)` | Chave primária. 64 chars hex. Determinístico e imutável. |
| 2 | `source` | `str` | ❌ | URL parsing | Domínio do portal (ex: `infomoney.com.br`) |
| 3 | `source_type` | `str` | ❌ | Lógica NB01 | `rss` · `scraping` · `reddit` |
| 4 | `title` | `str` | ❌ | Feed / HTML | Título bruto do artigo |
| 5 | `content` | `str` | ✅ | Feed / HTML | Corpo completo (texto limpo de tags HTML) |
| 6 | `summary` | `str` | ✅ | Feed / HTML | Lead ou resumo — máx 500 chars |
| 7 | `url` | `str` | ❌ | Feed / HTML | URL canônica — sem UTMs, sem âncoras `#` |
| 8 | `author` | `str` | ✅ | Feed / HTML | Autor. Metadado editorial público. |
| 9 | `published_at` | `str` | ✅ | Feed / Reddit | RSS: data real do feed · Scraping: **`None`** · Reddit: UTC ISO da criação |
| 10 | `collected_at` | `str` | ❌ | `datetime.now(UTC)` | ISO-8601 UTC do momento exato da coleta no NB01 |
| 11 | `language` | `str` | ❌ | Constante | `pt-br` para todas as fontes |
| 12 | `tags` | `str` | ✅ | Feed | Tags separadas por vírgula |
| 13 | `query_used` | `str` | ✅ | `matched_filter_term()` | Primeiro `FII_FILTER_TERM` encontrado no artigo |
| 14 | `ingestion_method` | `str` | ❌ | Lógica NB01 | `feedparser` · `requests+bs4` · `praw` · `reddit_public_api` · `frozen_parquet` |
| 15 | `raw_html` | `str` | ✅ | requests | HTML bruto do elemento extraído. Scraping only. Máx 2.000 chars. |
| 16 | `content_hash` | `str` | ❌ | `MD5(title+content[:500])` | Near-duplicate detection. 32 chars hex. |
| 17 | `metadata_json` | `str` | ✅ | Lógica NB01 | JSON string com extras específicos por tipo de fonte |

---

## Valores de `metadata_json` por Tipo de Fonte

### RSS / feedparser
```json
{ "feed_url": "https://www.infomoney.com.br/feed/", "feed_bozo": false }
```

### Scraping (requests + BS4)
```json
{ "status_code": 200, "elapsed_ms": 1234, "encoding": "utf-8" }
```

### Reddit (PRAW)
```json
{ "subreddit": "investimentos", "score": 42, "num_comments": 15, "upvote_ratio": 0.95 }
```

### Reddit (API pública)
```json
{ "score": 10, "num_comments": 3, "upvote_ratio": 0.88, "subreddit": "farialimabets", "endpoint": "hot" }
```

---

## Deduplicação Bronze (NB01 — antes do freeze)

Aplicada em 2 passes antes de salvar:

```python
df = df.drop_duplicates('article_id')     # mesma URL
df = df.drop_duplicates('content_hash')   # conteúdo quase-idêntico
```

Deduplicação cross-source final antes de gravar `bronze_all_articles.parquet`.

---

## Arquivos Gerados por NB01

| Arquivo | Conteúdo | Linhas esperadas |
|---|---|---|
| `bronze_all_articles.parquet` | Combinado — todas as 21 fontes | 500–5.000 |
| `rss_fii_articles.parquet` | Apenas fontes RSS (1–10) | 200–2.000 |
| `portal_fii_articles.parquet` | Apenas portais scraping (11–20) | 100–1.500 |
| `reddit_fii_posts.parquet` | Apenas Reddit (21) | 50–1.000 |

---

## Validação RDD (NB02)

```python
_ids_rdd = sdf.select("article_id").rdd.map(lambda r: r["article_id"])
_id_lens = _ids_rdd.map(lambda aid: len(aid)).distinct().collect()
assert all(l == 64 for l in _id_lens), "article_id deve ter 64 chars (SHA-256)"
```

---

*Bronze Schema Contract v1.0.0 · Investor Intelligence Platform FIIs Brasil*
