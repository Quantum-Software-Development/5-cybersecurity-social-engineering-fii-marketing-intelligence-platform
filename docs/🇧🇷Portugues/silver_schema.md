# Silver Schema — 22 Campos
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Camada:** Silver · **Localização:** `data/silver/` · **Gerado por:** NB02

---

## Transformações Bronze → Silver

| Transformação | UDF / Função | Detalhe |
|---|---|---|
| Limpeza de HTML | `clean_text()` | Remove tags, entidades HTML, URLs, boilerplates |
| Normalização de datas | `parse_date()` | Converte qualquer formato para ISO-8601 UTC |
| Label de fonte | `source_label()` | Domínio → nome comercial legível |
| Word count | `F.size(F.split(...))` | Número de palavras no `text_clean` |
| Char count | `F.length(...)` | Número de caracteres no `text_clean` |
| has_content flag | `word_count >= 30` | Flag boolean de qualidade mínima |

---

## Quality Gates (NB02)

| Gate | Condição | Ação se falha |
|---|---|---|
| **G1 — Null IDs** | `article_id != null AND url != null` | Descarta registro |
| **G2 — Word Count** | `word_count >= 30` | Descarta registro |
| **G3 — Dedup** | `Window.partitionBy("article_id").orderBy(collected_at DESC)` | Mantém mais recente |

---

## Schema Completo — 22 Campos

| # | Campo | Origem | Descrição |
|---|---|---|---|
| 1 | `article_id` | Bronze | SHA-256(url) — PK |
| 2 | `source` | Bronze | Domínio do portal |
| 3 | `source_type` | Bronze | `rss` · `scraping` · `reddit` |
| 4 | `source_label` | NB02 UDF | Nome comercial (ex: "InfoMoney") |
| 5 | `title` | Bronze | Título do artigo |
| 6 | `url` | Bronze | URL canônica |
| 7 | `author` | Bronze | Autor (nullable) |
| 8 | `published_at` | Bronze | Data original (nullable para scraping) |
| 9 | `published_dt` | NB02 UDF | ISO-8601 UTC normalizado (nullable) |
| 10 | `collected_at` | Bronze | ISO-8601 UTC da coleta |
| 11 | `language` | Bronze | `pt-br` |
| 12 | `tags` | Bronze | Tags separadas por vírgula |
| 13 | `query_used` | Bronze | FII_FILTER_TERM que ativou a coleta |
| 14 | `ingestion_method` | Bronze | Método de ingestão |
| 15 | `text_clean` | NB02 UDF | Corpo limpo — sem HTML, URLs, boilerplate |
| 16 | `word_count` | NB02 Spark | Número de palavras em `text_clean` |
| 17 | `char_count` | NB02 Spark | Número de caracteres em `text_clean` |
| 18 | `has_content` | NB02 Spark | `True` se `word_count >= 30` |
| 19 | `content_hash` | Bronze | MD5(title + content[:500]) |
| 20 | `metadata_json` | Bronze | JSON string com extras |

> `raw_html` é descartado no Silver — não tem utilidade após limpeza.

---

## Silver Enriched (NB05 adiciona 12 colunas)

Após NB05, o Silver é enriquecido com colunas de sentimento e sinais:

| Campo adicional | Tipo | Descrição |
|---|---|---|
| `polarity_score` | float | Score numérico [-1.0, +1.0] pelo léxico FII PT-BR |
| `sentiment_label` | str | `positivo` · `neutro` · `negativo` |
| `n_pos_terms` | int | Número de termos positivos encontrados |
| `n_neg_terms` | int | Número de termos negativos encontrados |
| `textblob_polarity` | float | Score TextBlob fallback (nullable) |
| `flag_dividendo` | bool | Presença de termos de dividendo/provento |
| `score_dividendo` | float | Intensidade [0.0, 1.0] |
| `flag_oportunidade` | bool | Presença de termos de oportunidade/compra |
| `score_oportunidade` | float | Intensidade [0.0, 1.0] |
| `flag_risco` | bool | Presença de termos de risco/volatilidade |
| `score_risco` | float | Intensidade [0.0, 1.0] |
| `flag_crise` | bool | Presença de termos de crise/queda |
| `score_crise` | float | Intensidade [0.0, 1.0] |
| `flag_vacancia` | bool | Presença de termos de vacância |
| `score_vacancia` | float | Intensidade [0.0, 1.0] |
| `flag_inadimplencia` | bool | Presença de termos de inadimplência/calote |
| `score_inadimplencia` | float | Intensidade [0.0, 1.0] |

---

## Boilerplates Removidos pela Limpeza

```python
_BOILER = [
    'leia mais', 'veja também', 'acesse aqui', 'clique aqui',
    'saiba mais', 'newsletter', 'assine já', 'você também pode'
]
```

---

## Relatório de Processamento (`silver_processing_report.json`)

```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "bronze_records_loaded": 1500,
  "gate_1_null_ids": 1498,
  "gate_2_word_count": 1350,
  "gate_3_dedup": 1320,
  "silver_records_final": 1320,
  "has_content_true": 1320,
  "source_type_counts": {"rss": 800, "scraping": 400, "reddit": 120},
  "min_word_count_threshold": 30,
  "spark_version": "3.5.0",
  "random_seed": 42
}
```

---

*Silver Schema v1.0.0 · Investor Intelligence Platform FIIs Brasil*
