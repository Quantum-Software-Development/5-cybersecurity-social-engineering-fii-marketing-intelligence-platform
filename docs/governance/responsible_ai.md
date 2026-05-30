# Responsible AI Framework

### **Investor Intelligence Platform - FIIs Brasil 🇧🇷**  
#### *Aligned with EU AI Act principles, IEEE Ethically Aligned Design, and Brazilian LGPD* 🇪🇺

<br><br>

## Guiding Principle

> This platform is exclusively educational and analytical. It identifies marketing channel opportunities — it does not provide investment advice, portfolio recommendations, or financial guidance of any kind.

<br><br>

## Five Pillars

### 1. Transparency

**What it means**: Users and stakeholders can understand how decisions are made.

**Implementation**:
- BM25 scores are fully decomposable per term (see `docs/BM25_FOUNDATION.md`)
- Sentiment classification thresholds are explicit and documented
- Algorithm selection rationale documented in `docs/methodology/research_design.md`
- All code open and version-controlled (Git)
- Source selection criteria documented in this repository

**Verification**: Any ranking output in the dashboard can be traced back to specific term frequencies in specific source articles.

<br><br>

### 2. Fairness

**What it means**: No source receives preferential treatment based on anything other than its content.

**Implementation**:
- All 20 portals evaluated with identical BM25 queries
- No commercial relationships influence rankings
- Algorithm (BM25) is purely term-frequency based
- Reddit treated as Behavioral Intelligence Layer (Source #21) — never overrides portal evidence
- Source selection criteria documented (20 financially-focused portals covering diverse editorial perspectives)

**Known bias**: Source selection is curated — other portals exist but are not monitored. This **selection bias** is documented in NB05 and `docs/governance/risk_register.md`.

<br><br>

### 3. Privacy

**What it means**: No personal data is collected, processed, or stored.

**Implementation**:
- Only public editorial content is scraped
- No user tracking in dashboard
- No cookies, analytics, or behavioral profiling
- Author names from articles: optional metadata, not PII under LGPD context
- See full compliance: `docs/governance/lgpd_compliance.md`

**LGPD Basis**: Processing is based on legitimate interest (academic research) applied exclusively to public editorial content.

<br><br>

### 4. Accountability

**What it means**: Decisions are traceable and auditable.

**Implementation**:
- Bronze Layer preserved as immutable audit trail
- `article_id` = `SHA-256(url)` — deterministic, traceable
- `data_collection_report.json` records every collection run
- `RANDOM_SEED = 42` across all notebooks
- Data lineage documented: `docs/governance/data_lineage.md`
- Model card: `docs/governance/model_card.md`
- Academic supervision: Prof. Eduardo Savino Gomes — PUC-SP

<br><br>

### 5. Safety

**What it means**: The system cannot cause financial harm through its outputs.

**Implementation**:

> [!NOTE]
>
> ⚠️  Esta ferramenta possui caráter exclusivamente educacional e analítico.
>   Não constitui recomendação de investimento.
>   Consulte um assessor financeiro qualificado antes de tomar decisões.
>
> This disclaimer is:
>  - Appended to **every** Groq chatbot response (code-level enforcement)
>  - Displayed in dashboard header
>  - Stated in README
>  - Documented in model card
> 
> *The Groq system prompt explicitly instructs the model to* ***never recommend buying or selling any FII***.

<br><br>

## Explainable AI (XAI)

All model outputs include human-interpretable explanations:

| Component | Explanation Method |
|-----------|-------------------|
| BM25 ranking | Per-term score decomposition |
| Sentiment | Polarity score + classified threshold |
| Negative context | Co-occurring keyword identification |
| Topic modeling | Top-10 representative terms per topic |
| Source score | Weighted formula with all components visible |

<br><br>

## Humanistic AI

AI augments human decision-making capacity. It does not replace judgment:

- Rankings are **inputs to strategy**, not autonomous decisions
- Marketing team interprets and contextualizes outputs
- No automated actions are triggered by system outputs
- Human review recommended before acting on any insight

<br><br>

## Governance Contacts

| Role | Person |
|------|--------|
| Academic supervisor | Eduardo Savino Gomes (PUC-SP) |
| Technical lead | Fabiana Campanari |
| Data engineer | Pedro Vyctor Almeida |

<br><br>


*See also: `docs/governance/lgpd_compliance.md` · `docs/governance/model_card.md`*
