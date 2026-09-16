"""BYOK endpoints: GET/PUT/DELETE /auth/me/llm-credential.

Mounted at /auth/me (not a separate /llm-credentials prefix) to sit
alongside the existing GET/PATCH /auth/me and POST /auth/me/password -
all three are "manage my own account" actions (api/routes/auth.py).

Gated on settings.byok_encryption_key being set: with BYOK off, every
endpoint here returns 404 as if it does not exist, rather than a 500 from
get_llm_credential_service's defensive ValueError - the profile page never
calls these endpoints while BYOK is off (Task 14), and an operator probing
the API sees the same "not found" a disabled feature should show.
"""
from typing import Optional

from fastapi import APIRouter, Body, Depends, Response

from api.models_llm_credentials import (
    LLMCredentialResponse,
    SaveLLMCredentialRequest,
    TestLLMCredentialRequest,
    TestLLMCredentialResponse,
)
from core.config import AppSettings, get_settings
from core.dependencies import get_llm_credential_service
from core.errors import NotFoundError
from core.security import Principal, require_authenticated
from services.llm_credential_service import LLMCredentialService

router = APIRouter(prefix="/auth/me", tags=["byok"])


def _require_byok_enabled(settings: AppSettings = Depends(get_settings)) -> None:
    if not settings.byok_encryption_key:
        raise NotFoundError("BYOK is not enabled on this deployment.")


@router.get("/llm-credential", response_model=None, dependencies=[Depends(_require_byok_enabled)])
async def get_llm_credential(
    service: LLMCredentialService = Depends(get_llm_credential_service),
    principal: Principal = Depends(require_authenticated),
):
    """GET /auth/me/llm-credential. 204 (no body) when none is saved -
    never a 404, since "no credential saved" is the normal, expected state
    for most users, not an error."""
    record = await service.get(principal.subject_id)
    if record is None:
        return Response(status_code=204)
    return LLMCredentialResponse.from_domain(record)


@router.put("/llm-credential", response_model=LLMCredentialResponse, dependencies=[Depends(_require_byok_enabled)])
async def save_llm_credential(
    payload: SaveLLMCredentialRequest,
    service: LLMCredentialService = Depends(get_llm_credential_service),
    principal: Principal = Depends(require_authenticated),
) -> LLMCredentialResponse:
    """PUT /auth/me/llm-credential. Validates the key with one live call
    before persisting (400 on failure, writes nothing - see
    services/llm_credential_service.py:LLMCredentialService.save)."""
    payload.validate_provider()
    record = await service.save(
        user_id=principal.subject_id,
        provider=payload.provider,
        api_key=payload.api_key,
        model=payload.model,
    )
    return LLMCredentialResponse.from_domain(record)


@router.delete("/llm-credential", status_code=204, dependencies=[Depends(_require_byok_enabled)])
async def delete_llm_credential(
    service: LLMCredentialService = Depends(get_llm_credential_service),
    principal: Principal = Depends(require_authenticated),
) -> None:
    """DELETE /auth/me/llm-credential. Idempotent - removing an already-absent
    credential still returns 204."""
    await service.delete(principal.subject_id)


@router.post("/llm-credential/test", response_model=TestLLMCredentialResponse, dependencies=[Depends(_require_byok_enabled)])
async def test_llm_credential(
    payload: Optional[TestLLMCredentialRequest] = Body(None),
    service: LLMCredentialService = Depends(get_llm_credential_service),
    principal: Principal = Depends(require_authenticated),
) -> TestLLMCredentialResponse:
    """POST /auth/me/llm-credential/test. Tests an entered API key in place
    without saving, or tests the user's currently saved credential if no key
    is provided in the payload."""
    if payload and payload.api_key and payload.api_key.strip():
        payload.validate_provider()
        res = await service.test_key(
            provider=payload.provider or "gemini",
            api_key=payload.api_key.strip(),
            model=payload.model,
        )
        return TestLLMCredentialResponse(**res)

    res = await service.test_saved(
        user_id=principal.subject_id,
        model=payload.model if payload else None,
    )
    return TestLLMCredentialResponse(**res)
