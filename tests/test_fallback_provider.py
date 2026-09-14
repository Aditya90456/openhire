"""Tests for FallbackLLMProvider — wraps a user's BYOK provider so a bad or
rate-limited key falls back to the system key for THAT call, and reports
the failure via a callback (which Task 11 uses to mark the credential
status='failed'), while any other transient error still propagates so
BaseAgent's existing retry logic (agents/base.py) handles it unchanged."""
from unittest.mock import AsyncMock

import pytest

from providers.base import LLMPermanentError, LLMProvider, LLMTransientError
from providers.llm.fallback import FallbackLLMProvider


class _StaticProvider(LLMProvider):
    def __init__(self, *, result=None, error=None):
        self._result = result
        self._error = error

    async def generate(self, prompt, **kwargs):
        if self._error:
            raise self._error
        return self._result

    async def generate_structured(self, prompt, schema, **kwargs):
        if self._error:
            raise self._error
        return self._result


@pytest.mark.asyncio
async def test_uses_primary_when_it_succeeds():
    primary = _StaticProvider(result="from primary")
    secondary = _StaticProvider(result="from secondary")
    on_failure = AsyncMock()
    provider = FallbackLLMProvider(primary, secondary, on_failure)

    result = await provider.generate("hi")
    assert result == "from primary"
    on_failure.assert_not_called()


@pytest.mark.asyncio
async def test_permanent_error_falls_back_and_reports():
    error = LLMPermanentError("bad key")
    primary = _StaticProvider(error=error)
    secondary = _StaticProvider(result="from secondary")
    on_failure = AsyncMock()
    provider = FallbackLLMProvider(primary, secondary, on_failure)

    result = await provider.generate("hi")
    assert result == "from secondary"
    on_failure.assert_called_once_with(error)


@pytest.mark.asyncio
async def test_rate_limit_transient_error_falls_back_and_reports():
    error = LLMTransientError("rate limited")
    primary = _StaticProvider(error=error)
    secondary = _StaticProvider(result="from secondary")
    on_failure = AsyncMock()
    provider = FallbackLLMProvider(primary, secondary, on_failure)

    result = await provider.generate("hi")
    assert result == "from secondary"
    on_failure.assert_called_once_with(error)


@pytest.mark.asyncio
async def test_generate_structured_also_falls_back():
    error = LLMPermanentError("bad key")
    primary = _StaticProvider(error=error)
    secondary = _StaticProvider(result={"ok": True})
    on_failure = AsyncMock()
    provider = FallbackLLMProvider(primary, secondary, on_failure)

    result = await provider.generate_structured("hi", schema={})
    assert result == {"ok": True}
    on_failure.assert_called_once_with(error)
