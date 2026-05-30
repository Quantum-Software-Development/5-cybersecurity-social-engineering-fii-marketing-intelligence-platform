# Data Dictionary
### **Investor Intelligence Platform - FIIs Brasil 🇧🇷**

<br><br>

## Bronze Layer Schema

Raw ingested data. No transformations applied. Preserved for audit.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `url` | string | Scraper | Original article URL |
| `source` | string | Scraper | Portal domain (e.g., `infomoney.com.br`) |
| `title` | string | RSS / HTML | Article headline (raw, may contain HTML) |
| `body_html` | string | RSS / HTML | Full article body (raw HTML) |
| `author` | string | RSS / HTML | Author name or "Unknown" |
| `published_date` | string | RSS / HTML | Publication date (raw string, unparsed) |
| `ingestion_timestamp` | string | Pipeline | ISO-8601 UTC timestamp of collection |
| `reddit_score` | int | Reddit API | Upvote score (Reddit only) |
| `reddit_num_comments` | int | Reddit API | Comment count (Reddit only) |

<br><br>

## Silver Layer Schema

Cleaned and normalized data. One record per unique article.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `article_id` | string | No | SHA-256 hash of `url` (deterministic) |
| `url` | string | No | Cleaned URL |
| `source` | string | No | Normalized domain name |
| `title` | string | No | Cleaned title (HTML stripped) |
| `body` | string | No | Cleaned body text (HTML stripped) |
| `author` | string | Yes | Author name |
| `published_date` | timestamp | Yes | Parsed publication date |
| `word_count` | int | No | Token count of `body` |
| `char_count` | int | No | Character count of `body` |
| `ingestion_timestamp` | timestamp | No | Collection timestamp |

**Deduplication key**: `url` (exact match)  
**Minimum quality filter**: `word_count >= 20` AND `char_count >= 100`

<br><br>

## Gold Layer — Output Tables

### `source_ranking.parquet`

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Portal domain |
| `avg_bm25_score` | float | Average BM25 score across FII queries |
| `positive_pct` | float | % of articles classified positive |
| `negative_pct` | float | % of articles classified negative |
| `neutral_pct` | float | % of articles classified neutral |
| `negative_context_score` | float | % of FII mentions in negative context window |
| `strategic_score` | float | Composite marketing priority score |
| `article_count` | int | Total articles from this source |
| `analysis_date` | timestamp | Date of analysis run |

<br>

### `sentiment_by_source.parquet`

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Portal domain |
| `sentiment` | string | `positive` / `negative` / `neutral` |
| `count` | int | Article count per sentiment |
| `avg_polarity` | float | Mean TextBlob polarity (EN baseline) |
| `avg_confidence` | float | Confidence score (lexicon-augmented) |

<br>

### `negative_context_terms.parquet`

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Portal domain |
| `term` | string | High-frequency term in negative context |
| `total_mentions` | int | Total occurrences of term |
| `negative_mentions` | int | Occurrences within negative window (±5 tokens) |
| `negative_pct` | float | `negative_mentions / total_mentions * 100` |
| `severity_score` | float | Weighted negative severity |

<br><


### `topic_clusters.parquet`

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | int | LDA topic index (0–4) |
| `topic_name` | string | Human-assigned label |
| `top_terms` | string | Top 10 terms (comma-separated) |
| `coherence_score` | float | Topic coherence (C_v) |
| `doc_count` | int | Documents predominantly in this topic |

<br><br>

## NLP Taxonomy — Monitored Hashtags

## Semantic Anchors

Used as semantic filters, BM25 query expansion terms, and topic modeling anchors.

| Group | Hashtags |
|---|---|
| **Real Estate Funds** | `#FII` · `#FIIs` · `#FundosImobiliarios` · `#Fundos` |
| **Income & Yield** | `#RendaPassiva` · `#Dividendos` · `#DividendYield` · `#PassiveIncome` |
| **Investments** | `#Investimentos` · `#Investidor` · `#CarteiraDeInvestimentos` · `#Investing` · `#InvestimentoInteligente` |
| **Financial Market** | `#MercadoFinanceiro` · `#Mercado` · `#Financeiro` · `#BolsaDeValores` · `#B3` · `#Acoes` |
| **Financial Education** | `#EducacaoFinanceira` |


