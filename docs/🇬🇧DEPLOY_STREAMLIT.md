
# 🚀 Deploying the Dashboard on Streamlit Community Cloud — Step-by-Step Guide

## Investor Intelligence Platform — FIIs Brasil 🇧🇷

> Prerequisite: the API must already be published on Render (see `DEPLOY_RENDER.md`).
> You will need the generated URL (e.g. `https://fii-intelligence-api.onrender.com`).

<br><br>

## ✅ Prerequisites

- [ ] Account on [Streamlit Community Cloud](https://share.streamlit.io) (GitHub login)
- [ ] **Public GitHub repository** — Streamlit Cloud requires this on the free tier
- [ ] API already published on Render, with its URL at hand
- [ ] `dashboard/requirements.txt` present (next to `Home.py` — see section 1.1 below)

<br><br>

## 🔧 Step 1.1 — About `dashboard/requirements.txt`

> ⚠️ **Important correction:** unlike what an earlier version of this guide
> stated, Streamlit Community Cloud does **not** always use the root
> `requirements.txt`. It first looks for a dependency file **in the same
> folder as the entrypoint** (`dashboard/Home.py`) and only falls back to the
> root if it does not find anything there — there is no field in the
> interface to manually point to a custom file.
>
> Therefore, this project uses `dashboard/requirements.txt` (7 packages:
> streamlit, pandas, numpy, pyarrow, plotly, requests, python-dotenv)
> instead of the root `requirements.txt` (~56 packages, including PySpark/Torch,
> which the dashboard does not use in production). Full details in
> [`docs/architecture/REQUIREMENTS_GUIA.md`](docs/architecture/REQUIREMENTS_GUIA.md).

```bash
git add dashboard/requirements.txt
git commit -m "chore: lightweight requirements for dashboard deploy"
git push
```


<br><br>

## 🔧 Step 2 — Update `Home.py`

Replace `dashboard/Home.py` with the version from this package (`dashboard/Home.py`).
The main difference: it automatically detects whether it should consume the API or
read local Parquet, via the `API_BASE_URL` variable:

```python
API_BASE_URL = (
    st.secrets.get("API_BASE_URL", "") if hasattr(st, "secrets") else ""
) or os.getenv("API_BASE_URL", "")
USE_API = bool(API_BASE_URL)
```

- **If `API_BASE_URL` is empty** → reads `data/gold/*.parquet` from the repository itself (development/local mode).
- **If `API_BASE_URL` is set** → all data calls become HTTP GET/POST requests to the API on Render.

This means the **same file** works both locally and in production — you do not
need to maintain two versions of the dashboard.

<br><br>

## 🔧 Step 3 — Commit the required files

```bash
git add dashboard/Home.py
git add dashboard/requirements.txt
git commit -m "feat: dashboard in hybrid mode (API + local fallback)"
git push
```

> ✅ Unlike Render (which uses `requirements-api.txt` via `render.yaml`),
> Streamlit Cloud automatically detects `dashboard/requirements.txt`
> because it is in the same folder as the entrypoint `dashboard/Home.py` — do
> not use the root `requirements.txt` here, it is too heavy (PySpark, Torch,
> Selenium) for what the dashboard actually needs. See
> [`docs/architecture/REQUIREMENTS_GUIA.md`](docs/architecture/REQUIREMENTS_GUIA.md)
> for full details.

<br><br>

## 🔧 Step 4 — Create the app on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Select the repository, branch (`main`), and main file:

```text
dashboard/Home.py
```

3. In **Advanced settings** → **Python version**: `3.11`
4. **Before clicking Deploy**, configure Secrets (next step)

***<br><br>

## 🔧 Step 5 — Configure Secrets (API URL)

In the app panel (even before the first deploy, under **Advanced settings**, or
later under **Settings → Secrets**), add:

```toml
API_BASE_URL = "https://fii-intelligence-api.onrender.com"
```

This is equivalent to an environment variable, but managed via the Streamlit
Cloud interface — it never appears in the code or in the public repository.

> 💡 **Testing locally with the real API before deploy:**
> ```bash > API_BASE_URL="https://fii-intelligence-api.onrender.com" streamlit run dashboard/Home.py > ```

<br><br>

## ✅ Step 6 — Deploy and Validate

1. Click **Deploy** — build takes ~2–5 minutes
2. Access the generated URL (e.g. `https://fii-intelligence.streamlit.app`)
3. In the sidebar, confirm the mode indicator:
    - 🟢 **Mode: API in production** → everything OK, consuming Render
    - 🔴 **API unavailable** → review `API_BASE_URL` in Secrets or check `/health` on Render
    - 🟡 **Mode: local Parquet** → `API_BASE_URL` was not configured (or is empty)

<br><br>

## 🔗 Step 7 — Close the CORS Loop

Go back to Render and update the `ALLOWED_ORIGINS` variable (which was `*`)
with the actual Streamlit Cloud URL:

```text
ALLOWED_ORIGINS=https://fii-intelligence.streamlit.app
```

This restricts who can call your API — a good security practice once you know
which origin is legitimate.

<br><br>

## ⚠️ Free Tier Limitations — Streamlit Community Cloud

| Limitation | Impact | Mitigation |
| :-- | :-- | :-- |
| **1 GB RAM** per app | More generous than Render (512MB) — handles the dashboard well | No action needed |
| **Public repository required** | Code (not sensitive data — you have none) is visible | Acceptable for this academic project |
| **App "sleeps" after inactivity** | First access after a while takes a few seconds to "wake up" | Acceptable for demo/presentation |
| **1 private app for free, others public** | Not a real limitation here, since the repo is already public | — |


<br><br>

## 🩺 Quick Troubleshooting

| Symptom | Probable cause | Solution |
| :-- | :-- | :-- |
| Sidebar shows 🔴 "API unavailable" | Render in cold start (spin-down) | Wait ~30–50s and reload the page |
| Error `ModuleNotFoundError: requests` | `requests` missing from `dashboard/requirements.txt` | Add `requests==2.34.2` to `dashboard/requirements.txt` (not to the root) |
| Dashboard shows outdated data | Render served old Gold data (old commit) | See automation section in `MANUAL_COMPLETO.md` |
| CORS error in browser console | `ALLOWED_ORIGINS` on Render does not include the Streamlit URL | Update `ALLOWED_ORIGINS` on Render as in Step 7 |


<br><br>

## 🔜 Next Step

With API + Dashboard published and connected, the next step is update
automation — see `COMPLETE_MANUAL.md`, section **"Real-time Automation and Update"**.

