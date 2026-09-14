"""Tests that BYOK_ENCRYPTION_KEY is read into AppSettings and that
build_default_container always wires an llm_credential_repository (BYOK
being 'off' means the value is never read, not that the repository is
missing - see core/llm_context.py's own check of the setting)."""
from core.config import AppSettings
from core.container import build_default_container
from repositories.interfaces import LLMCredentialRepository


def test_byok_encryption_key_defaults_to_none(monkeypatch):
    monkeypatch.delenv("BYOK_ENCRYPTION_KEY", raising=False)
    settings = AppSettings.from_env()
    assert settings.byok_encryption_key is None


def test_byok_encryption_key_reads_env(monkeypatch):
    monkeypatch.setenv("BYOK_ENCRYPTION_KEY", "some-fernet-key")
    settings = AppSettings.from_env()
    assert settings.byok_encryption_key == "some-fernet-key"


def test_container_always_has_llm_credential_repository_in_memory_mode():
    settings = AppSettings(database_url="")
    container = build_default_container(settings)
    assert isinstance(container.llm_credential_repository, LLMCredentialRepository)
