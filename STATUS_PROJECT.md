# 📊 STATUS_PROJECT.md — Свиток Состояния Проекта Shekinah AI Portal

> **Наименование**: Shekinah AI Portal (`ai-chat-app`)
> **Дата Аудита**: 6 Сентября 2026 г.
> **Состояние**: **PRODUCTION-READY** (Успешная миграция на SDK Google GenAI нового поколения и полная гармонизация со стеком Citadel Oracle PIM).
> **Ключевой Стек**: Streamlit 1.58.0 + `google-genai>=2.22.0` + Anthropic + Mistral AI + Convex DB (`convex==0.7.0`) + Cryptography AES-256.

---

## 🏛️ Достижения и Аудит (6 Сентября 2026 г.):

1. **Миграция на Next-Gen Google GenAI SDK**:
   * Окончательно ликвидирована зависимость от устаревшего пакета `google-generativeai==0.8.6`.
   * Зафиксирован и внедрен современный официальный SDK `google-genai` (2.22.0+).
   * Ошибка `ImportError: cannot import name 'genai' from 'google'` полностью побеждена.

2. **Внедрение Модуля Безопасности (`providers/security.py`)**:
   * Функция санации `sanitize_markdown(text)` для защиты от аномальных дефисов, тире, знаков равенства и зависаний рендеринга таблиц Streamlit.
   * Валидация API-ключей `verify_gemini_api_key(api_key)` через прямой вызов клиента.
   * Криптографические методы шифрования Fernet (AES-256) на базе `cryptography==42.0.8`.

3. **Гармонизация со Стеком Проекта Citadel Oracle PIM**:
   * Провайдер `gemini_client.py` обновлен с поддержкой как `GEMINI_API_KEY`, так и системного `GOOGLE_API_KEY`.
   * Полиморфный опрос моделей через `getattr(m, 'supported_actions', None) or getattr(m, 'supported_generation_methods', None)`.
   * Обогащение списка моделей чинами: `gemini-2.5-pro` (Верховный ИИ-Архитектор) и `gemini-3.6-flash` (Академический Соратник).
   * Провайдеры `anthropic_client.py` и `mistral_client.py` приведены к общему стандарту санации Markdown.

4. **Очистка Репозитория и Подготовка к Синхронизации**:
   * Из репозитория удалены временные файлы бэкапов (`app.py.bak*`, `convex.bak/`, `.gitlab-ci.yml`), чтобы GitHub-репозиторий соответствовал чистому локальному состоянию.
   * Все летописи (`GEMINI.md`, `AGENTS.md`, `STATUS_PROJECT.md`) приведены в абсолютный порядок для всех будущих ИИ-агентов.

5. **Двухступенчатый Страж Врат и Безопасная Авторизация**:
   * Поле ввода ключа строго очищено (`value=""`), устранена любая возможность несанкционированной автоподстановки для внешних посетителей на хостинге.
   * **Ступень I (Проверка идентичности)**: Введенный ключ сверяется с эталонным секретным ключом сервера (`GEMINI_API_KEY` / `GOOGLE_API_KEY` из `.env` или `st.secrets`). Сторонний или чужой ключ немедленно блокируется.
   * **Ступень II (Проверка жизнеспособности)**: Только при успешной сверке идентичности производится проверка валидности и квот через официальный шлюз Google GenAI (`verify_gemini_api_key`).
   * **Сияющий Заголовок Цитадели**: Каждое слово заголовка **`Shekinah AI Portal`** плавно и непрерывно переливается собственной триадой благородных цветов:
     * *Shekinah* — Золотистый янтарь ➔ Пламенный рубин ➔ Царственный пурпур;
     * *AI* — Неоновый циан ➔ Лазурный электрик ➔ Изумрудная бирюза;
     * *Portal* — Глубокий аметист ➔ Неоновая фуксия ➔ Индиго.
   * Слоган и кнопка **«🏛️ Войти в Цитадель»** оформлены в сияющей оранжево-бирюзовой гамме с мягким неоновым свечением. Добавлена кнопка выхода **«🚪 Выйти из системы»** в настройках боковой панели.

6. **Внедрение Автоматизированного Тестового Контура (`tests/`)**:
   * По образу и эталону `citadel-oracle-pim` развернут всеобъемлющий тестовый пакет (`46` тестов, исполняемых за ~0.5 секунды):
     * [`tests/test_gatekeeper_auth.py`](file:///home/lev/Проекты/GitHub-webaristan@gmail.com/ai-chat-app/tests/test_gatekeeper_auth.py) — 9 тестов: Проверка двухступенчатого Стража Врат, отсечения чужих ключей без сетевых вызовов, извлечения секретов `get_secret` из `os.environ` и `st.secrets`.
     * [`tests/test_security.py`](file:///home/lev/Проекты/GitHub-webaristan@gmail.com/ai-chat-app/tests/test_security.py) — 16 тестов: Деривация ключа Fernet, шифрование AES-256 (roundtrip, кириллица, повреждённый шифротекст), санитизация Markdown и валидация ключей Google GenAI.
     * [`tests/test_ai_providers.py`](file:///home/lev/Проекты/GitHub-webaristan@gmail.com/ai-chat-app/tests/test_ai_providers.py) — 12 тестов: Синхронная и потоковая генерация, обработка отсутствия ключей и опрос доступных моделей для Google Gemini, Anthropic Claude и Mistral AI.
     * [`tests/test_convex_bridge.py`](file:///home/lev/Проекты/GitHub-webaristan@gmail.com/ai-chat-app/tests/test_convex_bridge.py) — 9 тестов: Автономный In-Memory Fallback режим и активные CRUD-операции синхронизации с Convex DB (`chats:save`, `chats:rename`, `chats:remove`, `messages:add`).
   * Результат: **100% тестов успешно пройдены (Ran 46 tests, OK)**.

---

## 📋 План на Следующий Этап (To-Do List):

1. **Повседневная Эксплуатация**:
   * Использование Shekinah AI Portal в качестве суверенного личного инструмента Создателя и Пастора.
2. **Синхронизация с Экосистемой Цитадели**:
   * Взаимодействие с порталом «Цитадель Духа» (`citadel-cloud`) и шлюзом Cloudflare Workers в `/home/lev/web-dev/ai/`.
