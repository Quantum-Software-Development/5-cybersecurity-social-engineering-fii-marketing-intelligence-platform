# LGPD — Alinhamento e Conformidade
## Investor Intelligence Platform — FIIs Brasil 🇧🇷

**Lei nº 13.709, de 14 de agosto de 2018 — Lei Geral de Proteção de Dados Pessoais**

---

## Resumo Executivo

| Item | Status |
|---|---|
| Coleta de dados pessoais identificáveis | ❌ Não realizada |
| Profiling individual de investidores | ❌ Não realizado |
| Dados de crianças ou adolescentes | ❌ Não coletados |
| Dados sensíveis (Art. 5º, II, LGPD) | ❌ Não coletados |
| Base legal documentada | ✅ Interesse legítimo (Art. 7º, VI) |
| Minimização de dados | ✅ Implementada |
| Transparência de origem | ✅ Implementada via `source`, `ingestion_method` |
| Direito de exclusão | ✅ Viável via remoção do corpus |

---

## Base Legal (Art. 7º, LGPD)

**Base aplicável:** Art. 7º, VI — *Interesse legítimo do controlador ou de terceiro*

**Justificativa:**
O projeto processa exclusivamente conteúdo editorial e comunitário **públicamente disponível** sobre Fundos de Investimento Imobiliário (FIIs), para fins de:
- Análise de mercado acadêmica
- Inteligência de marketing em mercados financeiros
- Pesquisa e desenvolvimento metodológico em Big Data e NLP

O processamento não afeta negativamente os interesses ou direitos dos titulares dos dados mencionados nos conteúdos coletados.

---

## Tipos de Dados Tratados

### Dados tratados — Não são dados pessoais (Art. 5º, I, LGPD)

| Dado | Natureza | Justificativa de não ser dado pessoal |
|---|---|---|
| Títulos e texto de artigos | Conteúdo editorial público | Produzido para publicação pública |
| URLs de artigos | Endereços de páginas públicas | Identificam conteúdo, não pessoas |
| Nomes de portais (`source`) | Identificadores organizacionais | Dados de pessoa jurídica, não física |
| Tags e categorias | Metadados editoriais | Não identificam indivíduos |
| Timestamps de publicação | Metadados temporais públicos | Disponíveis publicamente no feed |

### Dados tratados — Metadados editoriais públicos

| Dado | Campo | Natureza |
|---|---|---|
| Nome do autor de artigo | `author` | Metadado editorial publicado voluntariamente |
| Username Reddit | `author` (Reddit) | Identificador público voluntariamente escolhido pelo usuário |

**Tratamento aplicado a dados de autores:**
- Armazenados como metadados de proveniência editorial
- Não são usados para profiling, scoring individual ou rastreamento
- Não são combinados com outras fontes para identificação adicional
- Nullable em todos os schemas — não são obrigatórios para o pipeline

---

## Dados Não Coletados

| Categoria | Motivo |
|---|---|
| CPF, RG, passaporte | Irrelevante para análise editorial de FIIs |
| Dados financeiros pessoais | Não coletados de APIs de corretoras ou Open Finance |
| Localização geográfica pessoal | Não relevante — análise de conteúdo |
| Dados de saúde ou biométricos | Fora do escopo |
| Dados de crianças | Fora do escopo |
| Histórico de navegação | Não há rastreamento de usuários |
| Dados de redes sociais (além de posts públicos Reddit) | Sem coleta de DMs, conexões, histórico privado |

---

## Princípios LGPD Atendidos (Art. 6º)

| Princípio | Como é atendido |
|---|---|
| **Finalidade (I)** | Análise de conteúdo editorial FII para pesquisa e marketing intelligence |
| **Adequação (II)** | Dados coletados são compatíveis com a finalidade declarada |
| **Necessidade (III)** | Apenas campos necessários para análise textual e proveniência |
| **Livre acesso (IV)** | N/A — sem titulares identificados no pipeline |
| **Qualidade dos dados (V)** | Quality gates em NB02 garantem dados limpos e normalizados |
| **Transparência (VI)** | Fontes documentadas publicamente neste repositório |
| **Segurança (VII)** | Credenciais via `.env` — não commitadas. Parquet local não exposto. |
| **Prevenção (VIII)** | Sem coleta de dados sensíveis. Sem profiling. |
| **Não discriminação (IX)** | Análise de conteúdo — sem scoring individual |
| **Responsabilização (X)** | Documentação completa. Autores identificados. |

---

## Reddit — Considerações Específicas

Os dados do Reddit são coletados via:
1. **API pública oficial** (`reddit.com/r/subreddit/new.json`) — dados públicos, sem autenticação
2. **PRAW** — API oficial Reddit com credenciais próprias da aplicação

**Termos de Serviço Reddit:** A coleta respeita os [Reddit API Terms](https://www.redditinc.com/policies/data-api-terms):
- `User-Agent` identificado: `FIIIntelligencePlatform/1.0 (academic; PUC-SP FACEI)`
- Rate limiting respeitado (2s entre requests)
- Sem coleta de dados privados

**Dados Reddit coletados:**
- Posts públicos de subreddits públicos (`r/investimentos`, `r/farialimabets`)
- Apenas posts relevantes para FIIs (filtro `FII_FILTER_TERMS`)
- Username como metadado editorial (não para identificação)

---

## Direitos dos Titulares

Para qualquer nome de autor eventualmente presente nos datasets:

| Direito (Art. 18, LGPD) | Como exercer |
|---|---|
| Confirmação de tratamento | Verificar schema Bronze campo `author` |
| Acesso | Os dados são os próprios artigos públicos |
| Correção | Não aplicável — dados espelham publicação original |
| Eliminação | Remover o `article_id` correspondente de `data/external/` e reprocessar |
| Portabilidade | Dados em Parquet — formato aberto e portável |
| Oposição | Contato: fabicampanari@proton.me |

---

## Retenção de Dados

| Dataset | Retenção | Justificativa |
|---|---|---|
| `data/external/` (Bronze) | Duração do projeto acadêmico | Reprodutibilidade de resultados |
| `data/silver/` | Duração do projeto | Análise acadêmica |
| `data/gold/` | Duração do projeto | Entrega acadêmica |
| Logs (`logs/`) | Rotação diária (filename com data) | Debug e auditoria técnica |

---

## Contato do Controlador (Contexto Acadêmico)

| Campo | Informação |
|---|---|
| Projeto | Investor Intelligence Platform — FIIs Brasil |
| Instituição | PUC-SP FACEI |
| Responsáveis | Fabiana Campanari · Pedro Vyctor Almeida |
| Contato | fabicampanari@proton.me |

---

*LGPD Alignment v1.0.0 · Investor Intelligence Platform FIIs Brasil*
