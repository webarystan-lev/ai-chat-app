"""
🏛️ Shekinah AI Portal — Тесты Шлюза ConvexBridge
Проверка реактивной синхронизации данных, fallback-режима и CRUD-операций с мокированием ConvexClient.
"""

import os
import json
import unittest
from unittest.mock import patch, MagicMock
from providers.convex_client import ConvexBridge


class TestConvexBridgeFallback(unittest.TestCase):
    """Тестирование автономного (In-Memory / Fallback) режима при отсутствии подключения к Convex."""

    def setUp(self):
        with patch.dict(os.environ, {}, clear=True):
            self.bridge = ConvexBridge()

    def test_initialization_inactive(self):
        """Проверка, что без CONVEX_URL мост переходит в неактивный режим."""
        self.assertFalse(self.bridge.is_active)
        self.assertIsNone(self.bridge.client)
        self.assertFalse(self.bridge.check_connection())

    def test_chats_fallback_safe(self):
        """Проверка безопасного возврата при операциях с чатами в fallback-режиме."""
        self.assertEqual(self.bridge.load_all_chats(), {})
        self.assertFalse(self.bridge.save_chat("chat-1", {}))
        self.assertFalse(self.bridge.rename_chat("chat-1", "Новое Название"))
        self.assertFalse(self.bridge.delete_chat("chat-1"))
        self.assertFalse(self.bridge.add_message("chat-1", {"role": "user", "content": "Тестовая реплика"}))


class TestConvexBridgeActive(unittest.TestCase):
    """Тестирование CRUD-методов ConvexBridge с активным мокированным клиентом."""

    def setUp(self):
        with patch.dict(os.environ, {}, clear=True):
            self.bridge = ConvexBridge()
        self.mock_client = MagicMock()
        self.bridge.client = self.mock_client
        self.bridge.is_active = True

    def test_check_connection_success(self):
        """Проверка успешной проверки связи."""
        self.mock_client.query.return_value = []
        self.assertTrue(self.bridge.check_connection())
        self.mock_client.query.assert_called_with("chats:list")

    def test_check_connection_failure(self):
        """Проверка обработки сетевого сбоя при проверке связи."""
        self.mock_client.query.side_effect = Exception("Convex network timeout")
        self.assertFalse(self.bridge.check_connection())

    def test_load_all_chats(self):
        """Проверка загрузки всех чатов со сбором сообщений и разбором JSON-метаданных."""
        self.mock_client.query.side_effect = [
            # 1-й вызов: chats:list
            [{
                "id": "chat-shekinah-1",
                "title": "Беседа о благодати",
                "provider": "Google Gemini",
                "model": "gemini-2.5-flash",
                "temperature": 0.7,
                "maxTokens": 4096,
                "systemPrompt": "Будь благословенным наставником."
            }],
            # 2-й вызов: messages:listForChat
            [{
                "id": "msg-1",
                "role": "user",
                "content": "Мир вам!",
                "timestamp": "2026-09-06T12:00:00Z",
                "meta": json.dumps({"rank": "Архитектор"})
            }]
        ]

        chats = self.bridge.load_all_chats()
        self.assertIn("chat-shekinah-1", chats)
        chat = chats["chat-shekinah-1"]
        self.assertEqual(chat["title"], "Беседа о благодати")
        self.assertEqual(len(chat["messages"]), 1)
        self.assertEqual(chat["messages"][0]["meta"]["rank"], "Архитектор")

    def test_save_chat(self):
        """Проверка сохранения параметров нового или существующего чата."""
        self.mock_client.mutation.return_value = "chat-123"
        chat_data = {
            "title": "Новый Свиток",
            "provider": "Google Gemini",
            "model": "gemini-2.5-pro",
            "temperature": 0.7,
            "max_tokens": 8192,
            "system_prompt": "Канон мудрости"
        }
        res = self.bridge.save_chat("chat-123", chat_data)
        self.assertTrue(res)
        self.mock_client.mutation.assert_called_once()
        args = self.mock_client.mutation.call_args[0]
        self.assertEqual(args[0], "chats:save")
        self.assertEqual(args[1]["id"], "chat-123")
        self.assertEqual(args[1]["title"], "Новый Свиток")

    def test_rename_chat(self):
        """Проверка переименования чата в Convex DB."""
        self.mock_client.mutation.return_value = None
        res = self.bridge.rename_chat("chat-123", "Обновленное Название")
        self.assertTrue(res)
        self.mock_client.mutation.assert_called_with("chats:rename", {
            "id": "chat-123",
            "title": "Обновленное Название"
        })

    def test_delete_chat(self):
        """Проверка удаления чата из Convex DB."""
        self.mock_client.mutation.return_value = None
        res = self.bridge.delete_chat("chat-123")
        self.assertTrue(res)
        self.mock_client.mutation.assert_called_with("chats:remove", {"id": "chat-123"})

    def test_add_message(self):
        """Проверка записи сообщения с сериализацией метаданных в JSON."""
        self.mock_client.mutation.return_value = "msg-999"
        msg_payload = {
            "id": "msg-999",
            "role": "assistant",
            "content": "Слово мудрости",
            "timestamp": "2026-09-06T12:05:00Z",
            "meta": {"thinking_time": 1.25}
        }
        res = self.bridge.add_message("chat-123", msg_payload)
        self.assertTrue(res)
        args = self.mock_client.mutation.call_args[0]
        self.assertEqual(args[0], "messages:add")
        self.assertEqual(args[1]["chatId"], "chat-123")
        self.assertEqual(args[1]["content"], "Слово мудрости")
        # Проверяем сериализацию meta
        meta_dict = json.loads(args[1]["meta"])
        self.assertEqual(meta_dict["thinking_time"], 1.25)


if __name__ == "__main__":
    unittest.main()
