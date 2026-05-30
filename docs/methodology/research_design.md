# Research Design

### **Investor Intelligence Platform - FIIs Brasil 🇧🇷**  
*Methodological rationale for academic project*

<br><br>

## Research Question

> *Which digital channels (financial portals and social platforms) exhibit the highest concentration of qualified FII investors, and what is the dominant sentiment profile of each channel?*

**Sub-questions**:
1. Which portals produce the most technically rich FII content? (BM25)
2. What is the sentiment distribution across sources? (Sentiment Analysis)
3. Which sources mention FII-related terms in predominantly negative contexts? (Negative Context Detection)
4. What discussion clusters characterize investor behavior in each channel? (Topic Modeling)

<br><br>

## Research Type

| Dimension | Classification |
|-----------|---------------|
| **Nature** | Applied research |
| **Approach** | Quantitative + computational |
| **Strategy** | Descriptive analytics |
| **Horizon** | Cross-sectional (6-month window) |
| **Data type** | Secondary (publicly available text) |

<br><br>

## Methodological Choices

### Why BM25 (not Neural Embeddings)?

| Criterion | BM25 | BERT/Embeddings |
|-----------|------|-----------------|
| Interpretability | ✅ Full | ❌ Black box |
| No training data required | ✅ Yes | ❌ Requires labeled data |
| Computational cost | ✅ Low | ❌ High |
| PT-BR support | ✅ Language-agnostic | ⚠️ Requires PT-BR model |
| XAI compliance | ✅ Native | ❌ Requires post-hoc explanation |
| Academic defensibility | ✅ Established (Robertson 2009) | ✅ State-of-the-art |

**Decision**: BM25 is preferred for academic scope due to interpretability and XAI alignment.

<br><br>

### Why TextBlob + Lexicon (not FinBERT)?

- No publicly available **PT-BR** FinBERT model at project inception
- TextBlob provides a reproducible, deterministic baseline
- Lexicon augmentation adds domain specificity without training data
- Accuracy ~75–80% is sufficient for **channel-level** marketing decisions
- FinBERT fine-tuning on PT-BR FII corpus is a V2 item

<br>  

### Why LDA (not BERTopic)?

- LDA is interpretable, deterministic (`random_state=42`)
- BERTopic requires large embedding model (computational overhead)
- 5-topic model sufficient for investor behavior segmentation
- Academic transparency favors established methods

<br>

## Corpus Design

| Dimension | Decision |
|-----------|---------|
| **Sources** | 20 curated financial portals |
| **Time window** | 6 months (recent, relevant) |
| **Language** | PT-BR exclusively |
| **Behavioral Layer** | Reddit mandatory (Source #21) — `r/investimentos` · `r/farialimabets` |
| **Minimum article length** | 20 words / 100 characters |
| **FII filter** | Title or body must contain FII-related terms |

<br>

### Corpus Limitations

1. **Selection bias**: 20 portals ≠ complete universe of FII discussion
2. **Temporal limitation**: 6-month window may miss long-term trends
3. **Language**: PT-BR only; excludes English-language FII analysis
4. **Platform**: Excludes Twitter/X, Telegram, YouTube, LinkedIn

<br><br>

## Validation Strategy

| Component | Validation Method |
|-----------|------------------|
| BM25 rankings | Human review of top-5 sources |
| Sentiment | Sample of 50 articles reviewed manually |
| Topic labels | Expert interpretation of top terms |
| Negative context | Spot-check of flagged source-term pairs |

<br><br>

## Academic Contribution

1. **Methodological**: Demonstrates BM25 application for marketing channel intelligence in a specialized financial domain
2. **Applied**: Provides a reproducible framework for FII marketing decision support
3. **Governance**: Demonstrates Responsible AI and CRISP-DM in a real-world NLP context
4. **Educational**: Applies Humanistic AI principles in a fintech context

<br><br>

## References

- Robertson, S. E., & Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. *Foundations and Trends in IR*, 3(4), 333–389.
- Chapman, P., et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS.
- Mitchell, M., et al. (2019). Model Cards for Model Reporting. *ACM FAccT*.
- Blei, D., Ng, A., & Jordan, M. (2003). Latent Dirichlet Allocation. *JMLR*, 3, 993–1022.


