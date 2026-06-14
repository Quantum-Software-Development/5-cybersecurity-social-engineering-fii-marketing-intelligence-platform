# Arquitetura Medallion — Bronze · Silver · Gold
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

---

## Visão Geral

A plataforma segue o padrão **Medallion Architecture** (Delta Lake / Databricks pattern), organizado em três camadas de qualidade crescente de dados:

```
FONTES EXTERNAS (21)
        │
        ▼
┌───────────────────────────────────┐
│  🥉 BRONZE  data/external/        │  ← Dados brutos, congelados (frozen)
│  Fidelidade máxima ao original    │    Nunca modificados após NB01
└───────────────┬───────────────────┘
                │ NB02 — ETL + Quality Gates
                ▼
┌───────────────────────────────────┐
│  🥈 SILVER  data/silver/          │  ← Dados limpos e normalizados
│  text_clean · timestamps UTC      │    Enriquecidos com sentimento em NB05
└───────────────┬───────────────────┘
                │ NB03–NB06 — Analytics
                ▼
┌───────────────────────────────────┐
│  🥇 GOLD    data/gold/            │  ← Datasets analíticos e de negócio
│  Rankings · MI Signals · Dashboard│    Prontos para FastAPI e Streamlit
└───────────────────────────────────┘
```

---

## Princípios de Design

| Princípio | Implementação |
|---|---|
| **Imutabilidade do Bronze** | NB01 grava `data/external/` uma vez. NB02–NB07 leem apenas. |
| **Separação de responsabilidades** | Cada camada tem schema, qualidade e propósito definidos. |
| **Reprodutibilidade** | `RANDOM_SEED=42` + dataset frozen = resultados idênticos entre execuções. |
| **Rastreabilidade** | `article_id` e `source` preservados do Bronze ao Gold. |
| **Progressão de qualidade** | Bronze: fidelidade. Silver: limpeza. Gold: valor analítico. |

---

## Camada Bronze — Data/External

**Propósito:** Preservar os dados exatamente como foram coletados.

**Responsabilidade:** Exclusiva do NB01.

**Regras:**
- Schema: 17 campos fixos
- `article_id = SHA-256(url)` — chave primária imutável
- `published_at = None` para conteúdo scraping (sem data real)
- Deduplicação por `article_id` e `content_hash` antes do freeze
- Compressão: Parquet snappy

**Arquivos:**
```
data/external/
├── bronze_all_articles.parquet  ← Input primário do NB02
├── rss_fii_articles.parquet
├── portal_fii_articles.parquet
└── reddit_fii_posts.parquet
```

---

## Camada Silver — Data/Silver

**Propósito:** Texto limpo, datas normalizadas, qualidade garantida.

**Responsabilidade:** NB02 (ETL base) + NB05 (enriquecimento de sentimento).

**Transformações NB02:**
1. `text_clean` — remove HTML, URLs, boilerplates
2. `published_dt` — ISO-8601 UTC (nullable para scraping)
3. `source_label` — domínio → nome comercial
4. `word_count`, `char_count`, `has_content`
5. **3 Quality Gates** (null IDs · word_count ≥ 30 · dedup Window)

**Enriquecimento NB05:**
- `polarity_score`, `sentiment_label`
- `flag_*` e `score_*` para 6 categorias de sinais FII

**Arquivos:**
```
data/silver/
├── silver_articles.parquet      ← 22 colunas base
└── silver_enriched.parquet      ← 22 + 17 colunas de sentimento/sinais
```

---

## Camada Gold — Data/Gold

**Propósito:** Datasets analíticos prontos para modelos, dashboards e APIs.

**Responsabilidade:** NB03, NB04, NB05, NB06, NB07.

**Subdiretórios:**

| Subdiretório | Gerado por | Conteúdo |
|---|---|---|
| `word_count/` | NB03 | Frequência de termos (MapReduce RDD) |
| `tfidf_bm25/` | NB04 | Índices TF-IDF + BM25 + funções de busca |
| `sentiment/` | NB05 | Stats de sentimento por fonte e por mês |
| `marketing_intelligence/` | NB06 | MI Signals por FII, top articles, funil TOFU/MOFU/BOFU |
| `dashboard/` | NB07 | Datasets consolidados para FastAPI + Streamlit |

---

## Fluxo de Dependências entre Notebooks

```
NB00 ──────────────────────────────────► NB01–NB07 (settings.py + logger.py)
NB01 ──────────────────────────────────► NB02 (data/external/*.parquet)
NB02 ──────────────────────────────────► NB03, NB04, NB05
NB03, NB04, NB05 ──────────────────────► NB06
NB03, NB04, NB05, NB06 ────────────────► NB07
NB07 ──────────────────────────────────► FastAPI, Streamlit, Groq chatbot
```

---

## Comparação com Padrões Industriais

| Aspecto | Implementação deste projeto | Padrão industrial (Databricks Delta Lake) |
|---|---|---|
| Camadas | Bronze / Silver / Gold | Bronze / Silver / Gold |
| Formato | Apache Parquet (snappy) | Delta format (Parquet + transaction log) |
| Imutabilidade | Freeze manual (NB01 único writer) | ACID transactions via Delta |
| Schema enforcement | Contrato documentado + validação RDD | Schema enforcement nativo Delta |
| Deduplicação | drop_duplicates + Window | MERGE INTO com Delta |
| Processamento | PySpark local[*] | PySpark em cluster Databricks/EMR |
| Escalabilidade | Até ~500 MB de corpus | Petabytes |

> **Contexto acadêmico:** A implementação com PySpark local[*] e Parquet snappy demonstra os mesmos princípios arquiteturais, patterns de código e modelo de qualidade de dados que seriam usados em escala industrial — apenas sem a infraestrutura de cluster.

---

*Medallion Architecture v1.0.0 · Investor Intelligence Platform FIIs Brasil*
