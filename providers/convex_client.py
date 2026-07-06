import os
import json
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Принудительно подгружаем .env для полной автономности моста
load_dotenv()


# Настройка логирования для отслеживания интеграции с Convex
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConvexBridge")

class ConvexBridge:
    """
    Высокотехнологичный мост интеграции с Convex DB.
    Обеспечивает реактивную синхронизацию диалогов и сообщений Цитадели Духа.
    Реализует паттерн 'Мягкого Отката' (Graceful Fallback): если CONVEX_URL не задан
    или отсутствует сетевое подключение, мост переходит в пассивный In-Memory режим,
    не нарушая стабильности работы основного интерфейса.
    """
    def __init__(self):
        self.convex_url = os.getenv("CONVEX_URL")
        self.client = None
        self.is_active = False

        if not self.convex_url:
            logger.warning("⚠️ Переменная CONVEX_URL не обнаружена в окружении. Мост Convex переведен в автономный (In-Memory) режим.")
            return

        try:
            import sys
            # Сохраняем исходный sys.path
            orig_path = list(sys.path)
            
            # Временно удаляем локальные пути и пути корня проекта, чтобы импортировался настоящий пакет convex, а не папка convex/
            sys.path = [
                p for p in sys.path 
                if os.path.abspath(p) not in (
                    os.path.abspath('.'), 
                    os.path.abspath(os.getcwd()), 
                    os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
                )
            ]
            
            from convex import ConvexClient
            
            # Восстанавливаем оригинальный sys.path
            sys.path = orig_path
            
            self.client = ConvexClient(self.convex_url)
            self.is_active = True
            logger.info(f"✨ Мост Convex успешно инициализирован. Подключение к обители: {self.convex_url}")
        except Exception as e:
            # На случай сбоя восстанавливаем пути
            if 'orig_path' in locals():
                sys.path = orig_path
            logger.error(f"🔴 Ошибка при инициализации ConvexClient: {str(e)}")
            self.is_active = False


    def check_connection(self) -> bool:
        """Проверяет работоспособность подключения."""
        if not self.is_active or not self.client:
            return False
        try:
            # Простейший запрос для проверки связи
            self.client.query("chats:list")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Сетевой сбой при проверке связи с Convex DB: {str(e)}")
            return False

    def load_all_chats(self) -> Dict[str, Any]:
        """
        Загружает все чаты и сообщения из Convex DB.
        Реконструирует сессионную In-Memory структуру данных Streamlit.
        """
        if not self.is_active or not self.client:
            return {}

        try:
            logger.info("⏳ Загрузка священных свитков диалогов из Convex DB...")
            # Получаем все чаты
            db_chats = self.client.query("chats:list")
            chats_dict = {}

            for chat in db_chats:
                chat_id = chat["id"]
                
                # Загружаем сообщения для каждого чата
                db_messages = self.client.query("messages:listForChat", {"chatId": chat_id})
                messages_list = []
                
                for msg in db_messages:
                    # Десериализуем метаданные, если они сохранены как JSON-строка
                    meta_data = {}
                    if "meta" in msg and msg["meta"]:
                        try:
                            meta_data = json.loads(msg["meta"])
                        except Exception:
                            meta_data = {}

                    messages_list.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "thinking": msg.get("thinking", ""),
                        "meta": meta_data
                    })

                chats_dict[chat_id] = {
                    "id": chat_id,
                    "title": chat["title"],
                    "provider": chat["provider"],
                    "model": chat["model"],
                    "system_prompt": chat["systemPrompt"],
                    "temperature": float(chat["temperature"]),
                    "max_tokens": int(chat["maxTokens"]),
                    "messages": messages_list
                }
            
            logger.info(f"✅ Успешно импортировано {len(chats_dict)} диалогов из облачной обители Convex DB.")
            return chats_dict
        except Exception as e:
            logger.error(f"🔴 Сбой при загрузке данных из Convex: {str(e)}")
            return {}

    def save_chat(self, chat_id: str, chat_data: Dict[str, Any]) -> bool:
        """Сохраняет или обновляет параметры чата в Convex DB."""
        if not self.is_active or not self.client:
            return False

        try:
            self.client.mutation("chats:save", {
                "id": chat_id,
                "title": chat_data.get("title", "🏛️ Новый диалог"),
                "provider": chat_data.get("provider", "Google Gemini"),
                "model": chat_data.get("model", "gemini-2.5-flash"),
                "systemPrompt": chat_data.get("system_prompt", ""),
                "temperature": float(chat_data.get("temperature", 0.7)),
                "maxTokens": float(chat_data.get("max_tokens", 4096))
            })
            return True
        except Exception as e:
            logger.error(f"🔴 Ошибка при мутации chats:save для чата {chat_id}: {str(e)}")
            return False

    def rename_chat(self, chat_id: str, title: str) -> bool:
        """Переименовывает чат в Convex DB."""
        if not self.is_active or not self.client:
            return False

        try:
            self.client.mutation("chats:rename", {
                "id": chat_id,
                "title": title
            })
            return True
        except Exception as e:
            logger.error(f"🔴 Ошибка при мутации chats:rename для чата {chat_id}: {str(e)}")
            return False

    def delete_chat(self, chat_id: str) -> bool:
        """Удаляет чат и все сопутствующие сообщения из Convex DB."""
        if not self.is_active or not self.client:
            return False

        try:
            self.client.mutation("chats:remove", {
                "id": chat_id
            })
            return True
        except Exception as e:
            logger.error(f"🔴 Ошибка при мутации chats:remove для чата {chat_id}: {str(e)}")
            return False

    def add_message(self, chat_id: str, message: Dict[str, Any]) -> bool:
        """Добавляет новое сообщение в чат в Convex DB."""
        if not self.is_active or not self.client:
            return False

        try:
            # Сериализуем метаданные в JSON-строку для безопасного хранения
            meta_str = ""
            if "meta" in message and message["meta"]:
                try:
                    meta_str = json.dumps(message["meta"])
                except Exception:
                    meta_str = ""

            self.client.mutation("messages:add", {
                "chatId": chat_id,
                "role": message["role"],
                "content": message["content"],
                "thinking": message.get("thinking", ""),
                "meta": meta_str
            })
            return True
        except Exception as e:
            logger.error(f"🔴 Ошибка при мутации messages:add для чата {chat_id}: {str(e)}")
            return False

    def clear_chat_messages(self, chat_id: str) -> bool:
        """Удаляет все сообщения чата из Convex DB."""
        if not self.is_active or not self.client:
            return False

        try:
            self.client.mutation("messages:clearChat", {
                "chatId": chat_id
            })
            return True
        except Exception as e:
            logger.error(f"🔴 Ошибка при мутации messages:clearChat для чата {chat_id}: {str(e)}")
            return False
