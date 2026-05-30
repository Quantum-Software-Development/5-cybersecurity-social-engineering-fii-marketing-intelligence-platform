# Data Lineage
### **Investor Intelligence Platform - FIIs Brasil 🇧🇷**

<br><br>


## End-to-End Data Flow

```mermaid
flowchart TD
    subgraph INGESTION ["NB01 — Data Ingestion"]
        A1["20 Financial Portals\nRSS Feeds"] --> BZ
        A2["Reddit (Source #21)\nr/investimentos\nr/farialimabets\nBehavioral Layer"] --> BZ
        BZ[("Bronze Layer\ndata/bronze/\nRaw Parquet")]
    end

    subgraph FREEZE ["Frozen Dataset"]
        BZ --> EX[("data/external/\nFrozen Real Data\nCommitted to Git")]
    end

    subgraph ETL ["NB02 — Bronze → Silver"]
        EX --> S1["HTML Cleaning\nDeduplication\nSchema Validation"]
        S1 --> SV[("Silver Layer\ndata/silver/\nClean Parquet")]
    end

    subgraph NLP ["NB03 — NLP Modeling"]
        SV --> N1["Word Count\n+ TF-IDF Vectorization"]
        SV --> N2["BM25 Ranking\n(Source-level)"]
        SV --> N3["Sentiment Analysis\n4-Layer PT-BR"]
        SV --> N4["Negative Context\nDetection"]
    end

    subgraph TOPICS ["NB04 — Topic Modeling"]
        SV --> T1["LDA Topic Modeling\n5 Topics"]
    end

    subgraph GOLD ["NB05 — Gold Layer"]
        N1 & N2 & N3 & N4 & T1 --> GL[("Gold Layer\ndata/gold/\nAnalytics Parquet")]
    end

    subgraph SERVE ["Production"]
        GL --> API["FastAPI\nRender\nNB06"]
        API --> DASH["Streamlit Dashboard\nStreamlit Cloud\nNB07"]
        DASH --> BOT["Groq Chatbot\nllama-3.1-8b-instant"]
        GL -. fallback .-> DASH
    end
```

<br><br>

## Layer Specifications

| Layer | Location | Format | Retention | Git |
|-------|----------|--------|-----------|-----|
| **Bronze** | `data/bronze/` | Parquet (partitioned by source) | Indefinite | ❌ gitignored |
| **Silver** | `data/silver/` | Parquet (single partition) | 6 months | ❌ gitignored |
| **Gold** | `data/gold/` | Parquet (one file per table) | Per analysis run | ❌ gitignored |
| **External (frozen)** | `data/external/` | Parquet + CSV + JSON | Permanent | ✅ committed |

<br><br>

## Transformation Lineage

### Bronze → Silver (NB02)

| Transformation | Input Field | Output Field | Logic |
|----------------|------------|--------------|-------|
| HTML stripping | `body_html` | `body` | BeautifulSoup |
| Deduplication | `url` | — | Drop exact URL duplicates |
| ID generation | `url` | `article_id` | `SHA-256(url)` |
| Date parsing | `published_date` (str) | `published_date` (timestamp) | PySpark `to_timestamp` |
| Quality filter | `body` | — | Drop if `word_count < 20` |
| Word count | `body` | `word_count` | `len(body.split())` |

<br>

### Silver → Gold (NB03–NB05)

| Output Table | Source Columns | Algorithm |
|-------------|---------------|-----------|
| `source_ranking` | `body`, `source` | BM25Okapi |
| `sentiment_by_source` | `body`, `source` | 4-layer PT-BR pipeline |
| `negative_context_terms` | `body`, `source` | Window co-occurrence |
| `topic_clusters` | `body` | LDA (Scikit-learn) |

<br><br>

## Reproducibility & System Guarantees

| Area | Mechanism | Purpose |
|---|---|---|
| **Bronze Layer** | Immutable ingestion | Preserves raw records without post-processing modifications |
| **Entity Consistency** | `article_id = SHA-256(url)` | Deterministic joins across pipeline executions |
| **Data Provenance** | `data_collection_report.json` | Tracks collection date, source counts, and dataset version |
| **Topic Modeling** | `RANDOM_SEED = 42` | Ensures reproducible LDA outputs across runs |


