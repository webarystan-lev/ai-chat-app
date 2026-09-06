"""
🏛️ Shekinah AI Portal — Тесты Мультимодельных ИИ-Провайдеров
Проверка клиентов Google Gemini, Anthropic Claude и Mistral AI с изоляцией сетевых вызовов и мокированием.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from providers import gemini_client, anthropic_client, mistral_client


class TestGeminiClient(unittest.TestCase):
    """Тестирование клиента Google Gemini (новый SDK google-genai)."""

    def test_missing_api_key(self):
        """Проверка безопасного поведения при отсутствии ключа API."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn("Ошибка", gemini_client.ask_gemini("Привет"))
            stream_res = list(gemini_client.stream_gemini([{"role": "user", "content": "Привет"}]))
            self.assertTrue(any("Ошибка" in chunk for chunk in stream_res))
            self.assertEqual(gemini_client.list_available_gemini_models(), [])

    @patch("providers.gemini_client.genai.Client")
    def test_ask_gemini_success(self, mock_client_cls):
        """Проверка успешной генерации ответа Gemini."""
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "Благодать Господа с вами."
        mock_client.models.generate_content.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key_123"}):
            answer = gemini_client.ask_gemini("Молитва", model_name="gemini-2.5-flash")
            self.assertEqual(answer, "Благодать Господа с вами.")
            mock_client.models.generate_content.assert_called_once()

    @patch("providers.gemini_client.genai.Client")
    def test_stream_gemini_success(self, mock_client_cls):
        """Проверка потоковой генерации Gemini."""
        mock_client = MagicMock()
        chunk1 = MagicMock(text="Свет ")
        chunk2 = MagicMock(text="и Истина.")
        mock_client.models.generate_content_stream.return_value = [chunk1, chunk2]
        mock_client_cls.return_value = mock_client

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key_123"}):
            chunks = list(gemini_client.stream_gemini([
                {"role": "system", "content": "Наставник"},
                {"role": "user", "content": "Наставь"}
            ]))
            self.assertEqual("".join(chunks), "Свет и Истина.")

    @patch("providers.gemini_client.genai.Client")
    def test_list_available_gemini_models(self, mock_client_cls):
        """Проверка фильтрации моделей Gemini по действию generateContent."""
        mock_client = MagicMock()
        m1 = MagicMock(supported_actions=["generateContent"])
        m1.name = "models/gemini-2.5-pro"
        m2 = MagicMock(supported_actions=["embedContent"])
        m2.name = "models/text-embedding-004"
        m3 = MagicMock(supported_actions=["generateContent"])
        m3.name = "models/gemini-2.5-flash"
        mock_client.models.list.return_value = [m1, m2, m3]
        mock_client_cls.return_value = mock_client

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key_123"}):
            models = gemini_client.list_available_gemini_models()
            self.assertIn("gemini-2.5-pro", models)
            self.assertIn("gemini-2.5-flash", models)
            self.assertNotIn("text-embedding-004", models)


class TestAnthropicClient(unittest.TestCase):
    """Тестирование клиента Anthropic Claude."""

    def test_missing_api_key(self):
        """Проверка поведения Anthropic при отсутствии ключа."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn("Ошибка", anthropic_client.ask_anthropic("Вопрос"))
            stream_res = list(anthropic_client.stream_anthropic([], "claude-3-5-sonnet", 0.7, 1000))
            self.assertTrue(any("Ошибка" in chunk for chunk in stream_res))
            self.assertEqual(anthropic_client.list_available_anthropic_models(), [])

    @patch("providers.anthropic_client.Anthropic")
    def test_ask_anthropic_success(self, mock_anthropic_cls):
        """Проверка генерации ответа Anthropic."""
        mock_client = MagicMock()
        mock_block = MagicMock()
        mock_block.text = "Академический ответ Соратника."
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            res = anthropic_client.ask_anthropic("Запрос", system_prompt="Системный канон")
            self.assertEqual(res, "Академический ответ Соратника.")
            mock_client.messages.create.assert_called_once()

    @patch("providers.anthropic_client.Anthropic")
    def test_stream_anthropic_success(self, mock_anthropic_cls):
        """Проверка потоковой генерации Anthropic."""
        mock_client = MagicMock()
        mock_stream_ctx = MagicMock()
        mock_stream = MagicMock()
        mock_stream.text_stream = ["Премудрость ", "Цитадели."]
        mock_stream_ctx.__enter__.return_value = mock_stream
        mock_stream_ctx.__exit__.return_value = False
        mock_client.messages.stream.return_value = mock_stream_ctx
        mock_anthropic_cls.return_value = mock_client

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            chunks = list(anthropic_client.stream_anthropic(
                [{"role": "user", "content": "Слово"}],
                "claude-3-5-sonnet",
                0.7,
                2000
            ))
            self.assertEqual("".join(chunks), "Премудрость Цитадели.")

    @patch("providers.anthropic_client.Anthropic")
    def test_list_available_anthropic_models(self, mock_anthropic_cls):
        """Проверка опроса моделей Anthropic."""
        mock_client = MagicMock()
        m1 = MagicMock(id="claude-3-5-sonnet-20241022")
        m2 = MagicMock(id="claude-3-5-haiku-20241022")
        mock_client.models.list.return_value = MagicMock(data=[m1, m2])
        mock_anthropic_cls.return_value = mock_client

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key"}):
            models = anthropic_client.list_available_anthropic_models()
            self.assertIn("claude-3-5-sonnet-20241022", models)
            self.assertIn("claude-3-5-haiku-20241022", models)


class TestMistralClient(unittest.TestCase):
    """Тестирование клиента Mistral AI."""

    def test_missing_api_key(self):
        """Проверка поведения Mistral при отсутствии ключа."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn("Ошибка", mistral_client.ask_mistral("Вопрос"))
            stream_res = list(mistral_client.stream_mistral([], "mistral-large-latest", 0.7, 1000))
            self.assertTrue(any("Ошибка" in chunk for chunk in stream_res))
            self.assertEqual(mistral_client.list_available_mistral_models(), [])

    @patch("providers.mistral_client.Mistral")
    def test_ask_mistral_success(self, mock_mistral_cls):
        """Проверка генерации ответа Mistral."""
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Ответ Европейского Гения."
        mock_response = MagicMock(choices=[mock_choice])
        mock_client.chat.complete.return_value = mock_response
        mock_mistral_cls.return_value = mock_client

        with patch.dict(os.environ, {"MISTRAL_API_KEY": "mis-test-key"}):
            res = mistral_client.ask_mistral("Запрос", system_prompt="Системный канон")
            self.assertEqual(res, "Ответ Европейского Гения.")
            mock_client.chat.complete.assert_called_once()

    @patch("providers.mistral_client.Mistral")
    def test_stream_mistral_success(self, mock_mistral_cls):
        """Проверка потоковой генерации Mistral."""
        mock_client = MagicMock()
        chunk1 = MagicMock()
        chunk1.data.choices = [MagicMock(delta=MagicMock(content="Благословение "))]
        chunk2 = MagicMock()
        chunk2.data.choices = [MagicMock(delta=MagicMock(content="Цитадели."))]
        mock_client.chat.stream.return_value = [chunk1, chunk2]
        mock_mistral_cls.return_value = mock_client

        with patch.dict(os.environ, {"MISTRAL_API_KEY": "mis-test-key"}):
            chunks = list(mistral_client.stream_mistral(
                [{"role": "user", "content": "Слово"}],
                "mistral-large-latest",
                0.7,
                2000
            ))
            self.assertEqual("".join(chunks), "Благословение Цитадели.")

    @patch("providers.mistral_client.Mistral")
    def test_list_available_mistral_models(self, mock_mistral_cls):
        """Проверка фильтрации текстовых моделей Mistral (без embed/ocr/tts)."""
        mock_client = MagicMock()
        m1 = MagicMock(id="mistral-large-latest")
        m2 = MagicMock(id="mistral-embed")
        m3 = MagicMock(id="codestral-latest")
        mock_client.models.list.return_value = MagicMock(data=[m1, m2, m3])
        mock_mistral_cls.return_value = mock_client

        with patch.dict(os.environ, {"MISTRAL_API_KEY": "mis-test-key"}):
            models = mistral_client.list_available_mistral_models()
            self.assertIn("mistral-large-latest", models)
            self.assertIn("codestral-latest", models)
            self.assertNotIn("mistral-embed", models)


if __name__ == "__main__":
    unittest.main()
