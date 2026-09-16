"""BYOK API request/response models. Deliberately do NOT nest
LLMCredentialRecord the way api/models_bugs.py nests BugReportRecord: that
record carries `encrypted_key`, which must never appear in a response.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from core.errors import BadRequestError
from repositories.interfaces import CredentialStatus, LLMCredentialRecord

# Gemini-only for now - the other three native providers remain fully
# supported in `build_provider` and can be re-enabled here later without a
# schema migration.
_SUPPORTED_PROVIDERS = {"gemini"}


class SaveLLMCredentialRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1)
    api_key: str = Field(min_length=1)
    model: Optional[str] = None

    def validate_provider(self) -> None:
        if self.provider not in _SUPPORTED_PROVIDERS:
            raise BadRequestError(
                f"Unsupported provider {self.provider!r}. "
                f"Supported: {', '.join(sorted(_SUPPORTED_PROVIDERS))}."
            )


class LLMCredentialResponse(BaseModel):
    provider: str
    model: Optional[str]
    key_hint: str
    status: CredentialStatus
    last_error: Optional[str]
    last_error_at: Optional[str]

    @classmethod
    def from_domain(cls, record: LLMCredentialRecord) -> "LLMCredentialResponse":
        return cls(
            provider=record.provider,
            model=record.model,
            key_hint=record.key_hint,
            status=record.status,
            last_error=record.last_error,
            last_error_at=record.last_error_at.isoformat() if record.last_error_at else None,
        )


class TestLLMCredentialRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Optional[str] = "gemini"
    api_key: Optional[str] = None
    model: Optional[str] = None

    def validate_provider(self) -> None:
        if self.provider and self.provider not in _SUPPORTED_PROVIDERS:
            raise BadRequestError(
                f"Unsupported provider {self.provider!r}. "
                f"Supported: {', '.join(sorted(_SUPPORTED_PROVIDERS))}."
            )


class TestLLMCredentialResponse(BaseModel):
    success: bool
    provider: str
    model: Optional[str] = None
    latency_ms: int
    message: str


__all__ = [
    "LLMCredentialResponse",
    "SaveLLMCredentialRequest",
    "TestLLMCredentialRequest",
    "TestLLMCredentialResponse",
]
