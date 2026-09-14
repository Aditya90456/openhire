"""FallbackLLMProvider — wraps a BYOK provider so a failing user key falls
back to the system key for that one call, rather than surfacing a
recruiter's billing problem to a candidate mid-interview (spec 'Decisions
taken' #4).

Deliberately does NOT catch every exception: an ordinary transient error
(a momentary rate limit that isn't attributable to a bad key specifically,
a timeout, a 5xx) still propagates unchanged so BaseAgent's existing retry
logic (agents/base.py) handles it exactly as it does for the system-key
path today. Only LLMPermanentError (revoked/malformed key) and
LLMTransientError (treated here as "this key/account is rate-limited")
trigger the fallback - see services/llm_credential_service.py for how
`on_primary_failure` marks the credential status='failed'.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from providers.base import LLMPermanentError, LLMProvider, LLMTransientError


class FallbackLLMProvider(LLMProvider):
    """Delegates to `primary`; on LLMPermanentError or LLMTransientError,
    completes the call on `secondary` and awaits `on_primary_failure(exc)`."""

    def __init__(
        self,
        primary: LLMProvider,
        secondary: LLMProvider,
        on_primary_failure: Callable[[Exception], Awaitable[None]],
    ) -> None:
        self._primary = primary
        self._secondary = secondary
        self._on_primary_failure = on_primary_failure

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            return await self._primary.generate(prompt, **kwargs)
        except (LLMPermanentError, LLMTransientError) as e:
            await self._on_primary_failure(e)
            return await self._secondary.generate(prompt, **kwargs)

    async def generate_structured(
        self, prompt: str, schema: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        try:
            return await self._primary.generate_structured(prompt, schema, **kwargs)
        except (LLMPermanentError, LLMTransientError) as e:
            await self._on_primary_failure(e)
            return await self._secondary.generate_structured(prompt, schema, **kwargs)
