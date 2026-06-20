

#  Investor Intelligence Platform 🇧🇷 FIIs Brazil 
###  Technical Documentation 

<br><br>

##  1. Project Overview

This project is a **data pipeline + retrieval + analytics system** focused on Brazilian REITs (FIIs).

It transforms raw financial news into structured datasets and enables:

* search and retrieval of relevant financial content
* sentiment analysis of news
* aggregated intelligence signals for FIIs
* API serving for external consumption
* interactive dashboard for analysis

<br><br>

##  2. System Architecture (Faithful)

### 🧠 Real System Flow

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart LR

A[External News Sources - RSS / Scraping / APIs] --> B[NB01 Data Ingestion]

B --> C[NB02 Cleaning & Normalization]

C --> D[NB03 NLP Processing - MapReduce Word Count]
C --> E[NB04 Retrieval Indexing - TF-IDF / BM25 / FAISS]
C --> F[NB05 Sentiment Analysis]

F --> G[NB06 FII Intelligence Metrics]

G --> H[NB07 Gold Dataset Builder]

H --> I[Git Repository - data gold parquet files]

I --> J[FastAPI Service Render]
I --> K[Streamlit Dashboard Cloud]

J --> K
```

<br><br>

##  3. Data Architecture (Medallion Pattern)

### 🥉 Bronze Layer (Ingestion)

* RSS feeds
* news scraping (requests + BeautifulSoup)
* external financial sources

📌 Raw, unstructured text

<br>

### 🥈 Silver Layer (Processing)

* text cleaning
* normalization
* deduplication
* formatting into structured records

📌 Clean structured dataset

<br>

### 🥇 Gold Layer (Final Outputs)

* sentiment scores
* retrieval indexes
* FII-level aggregated signals
* dashboard-ready datasets

📌 Business-ready intelligence layer

<br><br>

##  4. Retrieval System (Core Feature)

The system implements **hybrid search**:

* TF-IDF (lexical similarity)
* BM25 (ranking improvement)
* FAISS (semantic vector search)

<br><br>

### Retrieval Flow

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart LR

Q[User Query] --> T[TF-IDF Search]
Q --> B[BM25 Search]
Q --> F[FAISS Vector Search]

T --> R[Ranking Output]
B --> R
F --> R

R --> D[Top Relevant Articles]
```

<br><br>

##  5. NLP & Analytics Pipeline

Implemented in notebooks:

* NB03 → MapReduce word frequency (PySpark)
* NB05 → sentiment analysis (lexicon-based)
* NB06 → FII intelligence scoring

<br><br>

### Processing Chain

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart TD

TEXT[Clean News Data] --> NLP[NLP Processing]

NLP --> WC[Word Count - MapReduce]
NLP --> SENT[Sentiment Scoring]

SENT --> SCORE[FII Intelligence Score]
WC --> SCORE
```

<br><br>

## 6. Pipeline Execution (Batch System)

The system runs as a **sequential notebook pipeline**:

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart TD

NB00[NB00 Setup] --> NB01[Ingestion]
NB01 --> NB02[Cleaning]
NB02 --> NB03[NLP MapReduce]
NB02 --> NB04[TF-IDF / BM25 / FAISS]
NB02 --> NB05[Sentiment Analysis]
NB05 --> NB06[Intelligence Metrics]
NB06 --> NB07[Gold Dataset]
```

📌 Execution mode: **Batch processing (not streaming)**

<br><br>

## 🛰️ 7. API Layer (FastAPI)

The API serves processed data from the Gold layer.

### Responsibilities:

* expose structured endpoints
* serve retrieved articles
* handle query requests
* provide JSON responses

<br>

### API Flow

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart LR

GOLD[Gold Dataset - Git] --> API[FastAPI Service]

API --> A1[/articles endpoint/]
API --> A2[/query endpoint/]
API --> A3[/health endpoint/]

A1 --> CLIENT[External Consumers]
A2 --> CLIENT
A3 --> CLIENT
```

<br><br>

## 8. Dashboard Layer (Streamlit)

The dashboard provides:

* interactive visualization
* FII signals
* sentiment analysis
* ranked news exploration

<br><br>

### Dashboard Flow

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart LR

API[FastAPI] --> DASH[Streamlit Dashboard]
GOLD[Local Parquet Files] --> DASH

DASH --> USER[End User]
```

<br><br>

##  9. Deployment Architecture

### Real deployment setup:

* API → Render (FastAPI)
* Dashboard → Streamlit Cloud
* Data → Git repository (versioned)

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart LR

GIT[GitHub Repository] --> RENDER[Render - API]
GIT --> STREAMLIT[Streamlit Cloud]

RENDER --> STREAMLIT
```

<br><br>

##  10. Automation Pipeline

The system is updated via GitHub Actions (manual trigger):

<br>

```mermaid
%%{init: {'theme':'dark', 'themeVariables': {'primaryColor':'#00e5ff'}}}%%
flowchart LR

USER[Manual Trigger] --> ACTIONS[GitHub Actions]
ACTIONS --> PIPE[NB00 → NB07 Execution]
PIPE --> GOLD[Gold Dataset]
GOLD --> PUSH[Git Commit]
PUSH --> DEPLOY[Auto Deploy: Render + Streamlit]
```
<br><br>

## ⚠️ 11. Key Design Decisions

### Why Batch Processing?

* reproducibility of datasets
* easier debugging of pipelines
* lower infrastructure cost
* deterministic outputs

<br>

### Trade-offs

<br>

| Choice            | Impact                           |
| ----------------- | -------------------------------- |
| Batch processing  | not real-time                    |
| Git as storage    | simple but size-limited          |
| Notebook pipeline | slower than production ETL tools |

<br><br>

##  12. Technologies Used

* Python 3.11
* PySpark
* Pandas / NumPy
* Scikit-learn
* FAISS
* FastAPI
* Streamlit
* NLTK
* BeautifulSoup
* GitHub Actions

<br><br>

##  13. Final Summary

This system implements a full **data-to-intelligence pipeline**:

### Core capabilities:

* data ingestion (multi-source)
* cleaning and normalization
* NLP processing (MapReduce + sentiment)
* hybrid retrieval engine
* structured intelligence scoring
* API serving layer
* interactive dashboard

<br><br>

## ⚡️ Portfolio Positioning

This project demonstrates:

* data engineering pipeline design
* NLP processing at scale (PySpark)
* hybrid retrieval systems (IR + vector search)
* full-stack data product architecture
* production-style deployment workflow


