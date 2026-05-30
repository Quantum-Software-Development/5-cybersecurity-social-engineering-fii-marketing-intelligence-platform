# Medallion Architecture

**Investor Intelligence Platform - FIIs Brasil 🇧🇷**

---

## Overview

The **Medallion Architecture** (also known as Delta Architecture) organizes data into progressive quality layers. Each layer adds structure, cleaning, and business value to the preceding one.

```mermaid
flowchart LR
    subgraph BRONZE ["🥉 Bronze — Raw"]
        B1["Raw HTML/JSON\nfrom RSS/portals"]
        B2["Reddit — Source #21\nr/investimentos\nr/farialimabets\nBehavioral Layer"]
    end

    subgraph SILVER ["🥈 Silver — Cleaned"]
        S1["HTML stripped\nDeduplicated\nNormalized schema"]
    end

    subgraph GOLD ["🥇 Gold — Analytics-Ready"]
        G1["source_ranking.parquet"]
        G2["sentiment_by_source.parquet"]
        G3["negative_context_terms.parquet"]
        G4["topic_clusters.parquet"]
    end

    BRONZE --> SILVER --> GOLD
```

---

## Layer Definitions

### 🥉 Bronze — Raw Ingestion

**Principle**: Write-once, never modify. All raw data preserved for audit.

| Property | Value |
|----------|-------|
| **Location** | `data/bronze/` |
| **Format** | Parquet (partitioned by `source`) |
| **Transformations** | None |
| **Schema** | Flexible (source-dependent) |
| **Retention** | Project lifetime |
| **Git** | ❌ Not committed (data/bronze/ in .gitignore) |
| **Notebook** | `NB01` |

**What's stored**: Raw RSS entries, raw HTML bodies, raw Reddit post JSON.

---

### 🥈 Silver — Cleaned & Normalized

**Principle**: Single source of truth for downstream modeling. Validated, deduplicated, schema-enforced.

| Property | Value |
|----------|-------|
| **Location** | `data/silver/` |
| **Format** | Parquet (single partition) |
| **Key transformation** | Bronze → Silver (NB02, PySpark) |
| **Schema** | Fixed (see `docs/governance/data_dictionary.md`) |
| **ID** | `SHA-256(url)` — deterministic |
| **Quality** | No nulls in key fields; word_count ≥ 20 |
| **Git** | ❌ Not committed |
| **Notebook** | `NB02` |

**Transformations applied**:
```
Raw HTML → BeautifulSoup stripping → clean text
Duplicate URLs → de-duplicated (keep first occurrence)
published_date (string) → timestamp
article_id = SHA-256(url)
word_count = len(body.split())
```

---

### 🥇 Gold — Business-Ready Analytics

**Principle**: Pre-computed, aggregated outputs optimized for API serving and dashboard consumption.

| Property | Value |
|----------|-------|
| **Location** | `data/gold/` |
| **Format** | Parquet (one file per analytical output) |
| **Produced by** | NB03, NB04, NB05 |
| **Consumers** | FastAPI (NB06), Streamlit (NB07) |
| **Git** | ❌ Not committed (regenerated from Silver) |
| **Notebook** | `NB05` (final Gold export) |

**Gold tables**:

| File | Rows | Description |
|------|------|-------------|
| `source_ranking.parquet` | 20 | BM25 + sentiment + strategic score per source |
| `sentiment_by_source.parquet` | ~60 | Sentiment distribution per source |
| `negative_context_terms.parquet` | Variable | Negative term co-occurrence per source |
| `topic_clusters.parquet` | 5 | LDA topic model outputs |

---

### 🔒 External — Frozen Dataset

**Purpose**: Deterministic reproducibility and demo stability.

| Property | Value |
|----------|-------|
| **Location** | `data/external/` |
| **Origin** | NB01 real scraping, then frozen |
| **Git** | ✅ Committed (exception to gitignore) |
| **Mutation** | Never modified after initial collection |

```
data/external/
├── rss_fii_articles.parquet      # RSS data
├── portal_fii_articles.csv       # Portal data
├── reddit_fii_posts.parquet      # Reddit — Behavioral Layer (Source #21)
├── data_collection_report.json   # Provenance metadata
└── README.md                     # Documentation
```

**Why frozen?** Scraping results vary by run (new articles appear, old ones disappear). Freezing ensures:
- NB02–NB07 produce identical results on any machine
- Academic evaluation is fair and reproducible
- No demo failures due to live API issues

---

## Pipeline Flow

```
NB01: RSS + Portals + Reddit → data/bronze/ → data/external/ (freeze)
NB02: data/external/ → PySpark ETL → data/silver/
NB03: data/silver/ → BM25 + Sentiment + NegCtx → Gold intermediaries
NB04: data/silver/ → LDA Topics → Gold intermediaries
NB05: All Gold intermediaries → data/gold/ (final)
NB06: data/gold/ → FastAPI → REST endpoints
NB07: FastAPI (or data/gold/ fallback) → Streamlit → User
```

---

*Last updated: 2026-05-26 | Pattern: Medallion Architecture (Databricks, 2021)*
