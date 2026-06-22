# 🚀 Deploy do Dashboard no Streamlit Community Cloud — Guia Passo a Passo

## Investor Intelligence Platform — FIIs Brasil 🇧🇷

> Pré-requisito: a API já deve estar publicada no Render (ver `DEPLOY_RENDER.md`).
> Você vai precisar da URL gerada (ex: `https://fii-intelligence-api.onrender.com`).

---

## ✅ Pré-requisitos

- [ ] Conta no [Streamlit Community Cloud](https://share.streamlit.io) (login via GitHub)
- [ ] **Repositório GitHub público** — o Streamlit Cloud exige isso no tier gratuito
- [ ] API já publicada no Render, com URL em mãos
- [ ] `dashboard/requirements.txt` presente (ao lado de `Home.py` — ver seção 1.1 abaixo)

---

## 🔧 Passo 1.1 — Sobre o `dashboard/requirements.txt`

> ⚠️ **Correção importante:** diferente do que uma versão anterior deste
> guia indicava, o Streamlit Community Cloud **não** usa sempre o
> `requirements.txt` da raiz. Ele procura primeiro um arquivo de
> dependências **na mesma pasta do entrypoint** (`dashboard/Home.py`) e só
> cai para a raiz se não encontrar nada ali — não existe campo na
> interface para apontar manualmente um arquivo customizado.
>
> Por isso, este projeto usa `dashboard/requirements.txt` (7 pacotes:
> streamlit, pandas, numpy, pyarrow, plotly, requests, python-dotenv) em
> vez do `requirements.txt` da raiz (~56 pacotes, incluindo PySpark/Torch,
> que o dashboard não usa em produção). Detalhes completos em
> [`docs/architecture/REQUIREMENTS_GUIA.md`](docs/architecture/REQUIREMENTS_GUIA.md).

```bash
git add dashboard/requirements.txt
git commit -m "chore: requirements leve para deploy do dashboard"
git push
```

---

## 🔧 Passo 2 — Atualizar o `Home.py`

Substitua `dashboard/Home.py` pela versão deste pacote (`dashboard/Home.py`).
A diferença principal: ela detecta automaticamente se deve consumir a API ou
ler Parquet local, via a variável `API_BASE_URL`:

```python
API_BASE_URL = (
    st.secrets.get("API_BASE_URL", "") if hasattr(st, "secrets") else ""
) or os.getenv("API_BASE_URL", "")
USE_API = bool(API_BASE_URL)
```

- **Se `API_BASE_URL` estiver vazia** → lê `data/gold/*.parquet` do próprio
  repositório (modo desenvolvimento/local).
- **Se `API_BASE_URL` estiver definida** → todas as chamadas de dados passam
  a ser HTTP GET/POST para a API no Render.

Isso significa que o **mesmo arquivo** funciona local e em produção — você não
precisa manter duas versões do dashboard.

---

## 🔧 Passo 3 — Commitar os arquivos necessários

```bash
git add dashboard/Home.py
git add dashboard/requirements.txt
git commit -m "feat: dashboard em modo híbrido (API + local fallback)"
git push
```

> ✅ Diferente do Render (que usa `requirements-api.txt` via `render.yaml`),
> o Streamlit Cloud detecta automaticamente o `dashboard/requirements.txt`
> por estar na mesma pasta do entrypoint `dashboard/Home.py` — não use o
> `requirements.txt` da raiz aqui, ele é pesado demais (PySpark, Torch,
> Selenium) para o que o dashboard realmente precisa. Ver
> [`docs/architecture/REQUIREMENTS_GUIA.md`](docs/architecture/REQUIREMENTS_GUIA.md)
> para o detalhamento completo.

---

## 🔧 Passo 4 — Criar o app no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Selecione o repositório, branch (`main`) e o arquivo principal:
   ```
   dashboard/Home.py
   ```
3. Em **Advanced settings** → **Python version**: `3.11`
4. **Antes de clicar em Deploy**, configure os Secrets (próximo passo)

---

## 🔧 Passo 5 — Configurar Secrets (URL da API)

No painel do app (mesmo antes do primeiro deploy, em **Advanced settings**,
ou depois em **Settings → Secrets**), adicione:

```toml
API_BASE_URL = "https://fii-intelligence-api.onrender.com"
```

Isso é equivalente a uma variável de ambiente, mas gerenciado pela interface do
Streamlit Cloud — nunca fica exposto no código ou no repositório público.

> 💡 **Testando localmente com a API real antes do deploy:**
> ```bash
> API_BASE_URL="https://fii-intelligence-api.onrender.com" streamlit run dashboard/Home.py
> ```

---

## ✅ Passo 6 — Deploy e Validação

1. Clique em **Deploy** — build leva ~2-5 minutos
2. Acesse a URL gerada (ex: `https://fii-intelligence.streamlit.app`)
3. Na sidebar, confirme o indicador de modo:
   - 🟢 **Modo: API em produção** → tudo certo, consumindo o Render
   - 🔴 **API indisponível** → revisar `API_BASE_URL` nos Secrets ou checar `/health` do Render
   - 🟡 **Modo: Parquet local** → `API_BASE_URL` não foi configurada (ou está vazia)

---

## 🔗 Passo 7 — Fechar o Ciclo de CORS

Volte ao Render e atualize a variável `ALLOWED_ORIGINS` (que estava em `*`)
para a URL real do Streamlit Cloud:

```
ALLOWED_ORIGINS=https://fii-intelligence.streamlit.app
```

Isso restringe quem pode chamar sua API — boa prática de segurança depois que
você já sabe qual é a origem legítima.

---

## ⚠️ Limitações do Tier Free — Streamlit Community Cloud

| Limitação | Impacto | Mitigação |
|---|---|---|
| **1 GB RAM** por app | Folga maior que o Render (512MB) — comporta bem o dashboard | Sem ação necessária |
| **Repositório público obrigatório** | Código (não os dados sensíveis — você não tem nenhum) fica visível | Aceitável neste projeto acadêmico |
| **App "dorme" após inatividade** | Primeiro acesso após um tempo demora alguns segundos para "religar" | Aceitável para demo/apresentação |
| **1 app privado gratuito, demais públicos** | Não é limitação real aqui, já que o repo já é público | — |

---

## 🩺 Troubleshooting Rápido

| Sintoma | Causa provável | Solução |
|---|---|---|
| Sidebar mostra 🔴 "API indisponível" | Render em cold start (spin-down) | Aguarde ~30-50s e recarregue a página |
| Erro `ModuleNotFoundError: requests` | `requests` ausente de `dashboard/requirements.txt` | Adicione `requests==2.34.2` em `dashboard/requirements.txt` (não na raiz) |
| Dashboard mostra dados desatualizados | Render serviu Gold antigo (commit antigo) | Ver seção de automação no `MANUAL_COMPLETO.md` |
| Erro de CORS no navegador (console) | `ALLOWED_ORIGINS` no Render não inclui a URL do Streamlit | Atualizar `ALLOWED_ORIGINS` no Render conforme Passo 6 |

---

## 🔜 Próximo Passo

Com API + Dashboard publicados e conectados, o próximo passo é a automação de
atualização — ver `MANUAL_COMPLETO.md`, seção **"Automação e Atualização em
Tempo Real"**.
