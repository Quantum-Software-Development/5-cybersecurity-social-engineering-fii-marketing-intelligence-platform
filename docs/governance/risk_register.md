# Risk Register

**Investor Intelligence Platform - FIIs Brasil 🇧🇷**  
*Risk assessment for academic project and production deployment*

---

## Risk Matrix

| ID | Risk | Category | Probability | Impact | Severity | Mitigation |
|----|------|----------|-------------|--------|----------|------------|
| R01 | Scraping blocked during demo | Technical | Medium | High | 🔴 High | Frozen dataset in `data/external/` |
| R02 | Reddit API unavailable | Technical | High | Low | 🟡 Medium | Reddit is Behavioral Intelligence Layer (Source #21); pipeline works without it |
| R03 | Render (API) downtime | Deployment | Low | High | 🟡 Medium | Dashboard dual mode: fallback to Gold parquet |
| R04 | Groq API rate limit exceeded | Technical | Low | Medium | 🟢 Low | Error handling + retry; disclaimer still shown |
| R05 | Sentiment accuracy ~75% PT-BR | Model | Certain | Medium | 🟡 Medium | 4-layer architecture; limitations documented |
| R06 | BM25 misses semantic synonyms | Model | High | Low | 🟢 Low | Documented limitation; hybrid retrieval in roadmap |
| R07 | Source selection bias | Data | Medium | Medium | 🟡 Medium | 20 curated portals documented; bias disclosed |
| R08 | `GROQ_API_KEY_FII` exposed | Security | Low | Critical | 🔴 High | `st.secrets` + `.gitignore` enforced |
| R09 | Temporal drift (stale dataset) | Data | High | Low | 🟢 Low | Frozen dataset labeled with collection date |
| R10 | LDA topic instability | Model | Medium | Low | 🟢 Low | `RANDOM_SEED=42` + frozen corpus |
| R11 | Financial misinterpretation by users | Ethical | Medium | High | 🔴 High | Mandatory disclaimer; educational framing |
| R12 | PII exposure in scraped data | Privacy | Low | Critical | 🔴 High | Public data only; author names stripped on request |

---

## Severity Definitions

| Level | Probability × Impact |
|-------|---------------------|
| 🔴 **High** | Requires immediate mitigation |
| 🟡 **Medium** | Managed with documented controls |
| 🟢 **Low** | Acceptable residual risk |

---

## R08 — Secret Exposure: Detailed Mitigation

```python
# Mandatory loading pattern (dashboard/chatbot/groq_client.py)
import os, streamlit as st

def get_api_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY_FII"]
    except Exception:
        key = os.getenv("GROQ_API_KEY_FII")
        if not key:
            raise EnvironmentError("GROQ_API_KEY_FII not configured")
        return key
```

**Controls**:
- `.streamlit/secrets.toml` in `.gitignore`
- `.env` in `.gitignore`
- `secrets.toml.example` committed (template only)
- Pre-commit hook recommended (future)

---

## R11 — Financial Misinterpretation: Ethical Safeguards

All user-facing components include:

1. **Dashboard header warning** (Streamlit)
2. **Chatbot system prompt restriction** (Groq API)
3. **Per-response disclaimer** (appended automatically)
4. **README disclaimer** (repository entry point)
5. **NB05 Governance section** (academic documentation)

---

## Open Risks (Accepted)

| Risk | Rationale for Acceptance |
|------|--------------------------|
| TextBlob PT-BR limitations | No labeled FII dataset available; 4-layer mitigation sufficient for academic scope |
| BM25 lexical limitations | Hybrid retrieval is V2 roadmap item |
| Temporal dataset staleness | Re-run NB01 to refresh; frozen dataset is labeled with collection date |

---

*Last updated: 2026-05-26 | Review cycle: Per academic semester*
