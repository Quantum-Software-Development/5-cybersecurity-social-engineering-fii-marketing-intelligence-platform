
# 🔄 Data Update and Reprocessing — Technical Document

## Investor Intelligence Platform — FIIs Brasil 🇧🇷

> This document details two frequent questions about the system’s behavior in production: **(1)** how often the data is updated, and **(2)** whether each update requires reprocessing the entire pipeline from scratch. Both have direct answers that impact how the project should be operated and presented.[^1]

<br><br>

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [On-Demand vs. Scheduled — Two Different Concepts](#on-demand-vs-scheduled--two-different-concepts)
3. [Current System State](#current-system-state)
4. [How to Enable Scheduled Updates (Cron)](#how-to-enable-scheduled-updates-cron)
5. [Full Reprocessing vs. Incremental Processing](#full-reprocessing-vs-incremental-processing)
6. [Why Each Layer Resists (or Not) Incremental Processing](#why-each-layer-resists-or-not-incremental-processing)
7. [Execution Time Cost per Run](#execution-time-cost-per-run)
8. [What Would Be Needed for True Incremental Processing](#what-would-be-needed-for-true-incremental-processing)
9. [Recommendation and Trade-offs](#recommendation-and-trade-offs)
10. [See Also](#see-also)

<br><br>

## Executive Summary

| Question | Direct answer |
| :-- | :-- |
| Is there a fixed update interval today? | **No.** The trigger is manual (`workflow_dispatch`) — it updates when someone clicks, not at a scheduled time. |
| Does each update reprocess everything from scratch? | **Yes.** There is no incremental mode. NB01 re-collects all 21 sources; NB02–NB07 reprocess the entire corpus. |
| Is this an unresolved technical limitation or a deliberate choice? | **Deliberate choice**, with trade-offs documented below — it is not a bug, it is a characteristic of the chosen batch architecture. |
| Can this be changed? | Yes, in both dimensions — adding scheduling (`cron`) is simple; making processing incremental requires a non-trivial architectural redesign (detailed in section 6). |

<br><br>

## On-Demand vs. Scheduled — Two Different Concepts

These two concepts are often confused because both involve \"running the pipeline again\" — but they answer different questions: **who decides when** the update happens.[^1]


| Concept | Who decides \"when\" | Mechanism in GitHub Actions | Is it active in this project? |
| :-- | :-- | :-- | :-- |
| **On-demand** | A person, manually, at the moment they choose | `on: workflow_dispatch` | ✅ Yes |
| **Scheduled / periodic** | A clock, at fixed intervals, with no human intervention | `on: schedule: - cron: \"...\"` | ❌ No (intentionally disabled) |

Both mechanisms **can co-exist in the same workflow** — they are not mutually exclusive. It is perfectly possible to have a manual button *and* an automatic schedule at the same time; the decision in this project was to keep **only** the manual trigger for now and postpone scheduling.[^1]

<br><br>

## Current System State

```text
                    ┌─────────────────────────────┐
                    │   Someone clicks \"Run       │
                    │   workflow\" on GitHub       │
                    │   Actions tab               │
                    └──────────────┬──────────────┘
                                   │ (without this, nothing happens)
                                   ▼
            ┌──────────────────────────────────────────┐
            │  GitHub Actions runs, in sequence:       │
            │  NB00 → NB01 → NB02 → NB03 → NB04 →      │
            │  NB05 → NB06 → NB07                      │
            │  (20–45 minutes, depending on the        │
            │   response time of the 21 monitored      │
            │   sources)                               │
            └──────────────────┬───────────────────────┘
                               ▼
            ┌──────────────────────────────────────────┐
            │  git commit + git push (new Gold data)   │
            └──────────────────┬───────────────────────┘
                               ▼
            ┌─────────────────────┐      ┌──────────────────────────┐
            │  Render auto-       │      │  Streamlit Cloud auto-   │
            │  redeploys          │      │  redeploys               │
            │  (detects push)     │      │  (detects push)          │
            └─────────────────────┘      └──────────────────────────┘
                               │                          │
                               ▼                          ▼
                    Dashboard and API now serve the data from the moment of the click
```

**Practical consequence:** if nobody clicks the button for a week, the served data remains that of the last run, with no explicit \"stale data\" warning other than the `generated_at` field exposed in `/summary` and in the dashboard sidebar.[^1]

<br><br>

## How to Enable Scheduled Updates (Cron)

To transform the manual trigger into an automatic one, edit `.github/workflows/atualizar_dados.yml` and add a `schedule` block:[^1]

```yaml
on:
  workflow_dispatch:
    inputs:
      motivo:
        description: "Motivo da atualização"
        required: false
  schedule:
    - cron: "0 6 * * *"     # every day at 06:00 UTC (03:00 in Brasília)
```


### Cron syntax (5 fields)

```text
┌───────────── minute (0–59)
│ ┌─────────── hour (0–23)
│ │ ┌───────── day of month (1–31)
│ │ │ ┌─────── month (1–12)
│ │ │ │ ┌───── day of week (0–6, Sunday=0)
│ │ │ │ │
* * * * *
```

| Desired update | Cron expression |
| :-- | :-- |
| Once a day, at 6h UTC | `0 6 * * *` |
| Every 6 hours | `0 */6 * * *` |
| Every 12 hours | `0 */12 * * *` |
| Every Monday at 8h UTC | `0 8 * * 1` |
| Twice a day (6h and 18h UTC) | `0 6,18 * * *` |

> ⚠️ **Important about time zones:** GitHub Actions uses UTC. Brasília is UTC−3 (or UTC−2 during daylight saving, when applicable). For \"run at 6am in Brazil\", use `cron: \"0 9 * * *\"` (9h UTC = 6h Brasília, outside daylight saving).[^1]

> ⚠️ **Important about reliability:** GitHub does not guarantee execution at the exact second — at peak times, there may be a delay of a few minutes. This is acceptable for this use case (it is not a high-frequency trading system).[^1]

<br><br>

## Full Reprocessing vs. Incremental Processing

This is the most important distinction in this document, because it directly impacts **execution time** and **cost** (CI/CD minutes, external source requests).[^1]

### Definitions

| Term | Meaning |
| :-- | :-- |
| **Full reprocessing** (*full refresh*) | At each run, the entire pipeline runs from scratch: all sources are queried again, the whole corpus is cleaned, vectorized and analyzed again — regardless of what already existed before. |
| **Incremental processing** (*incremental update*) | At each run, only **new** data since the last run is processed; previous results are reused/merged, not recalculated. |

### What this project does today

**Full reprocessing, in all 8 steps, without exception.**[^1]


| Notebook | What is redone at each run |
| :-- | :-- |
| NB01 | All 21 sources are queried again from scratch — there is no control for \"fetch only items newer than the last collection\" |
| NB02 | All Bronze data is read and cleaned again (even if old articles have not changed) |
| NB03 | The word count (MapReduce) is recalculated for the entire corpus |
| NB04 | TF-IDF, BM25 and FAISS embeddings are **fully retrained/rebuilt** over the complete corpus |
| NB05 | Sentiment is recalculated for all articles, including those already analyzed before |
| NB06 | Marketing Intelligence metrics per FII are recalculated from scratch |
| NB07 | Final dashboard datasets are fully regenerated |

<br><br>

## Why Each Layer Resists (or Not) Incremental Processing

Not all layers have the same difficulty in becoming incremental.
This section details, layer by layer, **why** full reprocessing was the safest choice — and where there would be more or less technical difficulty to change that.[^1]

### 🟢 Layers that are relatively easy to make incremental

| Layer | Why it is viable | What would change |
| :-- | :-- | :-- |
| **NB01 — Ingestion** | RSS feeds already return items ordered by date; it is possible to store the most recent `published_at` per source and request only items after that | Add a \"checkpoint\" table (`last_collected_at` per source) and filter before saving |
| **NB05 — Sentiment** | Sentiment analysis is **per document**, independent — article A’s sentiment does not depend on article B | Run the sentiment function only on new `article_id`s and `UNION` with previous results |
| **FAISS (Layer 3 of NB04)** | FAISS indexes support **native incremental addition** via `index.add()` — no need to rebuild the entire index to add new vectors | Add only the embeddings of new articles to the existing index, without recreating it from scratch |

### 🔴 Layers that are structurally hard to make incremental

| Layer | Why it is hard | Technical detail |
| :-- | :-- | :-- |
| **TF-IDF (Layer 1 of NB04)** | The **IDF** (Inverse Document Frequency) of **every existing term** changes when a new document enters the corpus — it is not just \"add a row\", it is recomputing weights for the whole matrix | `IDF(t) = log((N+1)/(df(t)+1)) + 1` depends on `N` (total number of documents) and `df(t)` (in how many documents the term appears) — both change globally with each new article |
| **BM25 (Layer 2 of NB04)** | `avgdl` (average document length in the corpus) changes with each new article, affecting the normalization of **all** previous scores, not only new ones | The BM25 formula uses `avgdl` in the denominator for all `f(qi, D)` — a global value recomputed at each run |
| **NB03 — MapReduce Word Count** | Global word count is a cumulative aggregation — technically it *could* be incremental (add to the existing total), but `negative_ctx_ratio` depends on recomputing the context window over the full corpus to keep statistical consistency | It would require re-architecting as a true incremental aggregation (e.g. `reduceByKey` with state persisted between runs, not recreated each time) |
| **NB06 — Marketing Intelligence** | Each FII’s `mi_score` depends on averages (`sentiment_avg`, `relevance_avg`) over **all** articles related to that FII — adding a new article changes the average for all previous articles too | It would be necessary to store sums and counts (not only final averages) to allow incremental recomputation of means |

### Practical conclusion of this analysis

The layer that would **benefit the most** from incremental processing without sacrificing accuracy is **FAISS** (Layer 3) — it already supports this natively. The layers that **resist the most** are precisely those at the academic core of the project — **TF-IDF and BM25** — because their mathematics are defined relative to the entire corpus, not isolated documents.[^1]

This means a \"partially incremental\" version of the pipeline (e.g. only NB01 and NB05 incremental, NB04 and NB06 still full-refresh) is technically feasible and would be the most natural intermediate step — but it would still require rewriting checkpoint logic in at least two notebooks, which is beyond the scope of a simple configuration change.[^1]

<br><br>

## Execution Time Cost per Run

| Step | Approximate time | Depends on |
| :-- | :-- | :-- |
| NB00 | 2–5 min | First run downloads dependencies |
| NB01 | 15–30 min | **Largest variable** — response time of the 21 external sources |
| NB02 | 5 min | Corpus size collected |
| NB03 | 5 min | Corpus size |
| NB04 | 10–20 min | Training TF-IDF/BM25 + generating embeddings (FAISS) |
| NB05 | 10 min | Corpus size |
| NB06 | 15 min | 15 FIIs × N retrieval queries each |
| NB07 | 5 min | Final consolidation |
| **Total** | **~70–90 min** | — |

**Key point:** this time is **practically the same** whether the last update was 1 hour or 1 month ago — because everything is reprocessed from scratch. There is no \"fast update\" path today.[^1]

***

## What Would Be Needed for True Incremental Processing

Beyond the per-layer changes already described, a truly incremental architecture would require:[^1]


| New component | Function |
| :-- | :-- |
| **Checkpoint table** (e.g. `data/control/last_run_state.json`) | Store, per source, the timestamp of the last collected article |
| **Merge logic in NB02** | Instead of `df = pd.read_parquet(...)`, do `df_new = read_only_new(); df_total = pd.concat([df_existing, df_new])` |
| **Persistence of intermediate stats (NB03, NB06)** | Store partial sums/counts, not only final results, to allow incremental recomputation of means |
| **Periodic refit strategy for TF-IDF/BM25** | Even in an incremental scenario, these two models would need to be **fully retrained** at intervals (e.g. weekly), with new articles being served with approximate/outdated scores between refits |
| **Schema versioning** | Ensure that adding a new column in a notebook does not break merges with older data from previous runs |

> 📌 This list is deliberately simpler than the *streaming* architecture (Kafka, Spark Structured Streaming, transactional DB) described in `COMPLETE_MANUAL.md` — incremental batch processing is a middle ground between \"always full refresh\" (what exists now) and \"real-time streaming\" (which would be a much larger project). See the [\"See Also\"](#see-also) section below.[^1]

<br><br>

## Recommendation and Trade-offs

| Scenario | Recommendation |
| :-- | :-- |
| Academic delivery / demo | Keep as is — full reprocessing on demand is easy to explain and audit |
| Recurring use, still low volume | Add `schedule` (cron) to the current workflow, keeping full reprocessing — acceptable until collection runtime goes beyond ~1h |
| Evolution to real product, high volume of sources/articles | Prioritize incrementalization in NB01 and NB05 first (easier, higher gain), accept that NB04/NB06 remain periodic full-refresh |
| Need for minute/second latency | None of the above solves it — true streaming would be required (see `COMPLETE_MANUAL.md`) |

<br><br>

## See Also

- **`COMPLETE_MANUAL.md`**, section **\"Part 5 — Automation and Real-Time Updates\"** — explains the difference between batch and streaming, and what would be needed for a true real-time system (Kafka, Spark Structured Streaming, transactional DB, WebSocket).
- **`docs/methodology/MAPREDUCE_PATTERN.md`** — details the MapReduce implementation used in NB03, relevant to understanding why its current aggregation is not trivially incremental.
- **`docs/methodology/BM25_FOUNDATION.md`** — details the BM25 mathematical formula and why `avgdl` is a global corpus value, not per-document.
- **`.github/workflows/atualizar_dados.yml`** — file where the manual trigger is configured and where the `schedule` (cron) can be added.[^1]

<br><br>

*Data Update and Reprocessing · Investor Intelligence Platform FIIs Brasil*
