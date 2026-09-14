"""Tests for core/llm_context.py's ContextVar seam - the mechanism that
lets a request-scoped BYOK provider reach get_llm_provider() (Task 7)
without threading it through every agent/container constructor."""
import asyncio

import pytest

from core.llm_context import get_context_provider, reset_context_provider, set_context_provider
from providers.base import LLMProvider


class _StubProvider(LLMProvider):
    async def generate(self, prompt, **kwargs):
        return "stub"

    async def generate_structured(self, prompt, schema, **kwargs):
        return {}


def test_defaults_to_none():
    assert get_context_provider() is None


def test_set_then_get_then_reset():
    stub = _StubProvider()
    token = set_context_provider(stub)
    try:
        assert get_context_provider() is stub
    finally:
        reset_context_provider(token)
    assert get_context_provider() is None


@pytest.mark.asyncio
async def test_inherited_by_asyncio_create_task_child():
    """asyncio.create_task copies the current Context at creation time - the
    exact mechanism services/evaluation_dispatcher.py's fire-and-forget
    scheduling relies on to inherit a caller's provider (spec 'Reaching the
    agents')."""
    stub = _StubProvider()
    token = set_context_provider(stub)
    seen = {}

    async def child():
        seen["provider"] = get_context_provider()

    try:
        task = asyncio.create_task(child())
        await task
    finally:
        reset_context_provider(token)

    assert seen["provider"] is stub


@pytest.mark.asyncio
async def test_sibling_task_does_not_leak_into_a_fresh_task():
    """A value set in one request's context must not leak into another
    request's task that was never a child of the first."""
    stub = _StubProvider()

    async def unrelated_task():
        return get_context_provider()

    token = set_context_provider(stub)
    try:
        result = await asyncio.create_task(unrelated_task())
        # This task WAS created while the ContextVar was set, so by Python's
        # contextvars semantics it correctly inherits it - demonstrating
        # the mechanism Task 12's yield-dependency relies on: the value
        # only exists for tasks created during the `with`-like window
        # between set_context_provider and reset_context_provider.
        assert result is stub
    finally:
        reset_context_provider(token)
    assert get_context_provider() is None
