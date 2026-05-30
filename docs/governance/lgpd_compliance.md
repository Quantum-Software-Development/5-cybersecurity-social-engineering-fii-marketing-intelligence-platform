# LGPD Compliance

### **Investor Intelligence Platform - FIIs Brasil 🇧🇷**  
#### *Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018)*

<br><br>

## Summary Assessment

| Requirement | Status | Evidence |
|-------------|--------|---------|
| Personal data processed? | ✅ No | Public editorial content only |
| Legal basis established? | ✅ Yes | Legitimate interest (academic research) |
| Data minimization applied? | ✅ Yes | Only title, body, source, date retained |
| Purpose limitation? | ✅ Yes | Marketing intelligence exclusively |
| Transparency? | ✅ Yes | Open methodology, documented sources |
| Security measures? | ✅ Yes | No PII stored; secrets managed via `st.secrets` |
| Data subject rights applicable? | N/A | No personal data collected |



<br><br>

## Data Classification

### Data Collected and Processed

| Data Type | Classification | LGPD Applicability |
|-----------|---------------|-------------------|
| Article headlines | Public editorial content | Not personal data |
| Article body text | Public editorial content | Not personal data |
| Portal domain name | Technical identifier | Not personal data |
| Publication date | Metadata | Not personal data |
| Author name (RSS) | Potentially personal | Minimized — used as `author` field only |

<br>

### Data NOT Collected

- User identities
- IP addresses
- Browser fingerprints
- Behavioral tracking
- Cookie data
- Geographic data
- Financial data of individuals

<br><br>

## Legal Basis (Art. 7 LGPD)

**Art. 7, IX — Legitimate Interest**:

Processing is conducted for **academic research** (Projeto Integrador — PUC-SP) with the legitimate interest of understanding digital channel dynamics in the FII market. Processing is limited to publicly available editorial content.

**Conditions met**:
- Processing necessary for legitimate purpose
- Fundamental rights of data subjects not overridden
- No adverse impact on individuals

<br><br>

## Article Author Names — Special Consideration

RSS feeds may include author names (e.g., "Maria Silva"). Treatment:

1. **Stored as metadata** for source attribution, not profiling
2. **Not cross-referenced** with any personal database
3. **Not published** in dashboard outputs
4. **Minimized** — only used for data provenance documentation
5. **Removable** — `author` field can be dropped without impacting any analysis


<br><br>

## Data Retention

| Layer | Retention | Justification |
|-------|-----------|---------------|
| Bronze | Project duration | Audit trail for academic evaluation |
| Silver | Project duration | Reproducibility requirement |
| Gold | Project duration | Production API serving |
| External (frozen) | Indefinite | Deterministic reproducibility |

Post-project: All layers except `data/external/` should be deleted from local storage.

<br><br>

## Reddit Data — Additional Considerations

Reddit posts are **publicly visible content**. However:
- Usernames may be pseudonyms (not necessarily anonymized)
- Reddit posts are collected from **investment-focused subreddits** (`r/investimentos`, `r/farialimabets`)
- No cross-referencing with other datasets occurs
- Reddit is **Behavioral Intelligence Layer (Source #21) only** — can be fully excluded without impact

**Recommendation**: For public deployment, strip Reddit `author` field and use only post title and body.

<br><br>

## Dashboard — User Privacy

The Streamlit dashboard:
- Collects **no user data**
- Uses **no cookies** (default Streamlit behavior with `gatherUsageStats = false`)
- Logs **no IP addresses** (Streamlit Cloud responsibility)
- Requires **no authentication**
- Has **no user accounts**

<br><br>

## Contact & Oversight

| Role | Person / Institution |
|------|---------------------|
| Academic supervisor | Eduardo Savino Gomes — PUC-SP / FACEI |
| Data controllers | Fabiana Campanari · Pedro Vyctor Almeida |
| Institution | Pontifical Catholic University of São Paulo |

<br><br>

*Last updated: 2026-05-26 | Legal reference: Lei nº 13.709/2018 (LGPD)*  
*See also: `docs/governance/responsible_ai.md`*
