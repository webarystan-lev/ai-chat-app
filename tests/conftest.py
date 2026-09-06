"""
🏛️ Shekinah AI Portal — Fixtures & Test Setup
Общие фикстуры и изоляция окружения для тестирования компонентов Цитадели.
"""

import os
import pytest

@pytest.fixture
def test_passphrase() -> str:
    """Фикстура тестовой парольной фразы Цитадели."""
    return "shekinah_citadel_sacred_passphrase_2026"

@pytest.fixture
def test_secret_data() -> str:
    """Фикстура секретных данных для тестирования шифрования."""
    return "AIzaSyCitadelPortalTestSecretPayload123456789"

@pytest.fixture
def isolated_env(monkeypatch):
    """Изолированное окружение для предотвращения обращения к боевым сервисам."""
    monkeypatch.setenv("CONVEX_URL", "https://test-citadel.convex.cloud")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_api_key_valid_12345")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_api_key_12345")
    monkeypatch.setenv("MISTRAL_API_KEY", "test_mistral_api_key_12345")
    yield monkeypatch
