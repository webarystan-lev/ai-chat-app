import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
    // Таблица диалогов
    chats: defineTable({
        id: v.string(),             // UUID диалога из Streamlit сессии
                       title: v.string(),          // Заголовок диалога
                       provider: v.string(),       // Выбранный провайдер (например, "Google Gemini")
    model: v.string(),          // Название модели (например, "gemini-2.5-flash")
    systemPrompt: v.string(),   // Инструкция для ИИ
                       temperature: v.float64(),   // Креативность генерации
                       maxTokens: v.float64(),     // Максимальный лимит токенов
                       createdAt: v.float64(),     // Временной штамп создания (timestamp)
    }).index("by_uuid", ["id"]),

                            // Таблица сообщений
                            messages: defineTable({
                                chatId: v.string(),         // Внешний ключ: UUID диалога
                                                  role: v.string(),           // Роль автора реплики ("user" / "assistant")
                            content: v.string(),        // Текст сообщения
                                                  thinking: v.optional(v.string()), // Скрытый блок размышлений модели (thinking)
                            meta: v.optional(v.string()),     // JSON-сериализованный словарь метаданных (время, чин и др.)
                            createdAt: v.float64(),     // Временной штамп добавления
                            }).index("by_chatId", ["chatId"]),
});
