"""
🏛️ Shekinah AI Portal — Тесты Двухступенчатого Стража Врат («Ключ Премудрости»)
Проверка логики безопасной аутентификации, извлечения секретов get_secret и изоляции внешних вызовов.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from providers.security import get_secret


def authenticate_gatekeeper(entered_key: str, master_key: str, verify_fn) -> tuple[bool, str]:
    """
    Чистая функция, реализующая каноническую двухступенчатую логику Стража Врат из app.py:
    1. Ступень I: Проверка на непустоту, наличие серверного эталона и строгая идентичность ключей.
    2. Ступень II: Только при успешной Ступени I — вызов verify_fn.
    """
    clean_key = entered_key.strip() if entered_key else ""
    if not clean_key:
        return False, "🔴 Врата затворены: введите ключ доступа."
    
    if not master_key or not master_key.strip():
        return False, "⚠️ Внутренняя ошибка: мастер-шифр сервера не сконфигурирован."
    
    if clean_key != master_key.strip():
        return False, "🔴 Доступ запрещён: шифр не признан Стражем Врат Цитадели."
    
    valid, msg = verify_fn(clean_key)
    if valid:
        return True, "✅ Врата распахнуты. Доступ Создателя подтверждён!"
    else:
        return False, "🔴 Ключ признан истинным, однако шлюз Цитадели временно недоступен."


class TestSecretRetrieval(unittest.TestCase):
    """Тестирование функции get_secret."""

    def test_get_secret_from_env(self):
        """Проверка извлечения секрета из os.environ."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaSy_Secret_Env_123"}):
            self.assertEqual(get_secret("GEMINI_API_KEY"), "AIzaSy_Secret_Env_123")

    def test_get_secret_priority_env_over_secrets(self):
        """Проверка приоритета os.environ над st.secrets."""
        mock_st = MagicMock()
        mock_st.secrets = {"GEMINI_API_KEY": "from_secrets"}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "from_env"}):
            with patch.dict("sys.modules", {"streamlit": mock_st}):
                self.assertEqual(get_secret("GEMINI_API_KEY"), "from_env")

    def test_get_secret_fallback_to_secrets(self):
        """Проверка отката на st.secrets при отсутствии в os.environ."""
        mock_st = MagicMock()
        mock_st.secrets = {"GEMINI_API_KEY": "from_cloud_secrets"}
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict("sys.modules", {"streamlit": mock_st}):
                self.assertEqual(get_secret("GEMINI_API_KEY"), "from_cloud_secrets")

    def test_get_secret_missing(self):
        """Проверка возврата пустой строки при отсутствии секрета."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_secret("NON_EXISTENT_KEY_999"), "")


class TestTwoStageGatekeeper(unittest.TestCase):
    """Тестирование двухступенчатой защиты Стража Врат."""

    def setUp(self):
        self.master_key = "AIzaSy_MasterKey_Shekinah_2026"
        self.mock_verify_fn = MagicMock()

    def test_empty_entered_key(self):
        """Проверка отклонения пустого ввода ключа."""
        success, msg = authenticate_gatekeeper("", self.master_key, self.mock_verify_fn)
        self.assertFalse(success)
        self.assertIn("Врата затворены", msg)
        self.mock_verify_fn.assert_not_called()

        success, msg = authenticate_gatekeeper("   ", self.master_key, self.mock_verify_fn)
        self.assertFalse(success)
        self.mock_verify_fn.assert_not_called()

    def test_unconfigured_server_master_key(self):
        """Проверка обработки ситуации, когда на сервере не задан мастер-ключ."""
        success, msg = authenticate_gatekeeper("some_key", "", self.mock_verify_fn)
        self.assertFalse(success)
        self.assertIn("мастер-шифр сервера не сконфигурирован", msg)
        self.mock_verify_fn.assert_not_called()

    def test_stage_1_mismatch_blocks_without_api_call(self):
        """
        Ключевой тест безопасности: при вводе неверного ключа («чужой пассажир»)
        система НЕМЕДЛЕННО блокирует вход и НЕ производит вызовов к внешнему API.
        """
        alien_key = "AIzaSy_Alien_Passenger_Key_999"
        success, msg = authenticate_gatekeeper(alien_key, self.master_key, self.mock_verify_fn)
        self.assertFalse(success)
        self.assertIn("Доступ запрещён: шифр не признан", msg)
        # Внешний шлюз категорически не должен вызываться!
        self.mock_verify_fn.assert_not_called()

    def test_stage_1_match_proceeds_to_stage_2_success(self):
        """Проверка успешного прохождения обеих ступеней при валидном ключе."""
        self.mock_verify_fn.return_value = (True, "Ключ подлинный")
        success, msg = authenticate_gatekeeper(self.master_key, self.master_key, self.mock_verify_fn)
        self.assertTrue(success)
        self.assertIn("Врата распахнуты", msg)
        self.mock_verify_fn.assert_called_once_with(self.master_key)

    def test_stage_1_match_stage_2_gateway_failure(self):
        """Проверка ситуации, когда ключ совпал, но внешний шлюз вернул ошибку."""
        self.mock_verify_fn.return_value = (False, "API quota exceeded")
        success, msg = authenticate_gatekeeper(self.master_key, self.master_key, self.mock_verify_fn)
        self.assertFalse(success)
        self.assertIn("шлюз Цитадели временно недоступен", msg)
        self.mock_verify_fn.assert_called_once_with(self.master_key)


if __name__ == "__main__":
    unittest.main()
