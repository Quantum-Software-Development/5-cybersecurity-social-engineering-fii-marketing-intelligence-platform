
# STAGE 01 — Strategic Analysis

## Intelligence Platform for Real Estate Investment Funds (FII)

**Version:** 1.0  
**Date:** May 2026  
**Project:** Marketing and Investor Behavior Intelligence System  
**Specialization:** Brazilian Real Estate Investment Funds (FIIs)

---

## 1. Anchoring to the academic briefing

### 1.1 Project Integrator context

This project is a specialization of the challenge described in the Project Integrator — 2nd Term (May–June 2025), in the course of Cybersecurity and Social Engineering, subject Distributed Systems and Machine Learning.

The original briefing proposes to:

- process content from websites and social networks;  
- count words and identify the occurrence of specific terms;  
- understand which terms should be associated with the product/service to increase the chance of appearing for the target audience in a **positive** context;  
- identify the best channels for top-of-funnel strategy;  
- use PySpark and Jupyter;  
- present results in a dashboard with tables and charts;  
- implement sentiment analysis.

The briefing also adds a **mandatory extra challenge**:  
identify high-frequency words/terms that appear in a **negative context** for the target audience (and treat this as a sentiment analysis problem).

### 1.2 Theme and specialization

**Chosen theme:** Brazilian Real Estate Investment Funds (FIIs).

**Why FIIs make sense here:**

- **Growing market:** FIIs are a growing segment on B3, with more than 400 funds listed and assets under management above BRL 180 billion.  
- **Digitally active audience:** FII investors are present in forums, specialized portals, Reddit (e.g. r/investimentos, r/farialimabets) and other networks.  
- **Rich context for NLP:** discussions involve fundamental analysis, management, vacancy, dividends, risk, etc. It is a natural universe for NLP, BM25 and sentiment analysis.  
- **Top-of-funnel focus:** asset managers, brokers and analysis platforms need to know where this audience is and which terms generate positive engagement.  
- **Relevance of the extra challenge:** the FII market is highly sensitive to negative narratives (defaults, high vacancy, dividend cuts, “FII default”), so detecting high-frequency terms in negative contexts is critical.

---

## 2. Business problem and context

### 2.1 Strategic problem

The central question is:

> How can an FII asset manager, broker or analysis platform identify the most strategic digital channels to attract new investors (top of funnel) and which terms to associate with its communication to maximize positive engagement?

**Key challenges:**

- **Fragmented audience:** FII investors are scattered across dozens of portals, forums, subreddits, Telegram groups, YouTube channels, etc.  
- **A lot of noise, little signal:** much of the content is speculative, meme-driven or low quality.  
- **Ambiguous sentiment:** a simple term like “FII” may have high frequency but be used mostly in negative contexts.  
- **All sources treated as equal:** in practice, all sources are handled as if they had the same value, even when their audience profiles differ a lot.  
- **Inefficient marketing spend:** top-of-funnel campaigns are directed to channels without clear evidence that they reach the most relevant investors.

### 2.2 Target audience

**Primary audience:**

- FII asset managers;  
- Brokers and distributors;  
- Analysis and data platforms (Funds Explorer, FIIs.com.br etc.);  
- Financial media desks and editorial teams.

**Secondary audience:**

- Individual investors interested in FIIs;  
- Marketing teams designing top-of-funnel campaigns;  
- Data analysts and data scientists studying investor behavior.

### 2.3 Current gaps

| Gap                               | Description                                                              | Impact                                             |
|-----------------------------------|--------------------------------------------------------------------------|---------------------------------------------------|
| Lack of source ranking            | No ranking of sources by strategic relevance (BM25/TF‑IDF)               | Marketing decisions made on intuition             |
| Superficial sentiment analysis    | Generic tools do not understand specific financial context               | Ambiguous terms are misinterpreted                |
| Unstructured data                 | Content from Reddit, forums and portals is poorly structured or not at all | Loss of insight and hard comparison              |
| No topic clusters                 | No automatic segmentation into sub-themes (paper, brick, management, etc.) | Poorly segmented communication                  |
| Manual processing                 | Manual analysis of 20+ sources is impractical                            | Late or non-existent insights                     |

---

## 3. Platform value proposition

### 3.1 What this system is not

This system is **not**:

- a generic sentiment dashboard;  
- a “pretty” word cloud;  
- just a news aggregator;  
- a generic social listening tool;  
- a plain word counter.

### 3.2 What this system is

This system is:

- a **distributed marketing intelligence platform**;  
- an **investor behavior analysis system**;  
- an **audience discovery engine for FIIs**;  
- a **financial content relevance engine based on BM25**;  
- a **market intelligence platform powered by NLP**;  
- an **investor intelligence decision support system**;  
- a **top-of-funnel analytical platform**;  
- a first step towards a **RAG system** focused on FIIs (as a future evolution).

### 3.3 Business value

For asset managers, brokers and platforms, this solution:

- **Highlights the most strategic channels** for top-of-funnel actions, combining:  
  - BM25 relevance ranking;  
  - density of discussions about FIIs;  
  - audience profile;  
  - predominant sentiment.  

- **Suggests strategic terms** to be used in communication:  
  - high-frequency terms in positive context;  
  - relevant topic clusters;  
  - technical vocabulary that drives engagement in qualified channels.  

- **Flags high-risk channels**, where:  
  - key terms appear mostly in negative context;  
  - discussions are dominated by narratives that may damage fund or manager reputation.  

- **Delivers actionable intelligence**, via:  
  - an executive dashboard with KPIs;  
  - rankings of sources and terms;  
  - sentiment analysis by source and term;  
  - a conversational chatbot to explore the data.

---

## 4. High-level solution view

### 4.1 Main components (conceptual overview)

```text
┌─────────────────────────────────────────────────────────────┐
│                 FII INTELLIGENCE PLATFORM                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  WEB SCRAPING│  │   PYSPARK    │  │  NLP + BM25  │      │
│  │   (21 SOURCES)│▶│ DISTRIBUTED  │▶│    ENGINE    │      │
│  │              │  │  PROCESSING  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│          │                    │                   │        │
│          ▼                    ▼                   ▼        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          MinIO DATA LAKE (Bronze/Silver/Gold)        │  │
│  └──────────────────────────────────────────────────────┘  │
│          │                                        │        │
│          ▼                                        ▼        │
│  ┌──────────────┐                          ┌──────────────┐│
│  │   FASTAPI    │                          │  STREAMLIT   ││
│  │   BACKEND    │◀────────────────────────▶│  DASHBOARD   ││
│  │              │                          │  + CHATBOT   ││
│  └──────────────┘                          └──────────────┘│
│                                                   │        │
│                                                   ▼        │
│                                          ┌────────────────┐│
│                                          │   GROQ LLM     ││
│                                          │ (llama-3.1)    ││
│                                          └────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Value flow

- **Ingestion:** scraping of 20 financial portals + Reddit.  
- **Distributed processing:** PySpark organizes data into Bronze/Silver/Gold layers in the MinIO data lake.  
- **Relevance:** BM25 ranks contents and sources relevant to FIIs.  
- **NLP:** analysis of terms, topics, clusters and sentiment.  
- **Extra challenge:** detection of high-frequency terms in negative context, by term and by channel.  
- **Exposure:** FastAPI provides endpoints for other components.  
- **Visualization:** Streamlit presents KPIs, rankings and analyses.  
- **Interaction:** a Groq-based chatbot allows conversational exploration of intelligence.

---

## 5. Data sources (21 sources)

### 5.1 Categorization

The 21 sources are distributed into:

- **20 portals/platforms** (editorial, data, blogs, news)  
- **1 social network** (Reddit, focusing on investment- and FII-related subreddits)

A possible organization:

- **Category A – High-authority editorial portals**  
  Portals with journalistic analysis, manager interviews and macro coverage.

- **Category B – Analysis and data platforms**  
  Sites focused on quantitative data, rankings and indicators for FIIs.

- **Category C – Blogs and independent media**  
  Educational content, opinions from independent analysts and educators.

- **Category D – Market news**  
  Focused on material facts, deals, announcements and market moves.

- **Category E – Communities and forums (Reddit)**  
  User-generated content with high volume and strong sentiment polarization.

### 5.2 Reddit vs editorial portals

| Dimension                      | Reddit                                    | Editorial portals                         |
|--------------------------------|-------------------------------------------|-------------------------------------------|
| Volume                         | Very high (daily posts and comments)      | Medium (more spaced articles)             |
| Analytical quality             | Variable, lots of opinion and memes       | High, with editorial curation             |
| Sentiment                      | Strongly polarized                        | Generally neutral or analytical           |
| Authenticity                   | High (direct investor voice)             | Medium (editorial mediation)              |
| BM25 relevance                 | Lower (informal vocabulary, noise)        | Higher (technical vocabulary, key terms)  |
| Negative-context risk          | High                                      | Low                                       |
| Top-of-funnel value            | High (community discovery)                | High (authority and credibility)          |

**Insight:** Reddit is excellent to discover communities, language and “raw” sentiment, but requires strong filtering for noise and negative context. Editorial portals provide technical relevance and authority.

---

## 6. BM25 as relevance backbone

### 6.1 Why BM25

BM25 is a widely used relevance ranking algorithm in search systems. It considers:

- term frequency in a document;  
- term rarity across the collection (IDF);  
- document length (normalization).

In this platform:

- prevents short, low-information posts from dominating the ranking just by volume;  
- favors longer, denser documents with relevant terms (for example, full FII analyses);  
- combines naturally with the idea of “where it is worth investing time and budget”.

### 6.2 Example interpretation

- A long, technical report about a specific FII on Funds Explorer tends to score high on BM25.  
- A short Reddit post like “FII trash lol” tends to score low, even if “FII” appears.

---

## 7. NLP for topics and sentiment

### 7.1 Topics and clustering

Goal: identify **subtopics** within the FII universe, such as:

- paper vs brick FIIs;  
- discussions about active vs passive management;  
- focus on vacancy, dividends, P/VP, credit risk, etc.;  
- specific criticisms (defaults, dividend cuts, management issues).

This enables:

- communication segmented by FII type;  
- understanding which themes dominate each channel;  
- aligning campaigns with topics that already have traction in the right communities.

### 7.2 Sentiment

Goal: label text segments as positive, negative or neutral, taking financial context into account.

Examples:

- “FII cut dividends” → negative  
- “FII increased dividends” → positive  
- “vacancy 50%” → negative  
- “vacancy 5%” → positive  

The approach combines:

- generic sentiment models as a baseline;  
- domain-specific dictionaries/tuning for FIIs;  
- co‑occurrence analysis to understand context (words appearing near key terms).

---

## 8. Extra challenge: high-frequency terms in negative context

### 8.1 The challenge

From the original briefing:  
identify high-frequency terms that are used in negative contexts for the target audience.

In the FII context, this means:

- detecting central terms (for example, “FII”, “vacancy”, “dividend”, “management”, “default”);  
- measuring what percentage of their occurrences appear in negative context;  
- ranking terms and channels by their **risk level**.

### 8.2 Strategy

- extract n‑grams (e.g. “FII default”, “high vacancy”, “cut dividends”);  
- analyze co‑occurrence of negative words (“trash”, “default”, “bad”, “trap”) near “FII”;  
- compute risk scores by term and by source (for example, % of negative mentions of “FII” in each channel);  
- feed this into the dashboard, with a dedicated risk/alerts section.

---

## 9. Problem → solution (summary)

| #  | Problem                                              | Proposed solution                                      | Main technology                      |
|----|------------------------------------------------------|--------------------------------------------------------|--------------------------------------|
| 1  | Fragmented audience across 20+ sources               | Automated scraping + distributed processing            | Web Scraping + PySpark               |
| 2  | No clear view of where to invest marketing           | BM25-based ranking of sources                          | BM25 Engine                          |
| 3  | Ambiguous sentiment for key terms                    | Contextual sentiment analysis                          | NLP + Sentiment Analysis             |
| 4  | High-frequency terms in negative context             | Co‑occurrence detection and risk ranking               | N‑grams + context                    |
| 5  | No channel prioritization                            | Executive dashboard with KPIs and recommendations      | Streamlit + Plotly                   |
| 6  | Raw, unstructured data                               | Bronze/Silver/Gold pipeline                            | MinIO + Parquet + PySpark            |
| 7  | Manual analysis is infeasible                        | Scalable distributed execution                         | PySpark                              |
| 8  | Low interactivity when exploring insights            | Conversational chatbot                                 | Groq + `llama-3.1-8b-instant`        |
| 9  | No topic clusters                                    | Topic modeling / theme grouping                        | NLP + TF‑IDF                         |
| 10 | Decisions made by intuition                          | Quantitative + qualitative, data-driven intelligence   | Full integrated stack                |

---

## 10. Briefing → solution mapping

This platform was designed to meet the original briefing point by point:

- **Process websites and social networks:** scraping of 20 portals + Reddit.  
- **Count words and terms:** word frequency analysis via PySpark.  
- **Identify specific terms:** BM25 + keyword extraction.  
- **Maximize positive exposure in ads:** sentiment analysis + positive term ranking.  
- **Identify best channels:** ranking of sources (BM25 + sentiment).  
- **Use PySpark and Jupyter:** educational/operational notebook with PySpark pipeline.  
- **Dashboard with tables and charts:** Streamlit + Plotly.  
- **Sentiment analysis:** dedicated NLP module.  
- **Extra challenge (negative context):** specific pipeline for high-risk terms by channel.  
- **Academic + professional delivery:** full README, notebook, dashboard, backend and React presentation.


