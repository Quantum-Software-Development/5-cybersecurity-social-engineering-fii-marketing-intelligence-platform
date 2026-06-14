# MapReduce Word Count — Metodologia e Implementação
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

---

## O Paradigma MapReduce

MapReduce é um modelo de programação para processamento de grandes volumes de dados em paralelo, proposto por Dean & Ghemawat (2004) no contexto do Google File System.

A lógica central divide o processamento em duas funções puras:

```
MAP:    (key_in, value_in)    → list[(key_out, value_out)]
REDUCE: (key_out, list[value]) → list[result]
```

Para contagem de palavras:
```
MAP:    (doc_id, text)  → [(word, 1), (word, 1), ...]
REDUCE: (word, [1,1,1]) → (word, total_count)
```

---

## Implementação com PySpark RDD

### Por que RDD e não DataFrame API?

| Critério | RDD | DataFrame API |
|---|---|---|
| Analogia com MapReduce puro | ✅ Direta e explícita | ❌ Abstração implícita |
| Requisito acadêmico | ✅ Demonstra MapReduce nativo | ❌ Oculta o paradigma |
| Performance | Ligeiramente inferior | Superior (otimizações Catalyst) |
| Uso educacional | ✅ Ideal | Adequado para produção |

Para este projeto acadêmico, RDD foi escolhido para demonstrar explicitamente o paradigma MapReduce que o professor requisitou.

---

## Código Completo do MapReduce (NB03)

```python
# ── Entrada ───────────────────────────────────────────────────────────────────
texts_rdd = spark.sparkContext.parallelize(df_silver["text_clean"].tolist())

# ── MAP PHASE ─────────────────────────────────────────────────────────────────
tokens_rdd = (
    texts_rdd
    .flatMap(lambda text: tokenize(text))    # texto → stream de tokens
    .map(lambda w: (w, 1))                   # cada token → (word, 1)
)

# ── REDUCE PHASE ──────────────────────────────────────────────────────────────
word_counts_rdd = (
    tokens_rdd
    .reduceByKey(lambda a, b: a + b)         # soma por token
    .sortBy(lambda x: x[1], ascending=False) # ordena por frequência
    .collect()                               # materializa no driver
)

# ── RESULTADO ─────────────────────────────────────────────────────────────────
df_global_wc = pd.DataFrame(word_counts_rdd, columns=["term", "count"])
```

---

## Tokenizador PT-BR

### Pipeline de Normalização

```
Input: "Os Fundos Imobiliários pagaram Dividendos! Leia mais: https://..."
         │
         ▼ lowercase
       "os fundos imobiliários pagaram dividendos! leia mais: https://..."
         │
         ▼ regex [a-zà-ü]{3,}
       ["os", "fundos", "imobiliários", "pagaram", "dividendos", "leia", "mais"]
         │
         ▼ NFD normalize (remove acentos para lookup)
       ["os", "fundos", "imobiliarios", "pagaram", "dividendos", "leia", "mais"]
         │
         ▼ remove stopwords NLTK PT
       ["fundos", "imobiliarios", "pagaram", "dividendos"]
```

### Código
```python
_TOKEN_RE = re.compile(r"[a-zà-ü]{3,}", re.IGNORECASE | re.UNICODE)

def _norm(s: str) -> str:
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii").lower()

def tokenize(text: str) -> list:
    if not text: return []
    tokens = [_norm(t) for t in _TOKEN_RE.findall(text.lower())]
    return [t for t in tokens if t not in STOPWORDS_PT and len(t) >= 3]
```

### Por Que NFD Normalize?
`imobiliários` e `imobiliarios` devem mapear ao **mesmo** termo no índice.
NFD (Canonical Decomposition) separa o caractere base do acento, permitindo remover acentos sem perder a forma base da palavra.

---

## Word Count por Fonte (Source × Term)

Extensão do MapReduce básico para dimensão de fonte:

```python
source_rdd = spark.sparkContext.parallelize(
    list(zip(df_silver["source_label"], df_silver["text_clean"]))
)

source_wc_rdd = (
    source_rdd
    .flatMap(lambda x: [((x[0], w), 1) for w in tokenize(x[1])])
    .reduceByKey(lambda a, b: a + b)
    .map(lambda x: (x[0][0], x[0][1], x[1]))
    .sortBy(lambda x: (x[0], -x[2]))
    .collect()
)
```

---

## TOFU Term Frequency

Filtra os resultados do MapReduce global pelos termos do léxico TOFU:

```python
TOFU_TERMS = [
    "fii", "fiis", "fundo", "fundos", "imobiliario", "dividendo",
    "dividendos", "provento", "proventos", "rendimento", "yield",
    "cotista", "cota", "cotas", "vacancia", "renda", "tijolo",
    "papel", "logistica", "shopping", "laje", "galpao", ...
]

df_tofu = df_global_wc[df_global_wc["term"].isin(TOFU_TERMS)]
```

---

## Negative Context Analysis (Desafio do Professor)

**Problema:** Identificar palavras-chave de investimento que aparecem predominantemente em contextos negativos.

**Solução:** Para cada termo de risco, calcula a razão de co-ocorrência com palavras negativas em uma janela de ±5 tokens:

```python
NEGATIVE_WORDS = {
    "queda", "crise", "perda", "prejuizo", "calote", "default",
    "inadimplencia", "vacancia", "desvalorizacao", "reducao", ...
}

def negative_ctx_ratio(text: str, term: str, window: int = 5) -> float:
    tokens = tokenize(text)
    if term not in tokens: return 0.0
    positions = [i for i, t in enumerate(tokens) if t == term]
    neg_windows = 0
    for pos in positions:
        win = set(tokens[max(0, pos-window): pos+window+1])
        if win & NEGATIVE_WORDS:
            neg_windows += 1
    return neg_windows / len(positions)
```

**Interpretação do resultado:**
- `negative_ctx_ratio = 0.8` → "vacância" aparece em contexto negativo em 80% das ocorrências
- `negative_ctx_ratio = 0.2` → "dividendo" aparece em contexto negativo em apenas 20% das ocorrências

---

## Outputs Gerados (4 Artefatos Gold)

| Arquivo | Dimensões | Uso downstream |
|---|---|---|
| `global_word_count.parquet` | (V × 3): term, count, rank | Vocabulário base TF-IDF/BM25 (NB04), word cloud (NB07) |
| `source_word_count.parquet` | (S×V × 3): source, term, count | Análise de cobertura por portal (NB06, NB07) |
| `tofu_frequency.parquet` | (T × 5): term, count, rank, tofu_rank, n_sources | Marketing strategy (NB06) |
| `negative_context.parquet` | (R × 5): term, count, ratio, risk_level, n_docs | Risk detection (NB05, NB06) |

---

## Escalabilidade do Pattern MapReduce

O código escrito para `local[*]` (modo de desenvolvimento) é **idêntico** ao que rodaria em cluster:

```python
# Modo local (desenvolvimento)
spark = SparkSession.builder.master("local[*]").getOrCreate()

# Modo cluster (produção) — apenas mudança de master
spark = SparkSession.builder.master("yarn").getOrCreate()
# ou
spark = SparkSession.builder.master("spark://master:7077").getOrCreate()
```

A lógica RDD `.flatMap().map().reduceByKey().sortBy()` é distribuída automaticamente pelo Spark independente do master.

---

*MapReduce Word Count v1.0.0 · Investor Intelligence Platform FIIs Brasil*
