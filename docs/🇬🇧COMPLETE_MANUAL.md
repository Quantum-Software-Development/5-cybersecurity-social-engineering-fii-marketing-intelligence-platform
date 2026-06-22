# Complete Execution and Deployment Manual
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Who this manual is for:** anyone who needs to run this project — from someone who has never opened a terminal to someone who is already a data engineer and just wants the right command. The sections marked "🎓 Explaining" are for beginners; if you already know the basics, you can skip straight to the code blocks.

<br><br>

## 📋 Table of Contents

1. [TL;DR — For Those Who Already Know](#1-tldr--for-those-who-already-know)
2. [Architecture Overview](#2-architecture-overview)
3. [Part 1 — Preparing the Local Environment](#3-part-1--preparing-the-local-environment)
4. [Part 2 — Running the Notebooks (NB00→NB07)](#4-part-2--running-the-notebooks-nb00nb07)
5. [Part 3 — Testing Locally (API + Dashboard)](#5-part-3--testing-locally-api--dashboard)
6. [Part 4 — Production Deployment](#6-part-4--production-deployment)
7. [Part 5 — Automation and Real-Time Updates](#7-part-5--automation-and-real-time-updates)
8. [Part 6 — Consolidated Troubleshooting](#8-part-6--consolidated-troubleshooting)
9. [Command Cheat Sheet](#9-command-cheat-sheet)

<br><br>

## 1. TL;DR — For Those Who Already Know

```bash
# Environment
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Full pipeline (mandatory order)
jupyter nbconvert --to notebook --execute --inplace notebooks/NB0{0,1,2,3,4,5,6,7}_*.ipynb

# Pre-flight check
python scripts/preflight_check.py

# Commit Gold data (required — Render/Streamlit Cloud are stateless)
git add -f data/gold/ data/external/ data/silver/
git commit -m "data refresh" && git push

# Local — API
uvicorn api.app:app --reload --port 8000

# Local — Dashboard (reads local Parquet, empty API_BASE_URL)
streamlit run dashboard/Home.py

# Production — Dashboard consuming API
API_BASE_URL="https://YOUR-API.onrender.com" streamlit run dashboard/Home.py
```

**Deploy:** Render via `render.yaml` (Blueprint) → Streamlit Cloud pointing `API_BASE_URL` in Secrets → update `ALLOWED_ORIGINS` on Render with the final Streamlit URL. Data updates are **manual**, through GitHub Actions `workflow_dispatch` (the "Run workflow" button), not cron-based. Details in Part 7.

<br><br>

## 2. Architecture Overview

### 🎓 Explaining

Think of this project as a 3-stage production line:

1. **Data factory** (the 8 Jupyter notebooks, NB00→NB07) — runs on your machine (or on GitHub Actions), processes news, and generates ready-to-use files.
2. **Warehouse** (the `data/gold/` folders, inside the Git repository itself) — where the ready files are stored.
3. **Showcase** (API on Render + Dashboard on Streamlit Cloud) — where external users see the result, without needing to know how to run Python.

```text
┌─────────────────────────────────────────────────────────────┐
│  YOUR MACHINE (or GitHub Actions)                           │
│  Jupyter: NB00 → NB01 → ... → NB07                         │
│  Generates: data/gold/*.parquet, *.pkl, *.npz, *.faiss     │
└───────────────────────┬──────────────────────────────────────┘
                        │ git push
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  GITHUB                                                     │
│  Stores the code AND the Gold data (committed)              │
└───────────┬───────────────────────────────┬─────────────────┘
            │ auto-deploy                   │ auto-deploy
            ▼                               ▼
┌───────────────────────┐      ┌────────────────────────────┐
│  RENDER               │      │  STREAMLIT COMMUNITY CLOUD │
│  api/app.py           │◄────│  dashboard/Home.py         │
│  Reads repo data/gold/│ HTTP │  Calls the API via requests│
└───────────────────────┘      └────────────────────────────┘
```

**Key point that often causes confusion:** the notebooks do **not run** inside Render or Streamlit Cloud. These two platforms only **serve** what has already been processed and stored in Git. The processing is done by you, on your machine (or through GitHub Actions, in Part 7).

<br><br>

## 3. Part 1 — Preparing the Local Environment

<br>

### 3.1 — What you need to install

| Tool | Purpose | Minimum version |
|---|---|---|
| Python | Run the notebooks, the API, and the dashboard | 3.10+ (3.11 recommended) |
| Java (JDK) | PySpark depends on it internally | 11+ |
| Git | Clone the repository, make commits | any recent version |

<br>

### 🎓 Explaining: what is a "terminal"?

A terminal (or "command prompt", "shell", "console") is a text window where you type commands instead of clicking icons. Every command in this manual should be typed there, followed by Enter.

- **Windows:** open "PowerShell" or "Command Prompt" (search in the Windows search bar).
- **Mac:** open the "Terminal" app (Spotlight → type "Terminal").
- **Linux:** usually `Ctrl+Alt+T`.

When you see a block like this:
```bash
python --version
```
it means: type exactly that (without the `$`, if shown) and press Enter.

### 3.2 — Checking what is already installed

```bash
python3 --version      # should show 3.10 or higher
java -version          # should show 11 or higher
git --version          # any version
```

If any of these commands returns an error ("command not found"), install:

**Python:**
- Windows/Mac: download from [python.org/downloads](https://www.python.org/downloads/)
- Linux (Ubuntu/Debian): `sudo apt install python3.11 python3.11-venv`

**Java (JDK 11):**
- Windows: download "Temurin 11" from [adoptium.net](https://adoptium.net/)
- Mac: `brew install openjdk@11`
- Linux: `sudo apt install openjdk-11-jdk`

**Git:**
- Windows: [git-scm.com/download/win](https://git-scm.com/download/win)
- Mac: already installed, or `brew install git`
- Linux: `sudo apt install git`

<br>

### 3.3 — Cloning the project

### 🎓 Explaining: what does "clone" mean?

"Cloning" means downloading a complete copy of the project (code + history) from GitHub to your computer.

```bash
git clone <REPOSITORY-URL>
cd <project-folder-name>
```

> 📌 The `<REPOSITORY-URL>` will be added here when the final link is shared (see the "Repository and Links" section of the main README).

<br>

### 3.4 — Creating the virtual environment

### 🎓 Explaining: why a "virtual environment"?

A virtual environment is an "isolated box" just for this project's Python libraries — this prevents them from conflicting with other versions installed on your computer for other projects.

```bash
# Create the environment (one time only)
python3 -m venv .venv

# Activate the environment (every time you work on the project)
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows (PowerShell or CMD)
```

When activated, the start of the terminal line changes to show `(.venv)` — that is how you know you are "inside the right box".

<br>

> ⚠️ You need to **reactivate** the virtual environment every time you open a new terminal. If commands start failing with "module not found", the first thing to check is whether `(.venv)` appears at the beginning of the line.

<br>

### 3.5 — Installing the dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take between 2 and 8 minutes the first time (it installs PySpark, scikit-learn, Streamlit, FastAPI and — if you use Layer 3 semantic search — `sentence-transformers` and `faiss-cpu`, which are heavier).

<br>

### 3.6 — Configuring environment variables (.env)

```bash
cp .env.example .env
```

Open the `.env` file in a text editor (Notepad, VS Code, any editor) and fill in:

<br>

| Variable | Required? | Where to get it |
|---|---|---|
| `GROQ_API_KEY` | No (but without it the chatbot runs in "demo mode") | [console.groq.com](https://console.groq.com) — free |
| `REDDIT_CLIENT_ID` / `SECRET` | No (NB01 has automatic fallback) | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |

<br>

> 🔒 **Never** share or commit the `.env` file — it is already protected 

<br><br>

## 4. Part 2 — Running the Notebooks (NB00→NB07)

### 🎓 Explaining: why does the order matter?

Each notebook **reads the result** of the previous one. NB04 does not work without the Silver data generated by NB02; NB07 does not work without the results of NB03, NB04, NB05, and NB06. It is like assembling furniture by following the manual — skipping one step blocks the next one.


<br>

### 4.1 — Opening Jupyter

```bash
jupyter lab notebooks/
```

This opens a browser tab with the notebook list. Double-click `NB00_setup.ipynb` to open the first one.

<br>

### 🎓 Explaining: how to run a notebook

Inside Jupyter, each notebook is divided into "cells". To run one cell: click it and press `Shift + Enter` (it moves to the next one automatically). To run **all cells at once**, use the menu **Run → Run All Cells**.

<br>

### 4.2 — Execution table (mandatory order)

| # | Notebook | What it does | Estimated duration | Attention |
|---|---|---|---|---|
| 1 | `NB00_setup.ipynb` | Installs dependencies, creates `config/settings.py`, `api/app.py`, `dashboard/Home.py`, `groq_client.py` | ~2-5 min | First run downloads packages — may take longer |
| 2 | `NB01_bronze_ingestion.ipynb` | Live collection from 21 sources (RSS + scraping + Google News) | ~15-30 min | Depends on your internet; some sources may fail (normal, there is fallback) |
| 3 | `NB02_bronze_to_silver.ipynb` | Cleans and normalizes collected text | ~5 min | — |
| 4 | `NB03_word_count_mapreduce.ipynb` | Counts words via PySpark (MapReduce) | ~5 min | — |
| 5 | `NB04_tfidf_bm25.ipynb` | Builds the 3 search indexes (TF-IDF, BM25, FAISS) | ~10-20 min | The FAISS layer downloads a ~120MB model the first time |
| 6 | `NB05_contextual_sentiment.ipynb` | Calculates sentiment via the FII PT-BR lexicon | ~10 min | — |
| 7 | `NB06_marketing_intelligence.ipynb` | Generates metrics per FII (MI Score) | ~15 min | — |
| 8 | `NB07_dashboard_dataset.ipynb` | Consolidates everything for dashboard/API | ~5 min | Final step — generates the files production will use |

**Estimated total time:** 1h to 1h30 on the first full run.

<br>

### 4.3 — How to know whether a notebook ran correctly

At the end of each notebook there is a validation cell that prints something like:

```text
OK  dashboard_articles.parquet
OK  dashboard_fii_signals.parquet
...
🎉 8/8 checks — NB0X COMPLETE
```

If `XX` (error) appears instead of `OK`, **do not move on** to the next notebook — first solve the problem (see Part 8, Troubleshooting).

<br>

### 4.4 — Running through the command line (without opening Jupyter visually)

Useful if you already trust the pipeline and just want to reprocess quickly:

```bash
for nb in notebooks/NB0{0,1,2,3,4,5,6,7}_*.ipynb; do
  echo "Running $nb..."
  jupyter nbconvert --to notebook --execute --inplace "$nb"
done
```
<br><br>

## 5. Part 3 — Testing Locally (API + Dashboard)

### 5.1 — Running the API locally

```bash
uvicorn api.app:app --reload --port 8000
```

Open in the browser: [http://localhost:8000/docs](http://localhost:8000/docs) — this is the **Swagger UI**, an automatic page that lists all endpoints and lets you test them by clicking, without writing code.

<br>

### 🎓 Explaining: what is an "API"?

Here, API means a small server that answers questions in JSON format (a structured text format) when someone accesses a specific address. For example, opening `http://localhost:8000/health` in the browser shows something like:

```json
{"status": "ok", "version": "1.0.0", "data_available": true}
```

<br>

### 5.2 — Running the Dashboard locally

In **another** terminal (leave the API running in the first one):

```bash
source .venv/bin/activate   # if not yet activated in this terminal
streamlit run dashboard/Home.py
```

It opens automatically at [http://localhost:8501](http://localhost:8501).

By default (without `API_BASE_URL` defined), the dashboard reads the Parquet files directly from the `data/gold/` folder — it does not even need the API running for that.

<br>

### 5.3 — Testing the Dashboard consuming the local API

```bash
API_BASE_URL="http://localhost:8000" streamlit run dashboard/Home.py
```

This simulates the exact production behavior, but entirely on your machine — useful for detecting problems before doing the real deployment.

<br><br>

## 6. Part 4 — Production Deployment

<br>

> This section summarizes the two dedicated guides: `DEPLOY_RENDER.md` (API) and `DEPLOY_STREAMLIT.md` (Dashboard). Read them for the full step-by-step with screenshots of each configuration. Here is the overall view and the correct order.

<br>

### 6.0 — Which `requirements*.txt` to Use in Each Scenario

<br>

Before installing anything, it is important to know that this project has **4 different dependency files** — using the wrong one in the wrong place does not break anything locally, but it makes deployment slower or riskier.

```text
fii-intelligence-platform/
├── requirements.txt              ← Notebooks (local, complete, ~56 packages)
├── requirements-dev.txt          ← + Jupyter/tests (adds to the above)
├── requirements-api.txt          ← API deployment on Render (~11 packages)
└── dashboard/
    ├── Home.py
    └── requirements.txt          ← Dashboard deployment on Streamlit Cloud (~7 packages)
```

<br>

| Scenario | Command |
|---|---|
| Run notebooks NB00–NB07 | `pip install -r requirements.txt` |
| Develop + test + lint | `pip install -r requirements.txt -r requirements-dev.txt` |
| Test the API locally (lightweight environment) | `pip install -r requirements-api.txt` |
| Test the Dashboard locally (lightweight environment) | `pip install -r dashboard/requirements.txt` |
| API deployment on Render | Automatic — `render.yaml` already points to `requirements-api.txt` |
| Dashboard deployment on Streamlit Cloud | Automatic — Streamlit Cloud detects `dashboard/requirements.txt` by itself |

<br>

### 🎓 Explaining: why does the dashboard have its own `requirements.txt`?

Streamlit Community Cloud **does not have** a field in the interface where you can manually point to a different dependency file — it always looks first **in the same folder as the app entry file**. Since our app starts at `dashboard/Home.py`, placing a `requirements.txt` inside the `dashboard/` folder makes Streamlit Cloud use it automatically, instead of falling back to the root `requirements.txt` (heavy, made for notebooks with PySpark/Torch/Selenium, which the dashboard does not use in production).

<br>

> 📖 **Learn more:** the full explanation, including the quote from the official Streamlit documentation confirming this behavior, and the list of packages from the main `requirements.txt` that exist as future reference but are not used by the current code — in [`docs/architecture/REQUIREMENTS_GUIA.md`](docs/architecture/REQUIREMENTS_GUIA.md).

<br><br>

### 6.1 — Why the order matters: API first, Dashboard second

The production dashboard needs a working API URL to point to (`API_BASE_URL`). Doing it the other way around means configuring the dashboard twice.

<br>

### 6.2 — Checklist before any deployment

```bash
python scripts/preflight_check.py
```

This script automatically checks:
- Whether all required Gold files exist
- Whether they are **committed in Git** (not blocked by `.gitignore`)
- Whether `.env` is not being versioned by accident
- Whether file sizes are within GitHub's limit

Fix every item marked as `FAIL` before continuing.

<br>

### 6.3 — Committing the Gold data

```bash
git add -f data/gold/dashboard/*.parquet data/gold/dashboard/*.json
git add -f data/gold/tfidf_bm25/*.pkl data/gold/tfidf_bm25/*.npz data/gold/tfidf_bm25/*.parquet
git commit -m "chore: Gold data for deployment"
git push
```

<br>

> ⚠️ If you enabled Layer 3 (FAISS), you also need to commit `embeddings.npy`, `faiss_index.faiss`, and `embedding_config.json`.

<br>

### 6.4 — API deployment (Render)

Summary (full details in `DEPLOY_RENDER.md`):

1. Create an account at [Render](https://render.com)
2. **New → Blueprint** → connect the repository → Render detects `render.yaml`
3. Manually configure the `GROQ_API_KEY` secret (it is not passed through Blueprint)
4. Wait for the build (~3-6 min) and test: `curl https://YOUR-API.onrender.com/health`

<br>

### 6.5 — Dashboard deployment (Streamlit Cloud)

Summary (full details in `DEPLOY_STREAMLIT.md`):

1. Create an account at [Streamlit Community Cloud](https://share.streamlit.io)
2. **New app** → repository → main file `dashboard/Home.py`
3. In **Secrets**, add:
   ```toml
   API_BASE_URL = "https://YOUR-API.onrender.com"
   ```
4. Deploy (~2-5 min) and check the 🟢 indicator in the published dashboard sidebar

<br>

### 6.6 — Closing the loop (CORS)

Go back to Render and update:

```text
ALLOWED_ORIGINS=https://YOUR-APP.streamlit.app
```

<br><br>

## 7. Part 5 — Automation and Real-Time Updates

This is probably the most important question for understanding what this system **is** and what it **is not**.

<br>

### 7.1 — How it works TODAY

```text
You click "Run workflow" on GitHub
        ↓
GitHub Actions runs NB00 → NB07 (GitHub's server, not yours)
        ↓
New Gold data is committed automatically to the repository
        ↓
Render detects the push → automatically redeploys the API
Streamlit Cloud detects the push → automatically redeploys the dashboard
        ↓
Dashboard and API now serve the new data
```
<br>

**The trigger is manual (`workflow_dispatch`), not scheduled.** This was a deliberate decision, not a technical limitation — see the justification below.

<br>

### 7.2 — What is the update frequency, in practice?

**The frequency is "whenever you decide to click".** There is no fixed number like "updates every X hours" — because no schedule (`cron`) was configured. Each workflow run processes the news published **up to the exact moment when you clicked**, and that snapshot stays frozen until the next time someone triggers the workflow again.

### How to trigger it manually

1. Go to the repository's **Actions** tab on GitHub
2. Click **"Atualizar Dados FII (Manual)"** in the workflow list
3. Click the **"Run workflow"** button (top-right corner)
4. (Optional) write a reason in the text field
5. Click **"Run workflow"** again to confirm

The execution takes between 20 and 45 minutes (the longest part is NB01, collecting from live sources). Follow the progress in the Actions tab itself — each notebook appears as a step.

<br>

### 7.3 — Why was this not automated with cron (fixed schedule)?

<br>

| Reason | Explanation |
|---|---|
| NB01 is fragile by nature | It does real-time scraping from 20+ sites — any of them may change layout, go offline, or block the request on a specific day |
| Silent failure is worse than visible failure | If a cron job runs overnight and partially fails, the dashboard may serve incomplete data without anyone noticing until someone checks manually |
| Control over the update moment | In an academic presentation, you want to be able to update minutes before — not depend on a fixed schedule that may or may not have matched that moment |

<br>

### 7.4 — How to enable scheduled updates (if you want to later)

After running the workflow manually a few times and trusting that it is stable, you can add a schedule. Edit `.github/workflows/atualizar_dados.yml` and add, alongside `workflow_dispatch`:

```yaml
on:
  workflow_dispatch:
    inputs:
      motivo:
        description: "Reason for the update"
        required: false
  schedule:
    - cron: "0 6 * * *"   # every day at 06:00 UTC (03:00 Brasília time)
```
<br>

> 🎓 **Explaining "cron":** it is a 5-field notation (minute, hour, day of month, month, day of week) used to schedule tasks. `"0 6 * * *"` means "minute 0, hour 6, any day, any month, any day of week" — in other words, every day at 6:00 UTC. To run every 6 hours, use `"0 */6 * * *"`.

<br>

### 7.5 — What Would Be Required for True Real Time (Streaming)

This section is **educational** — it explains the difference between what was built (batch processing, on demand) and what a true **streaming** system would require, and why the first option was chosen for this project.

<br>

### 🎓 Explaining: Batch vs. Streaming

<br>

| | **Batch (what exists now)** | **Streaming (true real time)** |
|---|---|---|
| How it processes | Processes an entire batch at once, from start to finish, and then stops | Processes each event (each new article) the moment it arrives, continuously, without ever "ending" |
| Analogy | Washing an entire pile of clothes at once | A conveyor belt that washes each item as soon as it drops onto the belt |
| When data becomes available | Only after the entire process finishes (minutes) | Seconds after the event happens |
| Infrastructure | Can "sleep" between executions (like GitHub Actions) | Needs to be **always on**, 24/7 |

<br>

### What would change in the architecture

<br>

```text
CURRENT ARCHITECTURE (On-demand batch)
┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│ You click    │───▶│ NB01→NB07    │───▶│ Parquet in  │
│ "Run workflow"│    │ (20-45 min)  │    │ Git         │
└──────────────┘    └──────────────┘    └─────────────┘

STREAMING ARCHITECTURE (what WOULD be required)
┌─────────────┐   ┌──────────────────┐   ┌────────────────────┐
│ RSS/Scraper │──▶│ Message Broker   │──▶│ Spark Structured   │
│ (always     │   │ (Kafka / Kinesis /│   │ Streaming          │
│ running)    │   │ Pub/Sub — always │   │ (processes each    │
│             │   │ running)         │   │ event, always      │
│             │   │                  │   │ running)           │
└─────────────┘   └──────────────────┘   └─────────┬──────────┘
                                                    ▼
                                         ┌────────────────────┐
                                         │ Database           │
                                         │ (Postgres/Delta Lake│
                                         │ — not static Parquet│
                                         │ )                  │
                                         └─────────┬──────────┘
                                                    ▼
                                         ┌────────────────────┐
                                         │ Dashboard with     │
                                         │ WebSocket/SSE      │
                                         │ (self-updating,    │
                                         │ no manual reload)  │
                                         └────────────────────┘
```

<br>

### Components that would need to be added/replaced

<br>

| Current component | Would be replaced by | Why |
|---|---|---|
| NB01 executed on demand | An always-on service (for example, a container running 24/7) that constantly checks sources | Streaming requires a continuous process, not a one-time execution |
| No message broker | Apache Kafka, AWS Kinesis, or Google Pub/Sub | To decouple "who collects" from "who processes", at high frequency |
| PySpark in batch mode (`spark.read.parquet`) | Spark Structured Streaming (`spark.readStream`) | It is a different Spark execution mode, designed for continuous flows |
| Static Parquet in `data/gold/` | Transactional database (Postgres) or Delta Lake/Iceberg | Pure Parquet was not designed to safely receive constant incremental writes with ACID guarantees |
| Streamlit with `st.cache_data(ttl=300)` (reloads every 5 min, under user action) | WebSocket or Server-Sent Events (SSE) pushing data to the browser | To make the screen update by itself, without the user reloading the page |
| Render free / Streamlit Cloud free | Always-on infrastructure (for example, AWS ECS, GCP Cloud Run with min-instances, or a dedicated VPS) | Free tiers hibernate due to inactivity — incompatible with "always processing" |

<br>

### Why this was not implemented in this project

1. **Cost:** message broker + continuous processing + always-on database do not fit in free tiers — they would require paid cloud credits (AWS/GCP/Azure).

2. **Complexity vs. academic objective:** the original course requirement was to demonstrate MapReduce, TF-IDF, BM25, and Medallion architecture — all batch-processing concepts. Streaming is a different paradigm, usually taught in specific "Real-Time Data Systems" courses.

3. **Nature of the data source:** news about FIIs does not change second by second like stock prices do. Updating a few times per day already captures the domain's real dynamics — streaming would add complexity without proportional value.

<br>

### When would it make sense to evolve to streaming?

If this project evolved into a real commercial product, monitoring market signals that change minute by minute (not day by day), streaming would become justified. At its current stage — marketing intelligence based on editorial coverage — batch updates, even daily or on demand, already match the standard used by real social listening and media monitoring tools in the market.

<br><br>

## 8. Part 6 — Consolidated Troubleshooting

<br>

| Symptom | Where it happens | Probable cause | Solution |
|---|---|---|---|
| `ModuleNotFoundError` | Any notebook | Virtual environment not activated, or `pip install` did not run | `source .venv/bin/activate` and repeat `pip install -r requirements.txt` |
| `java: command not found` | NB00-NB07 (any with Spark) | Java not installed | See section 3.2 |
| Notebook hangs on "Running" forever | NB01 | Some source is taking too long to respond | Wait — there is a 20s timeout per source; or interrupt and run again |
| `FileNotFoundError: silver_articles.parquet` | NB03, NB04, NB05 | NB02 was not executed, or failed | Go back and rerun NB02 |
| Local API returns 404 on `/articles` | Local API test | NB07 was not executed, or `data/gold/dashboard/` is empty | Execute NB07 |
| Render shows "Application failed to respond" | Deployment on Render | `data/gold/` was not committed to Git | Run `python scripts/preflight_check.py` and fix the `FAIL`s |
| Dashboard on Streamlit Cloud shows 🔴 "API unavailable" | Deployment on Streamlit | Render is in cold start (spin down), or `API_BASE_URL` is wrong in Secrets | Wait 30-50s and reload; check the URL in Secrets |
| CORS error in browser console | Production dashboard | `ALLOWED_ORIGINS` on Render does not include the Streamlit URL | Update the variable in Render (section 6.6) |
| GitHub Actions fails on the NB01 step | Manual workflow | Some source blocked requests from GitHub's server (different IP from yours) | Normal and sometimes expected — the pipeline has fallback (Google News RSS) and continues with the remaining sources |
| `faiss-cpu` fails to install | `pip install -r requirements.txt` | Usually missing a C++ compiler in the system (rare, more common on old Windows) | Use `pip install faiss-cpu --only-binary :all:` or a WSL2 environment on Windows |

<br><br>

## 9. Command Cheat Sheet

<br>

```bash
# ── Environment (full notebooks) ───────────────────────────
python3 -m venv .venv
source .venv/bin/activate              # Linux/Mac
.venv\Scripts\activate                 # Windows
pip install -r requirements.txt
cp .env.example .env

# ── Lightweight environment (test only the API or only the Dashboard) ──
pip install -r requirements-api.txt          # isolated API
pip install -r dashboard/requirements.txt    # isolated Dashboard

# ── Notebooks ──────────────────────────────────────────────
jupyter lab notebooks/                                  # visual interface
jupyter nbconvert --to notebook --execute --inplace notebooks/NB00_setup.ipynb   # command line, one by one

# ── Validation ─────────────────────────────────────────────
python scripts/preflight_check.py

# ── Local: API ─────────────────────────────────────────────
uvicorn api.app:app --reload --port 8000
curl http://localhost:8000/health

# ── Local: Dashboard ───────────────────────────────────────
streamlit run dashboard/Home.py                                    # local mode (Parquet)
API_BASE_URL="http://localhost:8000" streamlit run dashboard/Home.py  # local API mode

# ── Git: committing Gold data ──────────────────────────────
git add -f data/gold/ data/external/ data/silver/
git commit -m "data refresh"
git push

# ── Production: testing endpoints ──────────────────────────
curl https://YOUR-API.onrender.com/health
curl https://YOUR-API.onrender.com/articles?limit=5
curl -X POST "https://YOUR-API.onrender.com/query?question=Which+FII+pays+the+highest+dividend"

<br>

# ── Automation: trigger manual update ──────────────────────
# (via the GitHub interface — Actions tab → Run workflow)
# or via GitHub CLI, if installed:
gh workflow run "Atualizar Dados FII (Manual)" -f motivo="Pre-presentation update"
```

---

*Complete Manual  · Investor Intelligence Platform FIIs Brasil · PUC-SP FACEI*
