"""
LLM provider factory and implementations.
"""
from typing import Optional

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    NVIDIA_NIM_API_KEY,
    NVIDIA_NIM_BASE_URL,
    NVIDIA_NIM_ENABLE_THINKING,
    NVIDIA_NIM_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from core.llm_context import get_context_provider
from providers.base import LLMProvider
from providers.llm.gemini import GeminiProvider
from providers.llm.groq import GroqProvider
from providers.llm.mock import MockLLMProvider
from providers.llm.nvidia_nim import NvidiaNimProvider
from providers.llm.openai import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    """Factory function to get LLM provider.

    Resolves in this order:
    1. A request-scoped BYOK provider set via core/llm_context.py's
       ContextVar (set by a FastAPI dependency on recruiter-authenticated
       routes - see api/dependencies for `apply_llm_context_for_recruiter`).
    2. The existing environment-variable dispatch below, unchanged - this
       is the ENTIRE fallback path main.py (the CLI) and every test that
       does not touch the ContextVar always takes.
    """
    context_provider = get_context_provider()
    if context_provider is not None:
        return context_provider

    # NVIDIA NIM is the primary provider (Nemotron; super-120b by default -
    # fastest and widest of the family, reasoning mode off. See
    # config/settings.py for the benchmark table behind that choice).
    # Groq, OpenAI, and Gemini remain fully supported alternatives.
    if LLM_PROVIDER == "nvidia_nim" or LLM_PROVIDER == "nvidia-nim":
        if not NVIDIA_NIM_API_KEY:
            raise ValueError(
                "NVIDIA_NIM_API_KEY environment variable is required for NVIDIA NIM provider"
            )
        return NvidiaNimProvider(
            api_key=NVIDIA_NIM_API_KEY,
            model=NVIDIA_NIM_MODEL,
            base_url=NVIDIA_NIM_BASE_URL,
            enable_thinking=NVIDIA_NIM_ENABLE_THINKING,
        )
    elif LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY environment variable is required for Groq provider"
            )
        return GroqProvider(api_key=GROQ_API_KEY, model=GROQ_MODEL)
    elif LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for OpenAI provider"
            )
        return OpenAIProvider(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
    elif LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required for Gemini provider"
            )
        return GeminiProvider(api_key=GEMINI_API_KEY, model=GEMINI_MODEL)
    elif LLM_PROVIDER == "mock":
        return MockLLMProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")


def build_provider(name: str, api_key: str, model: Optional[str] = None) -> LLMProvider:
    """Construct a provider from explicit values. Reads no environment
    except each provider's own model-default constant when `model` is
    omitted - the key and provider name always come from the caller
    (BYOK), never from OPENAI_API_KEY/GROQ_API_KEY/etc.

    Returns the SAME four classes get_llm_provider() already uses, so a
    BYOK-driven agent gets identical error classification and
    structured-output handling to the system-key path - no parallel client.
    """
    if name == "openai":
        return OpenAIProvider(api_key=api_key, model=model or OPENAI_MODEL)
    if name == "gemini":
        return GeminiProvider(api_key=api_key, model=model or GEMINI_MODEL)
    if name == "groq":
        return GroqProvider(api_key=api_key, model=model or GROQ_MODEL)
    if name == "nvidia_nim":
        return NvidiaNimProvider(
            api_key=api_key,
            model=model or NVIDIA_NIM_MODEL,
            base_url=NVIDIA_NIM_BASE_URL,
            enable_thinking=NVIDIA_NIM_ENABLE_THINKING,
        )
    raise ValueError(
        f"Unknown BYOK provider: {name!r}. Supported: openai, gemini, groq, nvidia_nim."
    )


__all__ = [
    "get_llm_provider",
    "build_provider",
    "LLMProvider",
    "MockLLMProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "GroqProvider",
    "NvidiaNimProvider",
]
