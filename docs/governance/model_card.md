# Model Card

**Investor Intelligence Platform - FIIs Brasil 🇧🇷**  
*Standardized model documentation per Google Model Card framework (Mitchell et al., 2019)*

---

## Model 1: BM25 Source Ranker

| Property | Value |
|----------|-------|
| **Model type** | Probabilistic ranking function |
| **Algorithm** | BM25Okapi (rank-bm25==0.2.2) |
| **Task** | Source relevance ranking |
| **Input** | Tokenized FII article corpus per source |
| **Output** | Float relevance score per source per query |
| **Parameters** | k1=1.5, b=0.75 |
| **Training** | None required (unsupervised) |
| **Notebook** | `03_nlp_bm25_sentiment.ipynb` |

**Performance**: No formal accuracy metric (ranking function). Validated through human review of top-5 sources.

**Limitations**: Lexical only; does not capture semantic equivalence (FII ≠ "fundo imobiliário").

**XAI**: Score fully decomposable per query term. See `docs/BM25_FOUNDATION.md`.

---

## Model 2: Sentiment Classifier (4-Layer PT-BR)

| Property | Value |
|----------|-------|
| **Model type** | Rule-based + lexicon hybrid |
| **Primary layer** | TextBlob (English baseline) |
| **Enhancement** | PT-BR financial lexicon |
| **Contextual** | Rule-based negation correction |
| **Extra challenge** | Negative Context Detection (window ±5) |
| **Input** | Raw article text (PT-BR) |
| **Output** | `positive` / `negative` / `neutral` + confidence |
| **Notebook** | `03_nlp_bm25_sentiment.ipynb` |

**Performance**: ~75–80% estimated accuracy on PT-BR financial text (no labeled dataset available; estimated from qualitative review).

**Known bias**: TextBlob trained on English corpus — PT-BR results require lexicon augmentation to be reliable.

**Limitations**:
- Sarcasm undetected
- Domain-specific idioms ("XPML11 está no chão" = negative) require manual lexicon entries
- Confidence scores are heuristic, not probabilistic

---

## Model 3: LDA Topic Model

| Property | Value |
|----------|-------|
| **Model type** | Unsupervised generative model |
| **Algorithm** | Latent Dirichlet Allocation |
| **Library** | Scikit-learn `LatentDirichletAllocation` |
| **n_components** | 5 |
| **max_iter** | 20 |
| **random_state** | 42 (fixed for reproducibility) |
| **Vectorizer** | TF-IDF (max_features=500, min_df=2) |
| **Notebook** | `04_topic_modeling_behavior.ipynb` |

**Typical topics identified**:
1. FII de Papel (CRI/CRA)
2. FII de Tijolo / Lajes Corporativas
3. FII de Logística / Galpões
4. Dividendos e Rendimentos
5. Análise de Gestão e Risco

**Limitations**: Topic labels are human-assigned post-hoc. Number of topics (k=5) is a design choice, not statistically optimized.

---

## Model 4: Groq AI Assistant

| Property | Value |
|----------|-------|
| **Provider** | Groq |
| **Model** | `llama-3.1-8b-instant` |
| **Purpose** | Educational Q&A about Gold layer findings |
| **Context** | Injected Gold parquet summaries (not RAG) |
| **Temperature** | 0.7 |
| **Max tokens** | 500 per response |
| **Secret** | `GROQ_API_KEY_FII` |

**Safety constraints**:
- Mandatory disclaimer appended to every response
- System prompt explicitly prohibits investment recommendations
- No financial advisory capability

**Disclaimer** (enforced at code level):
> *"Esta ferramenta possui caráter exclusivamente educacional e analítico. Não constitui recomendação de investimento."*

---

## Intended Use

This platform is designed for **marketing intelligence** — identifying which digital channels have the highest qualified FII investor concentration. It is **not** designed for:
- Investment advice
- Portfolio management
- Trading signals
- Individual investor profiling

---

*Last updated: 2026-05-26 | Version: 2.1*  
*Reference: Mitchell et al. (2019). Model Cards for Model Reporting. ACM FAccT.*
