# Análise de Sentimento FII PT-BR — Metodologia
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

---

## Por Que Não Usar VADER ou TextBlob Genérico

| Ferramenta | Problema específico para FIIs |
|---|---|
| **VADER (EN)** | "dividend" → neutro. "yield" → positivo por contexto inglês genérico. "default" → neutro (deveria ser altamente negativo no contexto FII). |
| **TextBlob (PT genérico)** | "vacância" → positivo (confunde com inglês *vacancy* = oportunidade de emprego). "inadimplência" → neutro (sem calibração financeira). |
| **Léxico FII PT-BR** | Todos os 70+ termos calibrados explicitamente para contexto financeiro imobiliário brasileiro. Revisável, auditável, versionável. |

---

## Léxico FII PT-BR — Estrutura

Score de polaridade `∈ [-1.0, +1.0]`:
- `>= 0.15` → `positivo`
- `<= -0.15` → `negativo`
- Entre → `neutro`

### Termos Positivos

| Termo | Score | Justificativa |
|---|---|---|
| `dividendo` / `dividendos` | +0.85 | Sinal central de performance FII |
| `provento` / `proventos` | +0.80 | Sinônimo de dividendo em contexto FII |
| `rendimento` / `rendimentos` | +0.75 | Retorno financeiro do fundo |
| `lucro` / `lucros` | +0.75 | Resultado positivo do fundo |
| `crescimento` | +0.70 | Expansão patrimonial |
| `oportunidade` | +0.75 | Sinal de intenção de compra |
| `record` | +0.80 | Performance histórica superior |
| `excelente` | +0.80 | Qualidade editorial positiva |
| `yield` | +0.70 | Dividend yield — métrica central FII |
| `valorizacao` | +0.70 | Apreciação de cota |
| `retomada` | +0.60 | Recuperação após queda |
| `desconto` | +0.60 | Cota abaixo do valor patrimonial — oportunidade |
| `compra` / `comprar` | +0.65 | Intenção de aquisição |
| `renda` | +0.55 | Renda passiva — objetivo central do investidor FII |

### Termos Negativos

| Termo | Score | Justificativa |
|---|---|---|
| `inadimplencia` / `calote` | -0.90 | Risco de crédito máximo |
| `default` | -0.85 | Equivalente em inglês de calote |
| `colapso` / `falencia` | -0.90 a -0.95 | Cenário extremo negativo |
| `crise` / `crash` | -0.85 a -0.90 | Contexto macro negativo |
| `vacancia` / `vacante` | -0.70 a -0.75 | Fundamental negativo: imóveis desocupados |
| `desocupacao` | -0.75 | Sinônimo de vacância |
| `prejuizo` / `perda` | -0.70 a -0.80 | Resultado financeiro negativo |
| `queda` / `quedas` | -0.65 | Depreciação de cota |
| `corte` | -0.60 | Redução de proventos |
| `reducao` | -0.55 | Diminuição de qualquer métrica positiva |
| `desvalorizacao` | -0.70 | Queda do valor patrimonial |
| `deterioracao` | -0.70 | Piora progressiva de fundamentos |
| `volatilidade` | -0.45 | Risco de mercado |
| `incerteza` | -0.50 | Contexto macroeconômico indefinido |
| `negativo` | -0.70 | Resultado ou contexto negativo explícito |

---

## Categorias de Sinais (Signal Flags)

Além do score de polaridade, o sistema detecta 6 categorias de sinais contextuais:

### `flag_dividendo` — Sinal de Distribuição
**Termos:** dividendo, dividendos, provento, proventos, rendimento, rendimentos, distribuicao, yield, renda, income

**Uso de marketing:** Identifica conteúdo de conversão — artigos sobre pagamento de proventos tendem a gerar maior engajamento de investidores.

### `flag_oportunidade` — Sinal de Compra
**Termos:** oportunidade, compra, desconto, barato, valorizacao, crescimento, recomendado, expansao, lucro

**Uso de marketing:** Mapeia intenção BOFU — investidores considerando aquisição de cotas.

### `flag_risco` — Sinal de Atenção
**Termos:** risco, riscos, volatilidade, incerteza, negativo, deterioracao, problema, fraco, alerta

**Uso de marketing:** Identifica momentos de cautela no mercado — oportunidade de comunicação educativa.

### `flag_crise` — Sinal Crítico
**Termos:** crise, crash, colapso, queda, quedas, desvalorizacao, falencia, prejuizo, perda, grave, critico

**Uso de marketing:** Alerta máximo — conteúdo de gestão de crise ou necessidade de comunicação defensiva.

### `flag_vacancia` — Sinal de Fundamental
**Termos:** vacancia, vacante, desocupacao, desocupado

**Uso de marketing:** Específico para FIIs de tijolo — métrica crítica para shoppings, lajes e galpões.

### `flag_inadimplencia` — Sinal de Crédito
**Termos:** inadimplencia, calote, default

**Uso de marketing:** Específico para FIIs de papel — risco de crédito dos CRIs e debentures.

---

## Score de Intensidade dos Sinais

Cada `flag_*` tem um `score_*` correspondente:

```python
score_dividendo = len(matched_terms) / len(SIGNAL_TERMS["dividendo"])
# score ∈ [0.0, 1.0]
```

Quanto mais termos do sinal aparecem no artigo, maior o score de intensidade.

---

## Pipeline de Análise (NB05)

```
text_clean
     │
     ▼
tokenize_pt()
     │  NFD normalize + lowercase + regex [a-zà-ü]{3,}
     ▼
scores = [LEX[t] for t in tokens if t in LEX]
     │
     ├─► polarity_score = mean(scores) se len(scores) > 0 else 0.0
     ├─► n_pos_terms = count(s > 0 for s in scores)
     ├─► n_neg_terms = count(s < 0 for s in scores)
     │
     ▼
sentiment_label:
     │  score >= 0.15  → "positivo"
     │  score <= -0.15 → "negativo"
     │  else           → "neutro"
     │
     ▼
compute_signals():
     │  Para cada categoria, verifica tokens_set ∩ SIGNAL_TERMS[cat]
     ├─► flag_* (bool)
     └─► score_* (float [0.0, 1.0])
```

**Fallback TextBlob:**
Se `polarity_score == 0.0` (nenhum termo do léxico encontrado), TextBlob é aplicado como fallback com peso condicional.

---

## Implementação via Spark UDF (NB05)

O léxico é serializado inline dentro da UDF para compatibilidade com serialização Spark:

```python
@F.udf(returnType=SENTIMENT_SCHEMA)
def analyze_udf(text: str):
    # Léxico compacto embutido diretamente na UDF
    LEX = {"dividendo": +0.85, "vacancia": -0.75, ...}
    SIG = {"dividendo": ["dividendo", "yield", ...], ...}
    # ... lógica de análise
    return tuple(results)
```

---

## Validação e Distribuição Esperada

Para um corpus FII típico:

| Label | % Esperado | Justificativa |
|---|---|---|
| `neutro` | 45–55% | Maioria dos artigos é notícia factual sem tom forte |
| `positivo` | 25–35% | FIIs têm narrativa de dividendos e renda passiva |
| `negativo` | 15–25% | Cobertura de riscos e momentos de mercado adverso |

---

*Sentiment Methodology v1.0.0 · Investor Intelligence Platform FIIs Brasil*
