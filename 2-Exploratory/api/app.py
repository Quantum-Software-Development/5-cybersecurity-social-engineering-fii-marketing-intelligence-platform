"""
api/app.py — FastAPI REST API (Production)
Investor Intelligence Platform — FIIs Brasil 🇧🇷

Local:  uvicorn api.app:app --reload --port 8000
Render: uvicorn api.app:app --host 0.0.0.0 --port $PORT
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────────────────────────────────────
# Logging (Render captures stdout — sem necessidade de arquivo de log aqui)
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("fii_api")

# ─────────────────────────────────────────────────────────────────────────────
# Feature flags — controlam custo de memória em ambientes restritos (Render free)
# ─────────────────────────────────────────────────────────────────────────────
# ENABLE_SEMANTIC_SEARCH=false evita carregar sentence-transformers + faiss-cpu
# (torch CPU sozinho consome ~300-700MB) — recomendado no tier free (512MB RAM).
# Em ambientes com mais memória (Render Starter+, execução local), defina =true.
ENABLE_SEMANTIC_SEARCH = os.getenv("ENABLE_SEMANTIC_SEARCH", "false").lower() == "true"

# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FII Market Intelligence API",
    description=(
        "Plataforma de inteligência de mercado FIIs — 21 fontes monitoradas.\n"
        "Pipeline: MapReduce + TF-IDF + BM25"
        + (" + FAISS" if ENABLE_SEMANTIC_SEARCH else "")
        + " + Sentimento FII PT-BR.\n\n"
        "⚠️ Não constitui recomendação de investimento."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS — necessário para o dashboard Streamlit Cloud (origem diferente) chamar
# esta API. Em produção, restrinja ALLOWED_ORIGINS via variável de ambiente.
# ─────────────────────────────────────────────────────────────────────────────
_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",")] if _origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
GOLD = ROOT / "data" / "gold"


def _load(sub: str, fname: str) -> pd.DataFrame:
    p = GOLD / sub / fname
    if not p.exists():
        raise HTTPException(
            404,
            f"Dataset não encontrado: {p.name}. "
            "Verifique se os artefatos Gold foram commitados ao repositório "
            "(ver seção 'Deploy' do README).",
        )
    return pd.read_parquet(p)


# ─────────────────────────────────────────────────────────────────────────────
# Startup — valida ambiente uma vez, loga estado (não bloqueia se faltar dado)
# ─────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    logger.info(f"FII Intelligence API iniciando | semantic_search={ENABLE_SEMANTIC_SEARCH}")
    logger.info(f"GOLD_DIR={GOLD} exists={GOLD.exists()}")
    if not (GOLD / "dashboard" / "dashboard_articles.parquet").exists():
        logger.warning(
            "dashboard_articles.parquet não encontrado — "
            "/articles e /summary retornarão 404 até os dados serem disponibilizados."
        )
    if not os.getenv("GROQ_API_KEY"):
        logger.warning("GROQ_API_KEY não configurada — /query funcionará em modo demo.")


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    """Health check — usado por Render para liveness probe e pelo dashboard
    para exibir qual motor de busca está ativo."""
    _articles_path = GOLD / "dashboard" / "dashboard_articles.parquet"
    _faiss_path = GOLD / "tfidf_bm25" / "faiss_index.faiss"
    return {
        "status": "ok",
        "version": "1.0.0",
        "docs": "/docs",
        "semantic_search_enabled": ENABLE_SEMANTIC_SEARCH,
        "faiss_index_present": _faiss_path.exists(),
        "data_available": _articles_path.exists(),
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
    }


@app.get("/articles")
def articles(
    limit: int = Query(20, ge=1, le=500),
    sentiment: Optional[str] = Query(None, pattern="^(positivo|neutro|negativo)$"),
    source: Optional[str] = None,
):
    df = _load("dashboard", "dashboard_articles.parquet")
    if sentiment:
        df = df[df["sentiment_label"] == sentiment]
    if source:
        df = df[df["source"].str.contains(source, case=False, na=False)]
    return df.head(limit).fillna("").to_dict(orient="records")


@app.get("/fii/{ticker}")
def fii_signals(ticker: str):
    df = _load("dashboard", "dashboard_fii_signals.parquet")
    result = df[df["ticker"] == ticker.upper()]
    if result.empty:
        raise HTTPException(404, f"FII {ticker.upper()} não encontrado no catálogo.")
    return result.fillna(0).to_dict(orient="records")


@app.get("/sources")
def sources():
    df = _load("dashboard", "dashboard_source_stats.parquet")
    return df.fillna("").to_dict(orient="records")


@app.post("/query")
async def query_rag(question: str = Query(..., min_length=5)):
    """
    Consulta RAG: Recuperação (TF-IDF + BM25, + FAISS se ENABLE_SEMANTIC_SEARCH)
    → Geração (Groq llama-3.1-8b-instant). Disclaimer legal sempre incluído.
    """
    try:
        import sys
        sys.path.insert(0, str(ROOT))
        from dashboard.chatbot.groq_client import chat, retrieve_context

        context_docs = retrieve_context(question, k=5)
        answer = chat(question, context="\n".join(context_docs))
        return {"question": question, "context_docs": context_docs, "answer": answer}
    except FileNotFoundError as e:
        raise HTTPException(
            503,
            f"Índices de busca não disponíveis: {e}. "
            "Execute NB04 e garanta que data/gold/tfidf_bm25/ foi commitado.",
        )
    except Exception as e:
        logger.exception("Erro no pipeline RAG")
        raise HTTPException(500, f"Erro no pipeline RAG: {e}")


@app.get("/summary")
def summary():
    p = GOLD / "dashboard" / "api_payload_summary.json"
    if not p.exists():
        raise HTTPException(404, "api_payload_summary.json não encontrado. Execute NB07.")
    data = json.loads(p.read_text())
    data["api_semantic_search_enabled"] = ENABLE_SEMANTIC_SEARCH
    return data


# ─────────────────────────────────────────────────────────────────────────────
# Local dev entrypoint — Render usa o startCommand do render.yaml, não isto.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.app:app", host="0.0.0.0", port=port, reload=True)
