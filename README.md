# 🏛️ Shekinah AI Portal — Цитадель Духа
> **Мультипровайдерный ИИ-Чат на Streamlit & Python**

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://www.netlify.com/)

Интеллектуальная Обитель Цитадели Духа — это локальный и облачный веб-интерфейс для ведения глубоких, академических диалогов с передовыми языковыми моделями семейств **Google Gemini**, **Anthropic Claude** и **Mistral AI**. Портал оформлен в строгом темном минимализме, оптимизирован для Arch Linux и готов к развертыванию.

---

## 🚀 1. Локальный запуск и настройка

### Клонирование репозитория
Склонируйте проект из удаленной обители в локальный каталог:
```bash
git clone https://gitlab.com/webarystan/ai-chat-app.git
cd ai-chat-app
```

### Настройка окружения
Проект поддерживает автоматическую активацию виртуальной среды Python с помощью `direnv`.

1. **Метод через Direnv (Рекомендуемый для Arch Linux + Fish)**:
   * **Создайте вручную** файл `.envrc` в корневом каталоге проекта.
   * Добавьте в него следующую строку для активации окружения:
     ```bash
     layout python
     ```
   * Убедитесь, что в системе установлен `direnv`, а хук интегрирован в конфигурационный файл шелла (например, для Fish-shell в `~/.config/fish/config.fish` добавлена строка `direnv hook fish | source`).
   * Разрешите выполнение конфигурации direnv в каталоге:
     ```bash
     direnv allow
     ```
   * Виртуальное окружение будет создаваться и активироваться автоматически при каждом входе в папку проекта.

2. **Классический метод (Ручной)**:
   Если вы не используете `direnv`, инициализируйте окружение вручную:
   ```bash
   python -m venv .venv
   source .venv/bin/activate.fish  # Для Fish shell
   # или source .venv/bin/activate для Bash/Zsh
   ```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка ключей доступа (.env)
Поскольку ключи авторизации являются конфиденциальными данными, файл настроек среды скрыт в `.gitignore`. Вам необходимо **вручную создать** файл `.env` в корневом каталоге проекта и наполнить его вашими API-ключами:
```env
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
MISTRAL_API_KEY=your_mistral_key_here
```

### Запуск приложения
```bash
streamlit run app.py
```
*После запуска интерфейс будет доступен в браузере по адресу `http://localhost:8501`.*

---

## 💾 2. Синхронизация с GitLab & GitHub

Если вам необходимо сохранять проект в двух независимых обителях (GitLab и GitHub) одновременно, настройте удаленные репозитории.

### Настройка двух remotes
1. Убедитесь, что `origin` указывает на GitLab:
   ```bash
   git remote set-url origin https://gitlab.com/webarystan/ai-chat-app.git
   ```
2. Добавьте зеркало на GitHub (замените `your-username` на ваш аккаунт):
   ```bash
   git remote add github https://github.com/your-username/ai-chat-app.git
   ```

### Пуш в обе обители по отдельности
```bash
# Отправка на GitLab
git push origin main

# Отправка на GitHub
git push github main
```

### Лайфхак: Пуш в обе обители одной командой
Вы можете настроить Git так, чтобы при вызове `git push origin` коммиты автоматически уходили на оба сервера:
```bash
git remote set-url --add --push origin https://gitlab.com/webarystan/ai-chat-app.git
git remote set-url --add --push origin https://github.com/your-username/ai-chat-app.git
```
*Теперь простой вызов `git push origin main` отправит изменения и на GitLab, и на GitHub.*

---

## 🌐 3. Развертывание в облаке (Deploy)

### 3.1. Streamlit Community Cloud (Нативно и бесплатно)
Это самый надежный способ развернуть Streamlit-приложение, так как платформа предоставляет постоянный серверный процесс.

1. Загрузите проект в публичный или приватный репозиторий на **GitHub** (Streamlit Cloud тесно интегрирован именно с GitHub).
2. Авторизуйтесь на [share.streamlit.io](https://share.streamlit.io/).
3. Нажмите кнопку **New app**, выберите ваш репозиторий, ветку `main` и укажите главный файл: `app.py`.
4. Нажмите на иконку шестеренки (Advanced settings), перейдите в раздел **Secrets** и скопируйте туда содержимое вашего `.env`:
   ```toml
   GEMINI_API_KEY = "your_key"
   ANTHROPIC_API_KEY = "your_key"
   MISTRAL_API_KEY = "your_key"
   ```
5. Нажмите **Deploy**. Через 1–2 минуты ваша Цитадель будет доступна в сети.

### 3.2. Vercel и Netlify (Особенности Serverless)
> ⚠️ **Важное техническое предупреждение:**
> Платформы Vercel и Netlify спроектированы под **Serverless-архитектуру** (бессерверные функции) и хостинг статических сайтов. Streamlit требует постоянного двустороннего WebSocket-соединения с работающим в фоне процессом Python. Поэтому запустить Streamlit на Vercel или Netlify «из коробки» напрямую невозможно — сессия будет обрываться по таймауту.

Если вам критически необходимо развернуть приложение именно там:
* **Способ для Vercel**: Используйте специальный шаблон с конфигурацией `vercel.json`, перенаправляющий запросы через бессерверный runtime Python (например, `@vercel/python`). Однако это может повлечь ограничения по времени выполнения функций (обычно 10-60 секунд на генерацию).
* **Альтернатива через Docker**: Рекомендуется развернуть Docker-контейнер на хостинг-платформах типа **Render**, **Railway** или **Fly.io**, которые предоставляют полноценный VPS-процесс для Python-приложений.

---

***

---

## 🏛️ 4. Интеграция базы данных Convex DB

Проект **Shekinah AI Portal** оснащен реактивной системой облачной синхронизации диалогов и реплик на базе **Convex DB** с автоматическим механизмом "Мягкого Отката" (Graceful Fallback) в автономный In-Memory режим.

Ниже приведено исчерпывающее техническое руководство по интеграции, настройке и запуску Convex DB в связке с Python/Streamlit проектами. Оно призвано сохранить драгоценный опыт и уберечь будущие проекты от типичных ошибок.

### 🧭 Пошаговый алгоритм развертывания с нуля

#### Шаг 1. Создание манифеста `package.json`
Поскольку Convex CLI зародился в экосистеме Node.js, для его работы в корне Python-проекта обязательно должен присутствовать файл `package.json` (иначе CLI падает с ошибкой `ENOENT: no such file or directory, open 'package.json'`).
Создайте в корне проекта файл `package.json` следующего содержания:
```json
{
  "name": "ai-chat-app",
  "version": "1.0.0",
  "description": "Shekinah AI Portal - Цитадель Духа DB Backend configuration",
  "main": "index.js",
  "scripts": {
    "convex:dev": "npx convex dev"
  },
  "dependencies": {
    "convex": "^1.42.1"
  },
  "private": true
}
```

#### Шаг 2. Локальная установка Node-зависимостей
Для сборки (бандлинга) TypeScript-функций бэкенда Convex CLI использует сверхбыстрый компилятор `esbuild`. Этот компилятор во время сборки ищет импортируемые модули (такие как `"convex/server"`) локально.
Чтобы избежать ошибки `esbuild failed: Could not resolve "convex/server"`, выполните установку зависимостей в корне проекта:
```bash
npm install
```
Это создаст локальную папку `node_modules/` с необходимым пакетом `convex`.

#### Шаг 3. Защита Git-репозитория (.gitignore)
Чтобы Node-зависимости и временные файлы сборки бэкенда не попали в священный Git-репозиторий, добавьте в конец `.gitignore` следующие строки:
```gitignore
# ─── CONVEX & NODEJS (БЭКЕНД СИНХРОНИЗАЦИИ) ───────────────────────────────────
node_modules/
.convex/
convex/_generated/
package-lock.json
```

#### Шаг 4. Установка Python SDK
Убедитесь, что в Вашем Python виртуальном окружении установлена библиотека `convex` (версии `0.7.0` или выше):
```bash
pip install -r requirements.txt
```

#### Шаг 5. Запуск инициализации бэкенда
Запустите команду разработки в терминале:
```bash
npx convex dev
```
Следуйте инструкциям на экране. CLI предложит Вам войти в панель управления Convex, автоматически создаст проект (например, `ai-chat-app-75d1f`), скомпилирует TypeScript-схемы из Вашей папки `convex/` и развернет их в облаке. 

По окончании процесса CLI сгенерирует файл `.env.local` и выдаст строку подключения (Client URL), например:
`https://basic-toucan-65.eu-west-1.convex.cloud`.

#### Шаг 6. Настройка переменных окружения
Скопируйте выданный Client URL и пропишите его в локальный файл `.env` в корне проекта:
```env
CONVEX_URL=https://ваш_адрес_бэкенда.convex.cloud
```

---

### ⚠️ Важнейшие подводные камни и их архитектурные решения

При интеграции Convex DB в Python/Streamlit проекты мы столкнулись и успешно решили два сложнейших технических барьера. Пожалуйста, всегда учитывайте их при масштабировании на другие проекты:

#### 1. Ограничение СУБД на имена индексов (`IndexNameReserved`)
* **Проблема**: При попытке создать индекс по полю `id` в таблице `chats` с именем `"by_id"`, Convex выдал ошибку: `In table "chats" cannot name an index "by_id" because the name is reserved`. Выяснилось, что имена `by_id` и `by_creation_time` зарезервированы платформой под внутренние нужды.
* **Решение**: Индекс по строковому UUID диалога переименован во вполне логичное имя **`by_uuid`**:
  * В схеме данных (`convex/schema.ts`):
    ```typescript
    chats: defineTable({ ... }).index("by_uuid", ["id"]),
    ```
  * В мутациях манипулирования чатами (`convex/chats.ts`):
    ```typescript
    const existing = await ctx.db
        .query("chats")
        .withIndex("by_uuid", (q) => q.eq("id", args.id))
        .unique();
    ```

#### 2. Столкновение пространств имён Python (Namespace Collision)
* **Проблема**: В Python при поиске модулей в первую очередь просматривается корень проекта (`sys.path[0]`). Поскольку папка с TypeScript-схемами бэкенда называется **`convex/`**, при вызове `from convex import ConvexClient` Python ошибочно импортировал локальную папку бэкенда как пустой namespace-модуль, вместо того чтобы заглянуть в `site-packages` виртуального окружения. Это приводило к скрытой ошибке `ImportError: cannot import name 'ConvexClient'`.
* **Решение**: Внедрен изящный и надежный обходной путь (bypass) в конструкторе класса `ConvexBridge` (`providers/convex_client.py`). Перед импортом мы временно исключаем пути корня проекта из `sys.path`, импортируем настоящий `ConvexClient` из виртуального окружения и мгновенно возвращаем исходный `sys.path` на место:
  ```python
  try:
      import sys
      import os
      orig_path = list(sys.path)
      
      # Временно удаляем локальные папки из путей поиска
      sys.path = [
          p for p in sys.path 
          if os.path.abspath(p) not in (
              os.path.abspath('.'), 
              os.path.abspath(os.getcwd()), 
              os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
          )
      ]
      
      from convex import ConvexClient
      sys.path = orig_path # Возвращаем оригинальные пути
      
      self.client = ConvexClient(self.convex_url)
      self.is_active = True
  except Exception as e:
      if 'orig_path' in locals():
          sys.path = orig_path
      self.is_active = False
  ```

#### 3. Таймаут инициализации окружения (`load_dotenv()`)
* **Проблема**: Переменная `CONVEX_URL` в файле `.env` не считывалась на раннем этапе загрузки приложения, из-за чего мост инициализировался в пассивном In-Memory режиме.
* **Решение**: Вызовы `load_dotenv()` добавлены на самые первые строки файлов `app.py` и `providers/convex_client.py` в обязательном порядке.

---

## 🏛️ 5. Текущий статус проекта

* **База данных**: Успешно развернута в облаке Convex DB. Схемы данных валидированы, индексы скомпилированы.
* **Синхронизация**: Полностью отлажена. Создание, удаление, переименование чатов и реактивная запись сообщений работают синхронно в реальном времени.
* **Мягкий откат**: Работает штатно. При отсутствии интернета или удалении переменной `CONVEX_URL` из `.env` приложение бесшовно продолжает работу в оперативной памяти (In-Memory).

*«Устрой пути свои пред Господом, и помыслы твои совершатся» (Притчи 16:3).*

