# BM25 — Fundação Matemática e Implementação
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Referência principal:** Robertson, S. E., & Zaragoza, H. (2009). *The Probabilistic Relevance Framework: BM25 and Beyond.* Foundations and Trends in Information Retrieval, 3(4), 333–389.

---

## Fórmula Completa

```
BM25(D, Q) = Σ IDF(qi) · [f(qi,D) · (k1+1)] / [f(qi,D) + k1 · (1 − b + b · |D|/avgdl)]
```

| Componente | Símbolo | Descrição |
|---|---|---|
| Termo da query | `qi` | i-ésimo token da query Q |
| Frequência no documento | `f(qi, D)` | Número de vezes que `qi` aparece no documento D |
| Comprimento do documento | `\|D\|` | Total de tokens no documento D |
| Comprimento médio do corpus | `avgdl` | Média de `\|D\|` para todos os documentos |
| Saturação de frequência | `k1 = 1.5` | Controla o retorno decrescente de termos repetidos |
| Normalização por comprimento | `b = 0.75` | Penaliza documentos mais longos que a média |
| IDF do termo | `IDF(qi)` | `log((N - df(qi) + 0.5) / (df(qi) + 0.5) + 1)` |

---

## Parâmetros Usados

| Parâmetro | Valor | Justificativa |
|---|---|---|
| `k1` | **1.5** | Valor padrão recomendado por Robertson & Zaragoza. Menor = saturação mais rápida. |
| `b` | **0.75** | Valor padrão recomendado. `b=0` = sem normalização. `b=1` = normalização total. |

### Efeito de k1 (saturação de frequência)

```
k1=0.5  → Quase binário (presença/ausência)
k1=1.5  → Retorno decrescente moderado ← usado aqui
k1=3.0  → Frequência tem mais peso (mais próximo de TF puro)
```

### Efeito de b (normalização por comprimento)

```
b=0.0   → Sem normalização — documentos longos favorecem
b=0.75  → Normalização moderada ← usado aqui
b=1.0   → Normalização total por avgdl
```

---

## IDF — Fórmula Robustificada

```
IDF(qi) = log( (N - df(qi) + 0.5) / (df(qi) + 0.5) + 1 )

N     = total de documentos no corpus
df(qi) = número de documentos contendo qi
```

O `+ 0.5` nas duas posições e `+ 1` no final evitam:
- IDF negativo para termos muito comuns
- Divisão por zero

---

## Implementação no Projeto

### Biblioteca usada
```python
from rank_bm25 import BM25Okapi
```

### Construção do índice (NB04)
```python
# corpus_tokens = List[List[str]] — tokens normalizados NFD
bm25_index = BM25Okapi(
    corpus_tokens,
    k1=1.5,
    b=0.75,
)
```

### Consulta (NB04 / NB06)
```python
query_tokens = tokenize_pt("dividend yield FII logística")
scores = bm25_index.get_scores(query_tokens)  # ndarray shape (N_docs,)
top_k_indices = scores.argsort()[::-1][:10]
```

---

## BM25 vs TF-IDF — Diferenças Fundamentais

| Aspecto | TF-IDF (sklearn) | BM25Okapi |
|---|---|---|
| **Normalização de comprimento** | Indireta (via IDF) | Explícita (`b=0.75, avgdl`) |
| **Saturação de frequência** | `sublinear_tf=True` aplica `log(1+tf)` | Explícita via fórmula com `k1` |
| **Operação de busca** | Similaridade coseno (espaço vetorial) | Soma ponderada de scores por termo |
| **Corpus dependente** | Sim (IDF calculado no fit) | Sim (avgdl calculado no init) |
| **Semântica** | Bag-of-words | Bag-of-words |
| **Desempenho em docs variáveis** | Médio | **Superior** |

---

## Score Híbrido (NB04 / NB06)

```python
def _minmax_norm(arr):
    mn, mx = arr.min(), arr.max()
    return np.zeros_like(arr) if mx == mn else (arr - mn) / (mx - mn)

s_tf_norm  = _minmax_norm(scores_tfidf)   # [0.0, 1.0]
s_bm_norm  = _minmax_norm(scores_bm25)    # [0.0, 1.0]
score_hybrid = 0.4 * s_tf_norm + 0.6 * s_bm_norm
```

**Por que 60% BM25?**
- O corpus FII contém artigos de 200 a 5.000 palavras
- BM25 normaliza explicitamente por `avgdl` → mais justo para documentos curtos
- TF-IDF complementa com sensibilidade a bigramas e termos raros

---

## Propriedades de XAI (Explicabilidade)

O BM25 é totalmente interpretável:

```python
# Score de cada termo da query para um documento específico
term_scores = {
    qi: bm25_index.get_scores([qi])[doc_index]
    for qi in query_tokens
}
# → {"dividendo": 2.34, "yield": 1.87, "logistica": 0.95, ...}
```

Cada score `mi_score` pode ser decomposto até o nível de:
`FII ticker → query_term → BM25_component → f(qi,D) + IDF(qi)`

---

## Limitações Conhecidas

| Limitação | Impacto no projeto | Mitigação |
|---|---|---|
| Bag-of-words (sem semântica) | "rendimento" ≠ "yield" para o BM25 | `ngram_range=(1,2)` no TF-IDF captura bigramas |
| Dependência de tokenização | Qualidade do tokenizador PT-BR afeta resultados | NFD normalization + stopwords NLTK |
| Corpus estático | Índice precisa ser reconstruído para novos docs | Reconstruir após cada NB01 + NB02 |
| Sem learning | Não aprende com feedback de relevância | MI score combina com sentimento como proxy |

---

*BM25 Foundation v1.0.0 · Investor Intelligence Platform FIIs Brasil*
