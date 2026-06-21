"""
llm_client.py
Unified LLM client supporting OpenAI GPT-4o and Google Gemini.
Reads provider choice from .env or Streamlit secrets.
"""
import os
import streamlit as st

# ── Provider detection ────────────────────────────────────────────────────────

def _get_env(key: str) -> str | None:
    """Check st.secrets first, then os.environ."""
    try:
        return st.secrets.get(key)
    except Exception:
        pass
    return os.getenv(key)


def get_available_providers() -> list[str]:
    providers = []
    if _get_env("OPENAI_API_KEY"):
        providers.append("openai")
    if _get_env("GEMINI_API_KEY"):
        providers.append("gemini")
    return providers


# ── OpenAI ────────────────────────────────────────────────────────────────────

def _call_openai(prompt: str, system: str = "") -> str:
    from openai import OpenAI
    client = OpenAI(api_key=_get_env("OPENAI_API_KEY"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


# ── Gemini ────────────────────────────────────────────────────────────────────

def _call_gemini(prompt: str, system: str = "") -> str:
    import google.generativeai as genai
    genai.configure(api_key=_get_env("GEMINI_API_KEY"))
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system if system else None,
    )
    response = model.generate_content(prompt)
    return response.text.strip()


# ── Public API ────────────────────────────────────────────────────────────────

def call_llm(prompt: str, system: str = "", provider: str = "gemini") -> str:
    """
    Call LLM with a prompt.
    provider: "openai" | "gemini"
    Falls back gracefully if a key is missing.
    """
    if provider == "openai":
        if not _get_env("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set. Add it to .env or Streamlit secrets.")
        return _call_openai(prompt, system)
    elif provider == "gemini":
        if not _get_env("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not set. Add it to .env or Streamlit secrets.")
        return _call_gemini(prompt, system)
    else:
        raise ValueError(f"Unknown provider: {provider}")
