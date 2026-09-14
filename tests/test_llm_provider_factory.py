"""Tests for providers.llm.build_provider (BYOK) — a pure constructor over
the four existing native provider classes, distinct from get_llm_provider()
which resolves from the environment/ContextVar (see
tests/test_llm_context.py for that)."""
import pytest

from providers.llm import build_provider
from providers.llm.openai import OpenAIProvider
from providers.llm.gemini import GeminiProvider
from providers.llm.groq import GroqProvider
from providers.llm.nvidia_nim import NvidiaNimProvider


def test_build_provider_openai():
    provider = build_provider("openai", api_key="k", model="gpt-4o")
    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "gpt-4o"


def test_build_provider_gemini():
    provider = build_provider("gemini", api_key="k", model="gemini-flash-lite-latest")
    assert isinstance(provider, GeminiProvider)


def test_build_provider_groq():
    provider = build_provider("groq", api_key="k")
    assert isinstance(provider, GroqProvider)


def test_build_provider_nvidia_nim():
    provider = build_provider("nvidia_nim", api_key="k")
    assert isinstance(provider, NvidiaNimProvider)


def test_build_provider_uses_model_default_when_model_is_none():
    from config.settings import OPENAI_MODEL

    provider = build_provider("openai", api_key="k", model=None)
    assert provider.model == OPENAI_MODEL


def test_build_provider_unknown_name_raises_value_error():
    with pytest.raises(ValueError):
        build_provider("litellm-or-whatever", api_key="k")


def test_build_provider_reads_no_environment(monkeypatch):
    """A BYOK key must never fall back to a server-side env var key -
    that would defeat the entire feature."""
    monkeypatch.setenv("OPENAI_API_KEY", "server-side-key-must-not-be-used")
    provider = build_provider("openai", api_key="user-supplied-key")
    assert provider.api_key == "user-supplied-key"


from providers.llm import get_llm_provider
from providers.llm.mock import MockLLMProvider


def test_get_llm_provider_uses_context_var_when_set(monkeypatch):
    from core.llm_context import reset_context_provider, set_context_provider

    monkeypatch.setattr("providers.llm.LLM_PROVIDER", "mock")
    stub = build_provider("groq", api_key="k")
    token = set_context_provider(stub)
    try:
        assert get_llm_provider() is stub
    finally:
        reset_context_provider(token)


def test_get_llm_provider_falls_back_to_env_when_context_unset(monkeypatch):
    monkeypatch.setattr("providers.llm.LLM_PROVIDER", "mock")
    provider = get_llm_provider()
    assert isinstance(provider, MockLLMProvider)
