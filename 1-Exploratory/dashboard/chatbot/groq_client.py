
"""
dashboard/chatbot/groq_client.py
Groq AI client with mandatory financial disclaimer enforcement.
Humanistic AI: educational and analytical only. Never financial advisory.
"""

import os

DISCLAIMER = (
    "\n---\n"
    "⚠️ **AVISO IMPORTANTE**: Esta resposta possui caráter exclusivamente "
    "**educacional e analítico** e **não constitui recomendação de investimento**. "
    "Consulte um assessor financeiro qualificado antes de tomar decisões."
)

FORBIDDEN_ADVISORY_TERMS = [
    "recomendo comprar", "recomendo vender", "compre agora",
    "venda agora", "melhor investimento", "garanto retorno",
    "invista em", "compra de fii", "venda de fii",
]


def get_api_key() -> str:
    """Load GROQ_API_KEY_FII from st.secrets or environment. Never hardcoded."""
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY_FII"]
    except Exception:
        key = os.getenv("GROQ_API_KEY_FII", "")
        if not key:
            raise EnvironmentError(
                "GROQ_API_KEY_FII not configured. "
                "Add to .streamlit/secrets.toml or set as environment variable."
            )
        return key


def contains_advisory_language(text: str) -> bool:
    """Detect if model response contains forbidden advisory language."""
    t = text.lower()
    return any(term in t for term in FORBIDDEN_ADVISORY_TERMS)


def chat(user_message: str, context: str, model: str = "llama-3.1-8b-instant") -> str:
    """
    Send message to Groq. Appends DISCLAIMER to every response.
    Raises ValueError if response contains forbidden advisory language.
    """
    from groq import Groq
    client = Groq(api_key=get_api_key())

    system_prompt = (
        "Você é um assistente analítico especializado em Fundos de Investimento Imobiliário (FII) "
        "para fins EXCLUSIVAMENTE educacionais e analíticos.\n\n"
        "REGRAS ABSOLUTAS:\n"
        "- NUNCA recomende compra ou venda de FIIs\n"
        "- NUNCA forneça consultoria financeira\n"
        "- SEMPRE mantenha caráter educacional\n"
        "- Use apenas dados do contexto fornecido\n\n"
        f"CONTEXTO DOS DADOS:\n{context}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        max_tokens=500,
        temperature=0.7,
    )

    answer = response.choices[0].message.content

    if contains_advisory_language(answer):
        answer = (
            "[Resposta filtrada: conteúdo de consultoria detectado. "
            "Esta plataforma não oferece recomendações de investimento.]"
        )

    return answer + DISCLAIMER  # Disclaimer ALWAYS appended
