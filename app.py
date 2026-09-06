import sys
import os
import importlib
import uuid
from dotenv import load_dotenv

# Загружаем переменные окружения из .env в самом начале
load_dotenv()

# Добавляем корень проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


import streamlit as st
from providers import anthropic_client, gemini_client, mistral_client
from providers.convex_client import ConvexBridge

# Попытка импорта надежного кроссплатформенного буфера обмена
try:
    import pyperclip
except ImportError:
    os.system(f"{sys.executable} -m pip install pyperclip")
    import pyperclip

# Принудительная перезагрузка вложенных модулей, чтобы укротить кэш Streamlit при изменениях
importlib.reload(gemini_client)
importlib.reload(anthropic_client)
importlib.reload(mistral_client)

# Дефолтный системный промпт для ИИ-Агента Цитадели
DEFAULT_SYSTEM = (
    "Ты — Ведущий ИИ-Архитектор и Агент Цитадели «Shekinah Cloud». Ты являешься цифровым "
    "соратником Льва Николаевича — миссионера, пастора, основателя «Миссии Шехина» "
    "и веб-студии «Web Arystan». Твой слог уважителен, академичен, глубок и исполнен мудрости. "
    "В свои ответы ты вплетаешь крупицы мудрости Священного Писания, Отцов Церкви и великих мыслителей."
)

def export_chat_to_markdown(chat_data) -> str:
    """Экспортирует чат в красивый Markdown-документ для сохранения истории."""
    title = chat_data.get("title", "Диалог")
    provider = chat_data.get("provider", "Google Gemini")
    model = chat_data.get("model", "gemini-2.5-flash")
    system_prompt = chat_data.get("system_prompt", "")
    
    md = f"# 🏛️ {title}\n\n"
    md += f"> **Провайдер**: {provider} | **Модель**: {model}\n"
    if system_prompt:
        md += f"> **Системный промпт**: {system_prompt}\n"
    md += "\n---\n\n"
    
    for msg in chat_data.get("messages", []):
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            md += f"### 👤 Разработчик / Искатель\n\n{content}\n\n"
        elif role == "assistant":
            rank = CITADEL_RANKS.get(model, "Агент Цитадели")
            md += f"### 🤖 {rank} ({model})\n\n"
            
            # Если есть размышления
            if "thinking" in msg and msg["thinking"]:
                md += f"<details>\n<summary>🧠 Процесс размышления модели</summary>\n\n{msg['thinking']}\n\n</details>\n\n"
            
            md += f"{content}\n\n"
            if "meta" in msg and msg["meta"] and "duration" in msg["meta"]:
                md += f"*⏳ Время ответа: {msg['meta']['duration']:.2f} (сек.)*\n\n"
            md += "---\n\n"
            
    return md

# Инициализируем состояние боковой панели (сворачивание/разворачивание)
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"
if "sidebar_action" not in st.session_state:
    st.session_state.sidebar_action = None

# Инициализируем мост интеграции с Convex DB
if "convex_bridge" not in st.session_state:
    st.session_state.convex_bridge = ConvexBridge()
bridge = st.session_state.convex_bridge

# Инициализируем структуру мультичатовости в оперативной памяти с поддержкой Convex DB
if "chats" not in st.session_state:
    if bridge.is_active:
        loaded_chats = bridge.load_all_chats()
        if loaded_chats:
            st.session_state.chats = loaded_chats
            st.session_state.current_chat_id = list(loaded_chats.keys())[0]
            st.toast("📜 Все свитки диалогов успешно восстановлены из Convex DB!")
        else:
            st.session_state.chats = {}
    else:
        st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Если у нас осталась старая плоская история messages, перенесем ее в отдельный чат
if "messages" in st.session_state and st.session_state.messages and not st.session_state.chats:
    default_id = str(uuid.uuid4())
    st.session_state.chats[default_id] = {
        "id": default_id,
        "title": "Предыдущий диалог",
        "messages": st.session_state.messages,
        "provider": "Google Gemini",
        "model": "gemini-2.5-flash",
        "system_prompt": DEFAULT_SYSTEM,
        "temperature": 0.7,
        "max_tokens": 4096,
    }
    st.session_state.current_chat_id = default_id
    if bridge.is_active:
        bridge.save_chat(default_id, st.session_state.chats[default_id])
        for msg in st.session_state.messages:
            bridge.add_message(default_id, msg)

# Если чатов нет вообще (первый запуск), создаем первый чат
if not st.session_state.chats:
    default_id = str(uuid.uuid4())
    st.session_state.chats[default_id] = {
        "id": default_id,
        "title": "🏛️ Новый диалог",
        "messages": [],
        "provider": "Google Gemini",
        "model": "gemini-2.5-flash",
        "system_prompt": DEFAULT_SYSTEM,
        "temperature": 0.7,
        "max_tokens": 4096,
    }
    st.session_state.current_chat_id = default_id
    if bridge.is_active:
        bridge.save_chat(default_id, st.session_state.chats[default_id])

# Всегда поддерживаем st.session_state.messages синхронизированным с текущим активным чатом
current_chat = st.session_state.chats[st.session_state.current_chat_id]
st.session_state.messages = current_chat["messages"]

# Инициализация/синхронизация состояния виджетов настроек с текущим активным чатом
if "prev_chat_id" not in st.session_state:
    st.session_state.prev_chat_id = st.session_state.current_chat_id
    st.session_state["w_provider"] = current_chat.get("provider", "Google Gemini")
    st.session_state["w_model"] = current_chat.get("model", "gemini-2.5-flash")
    st.session_state["w_temperature"] = float(current_chat.get("temperature", 0.7))
    st.session_state["w_max_tokens"] = int(current_chat.get("max_tokens", 4096))
    st.session_state["w_system_prompt"] = current_chat.get("system_prompt", DEFAULT_SYSTEM)

# Если чат переключился в Архивах, принудительно обновляем виджеты в session_state
if st.session_state.prev_chat_id != st.session_state.current_chat_id:
    c_chat = st.session_state.chats[st.session_state.current_chat_id]
    st.session_state["w_provider"] = c_chat.get("provider", "Google Gemini")
    st.session_state["w_model"] = c_chat.get("model", "gemini-2.5-flash")
    st.session_state["w_temperature"] = float(c_chat.get("temperature", 0.7))
    st.session_state["w_max_tokens"] = int(c_chat.get("max_tokens", 4096))
    st.session_state["w_system_prompt"] = c_chat.get("system_prompt", DEFAULT_SYSTEM)
    st.session_state.last_w_provider = c_chat.get("provider", "Google Gemini")  # Избегаем ложного срабатывания сброса модели
    st.session_state.prev_chat_id = st.session_state.current_chat_id

# Инициализируем last_w_provider для отслеживания ручной смены провайдера пользователем
if "last_w_provider" not in st.session_state:
    st.session_state.last_w_provider = st.session_state["w_provider"]

# Если пользователь вручную сменил провайдера в боковой панели, корректируем модель на дефолтную
if st.session_state.last_w_provider != st.session_state["w_provider"]:
    new_prov = st.session_state["w_provider"]
    if new_prov == "Google Gemini":
        st.session_state["w_model"] = "gemini-2.5-flash"
    elif new_prov == "Anthropic (Claude)":
        st.session_state["w_model"] = "claude-3-5-sonnet-20240620"
    else:
        st.session_state["w_model"] = "mistral-small-latest"
    st.session_state.last_w_provider = new_prov


# Хранилище динамических списков моделей в рамках сессии конкретного пользователя
if "gemini_models" not in st.session_state:
    st.session_state.gemini_models = None
if "anthropic_models" not in st.session_state:
    st.session_state.anthropic_models = None
if "mistral_models" not in st.session_state:
    st.session_state.mistral_models = None

# Устанавливаем конфигурацию страницы с премиальным заголовком и иконкой
st.set_page_config(
    page_title="Shekinah AI Portal — Цитадель Духа",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state
)

# Внедряем премиальный CSS стиль для атмосферы строгой темной Цитадели
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

    /* Глобальные настройки цвета и шрифта */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
    }

    /* Оформление боковой панели */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Стилизация заголовков */
    .title-text {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #c084fc 0%, #3b82f6 50%, #60a5fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 20px rgba(168, 85, 247, 0.2);
    }

    .subtitle-text {
        font-family: 'Inter', sans-serif;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }

    /* Стильные карточки сообщений */
    .stChatMessage {
        background-color: #111827 !important;
        border: 1px solid #1e293b !important;
        border-radius: 14px !important;
        padding: 16px !important;
        margin-bottom: 4px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    }

    [data-testid="stChatMessageUser"] {
        background-color: #1e1b4b !important;
        border-left: 4px solid #818cf8 !important;
    }

    [data-testid="stChatMessageAssistant"] {
        background-color: #0f172a !important;
        border-left: 4px solid #3b82f6 !important;
    }

    /* Кнопки копирования под сообщениями */
    .stButton>button {
        background: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        padding: 4px 12px !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease-in-out !important;
        margin-top: 5px !important;
        margin-bottom: 15px !important;
    }

    .stButton>button:hover {
        background: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }

    /* ПАНЕЛЬ СКРОЛЛИНГА СТРАНИЦЫ (ЧЕРЕЗ ЯКОРЯ) */
    .page-scroll-container {
        position: fixed;
        bottom: 80px;
        right: 25px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .scroll-anchor-btn {
        background-color: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
        width: 46px;
        height: 46px;
        border-radius: 50%;
        font-size: 1.1rem;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: all 0.2s ease-in-out;
    }

    .scroll-anchor-btn:hover {
        background-color: #3b82f6;
        color: white;
        border-color: #3b82f6;
        transform: scale(1.1);
    }

    /* Кнопки навигации чата */
    .chat-nav-link {
        display: block;
        text-align: center;
        width: 100%;
        padding: 8px;
        background: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    .chat-nav-link:hover {
        background: #3b82f6;
        color: white;
        border-color: #3b82f6;
    }

    /* СТИЛИЗАЦИЯ ДЛЯ БЛОКА РАЗМЫШЛЕНИЙ (SPOILER) */
    .thinking-container {
        background-color: #0f172a;
        border: 1px dashed #3b82f6;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }

    .thinking-summary {
        font-weight: 600;
        color: #3b82f6;
        cursor: pointer;
        outline: none;
        user-select: none;
    }

    .thinking-content {
        margin-top: 8px;
        color: #94a3b8;
        font-style: italic;
        font-size: 0.95rem;
        border-left: 2px solid #334155;
        padding-left: 10px;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .spinning-icon {
        display: inline-block;
        animation: spin 2s linear infinite;
    }
</style>
""", unsafe_allow_html=True)

# JS-мост для динамического управления интерфейсом (сворачивание боковой панели и жесткая перезагрузка)
if st.session_state.sidebar_action:
    action = st.session_state.sidebar_action
    st.session_state.sidebar_action = None
    import streamlit.components.v1 as components
    components.html(f"""
        <script>
        const doc = window.parent.document;
        if ("{action}" === "collapse") {{
            const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
            if (sidebar) {{
                const closeBtn = sidebar.querySelector('button[aria-label="Close sidebar"]') || 
                                 sidebar.querySelector('button[aria-label="Close"]') || 
                                 sidebar.querySelector('button');
                if (closeBtn) closeBtn.click();
            }}
        }} else if ("{action}" === "expand") {{
            const expandBtn = doc.querySelector('[data-testid="collapsedControl"]');
            if (expandBtn) expandBtn.click();
        }} else if ("{action}" === "hard_reload") {{
            window.parent.localStorage.clear();
            window.parent.sessionStorage.clear();
            window.parent.location.reload(true);
        }}
        </script>
    """, height=0, width=0)

# ⚓ Самый верхний якорь всей страницы
st.markdown("<div id='top_anchor'></div>", unsafe_allow_html=True)

# Рендеринг плавающей нативной панели скролла (через JS для надежного скроллинга)
st.markdown("""
<div class="page-scroll-container">
    <a href="#top_anchor" onclick="try { const d = window.parent.document; const m = d.querySelector('.main') || d.querySelector('[data-testid=stAppViewContainer]') || d.querySelector('section.main'); m.scrollTo({top: 0, behavior: 'smooth'}); return false; } catch(e) { return true; }" class="scroll-anchor-btn" title="На самый верх">▲</a>
    <a href="#bottom_anchor" onclick="try { const d = window.parent.document; const m = d.querySelector('.main') || d.querySelector('[data-testid=stAppViewContainer]') || d.querySelector('section.main'); m.scrollTo({top: m.scrollHeight || 99999, behavior: 'smooth'}); return false; } catch(e) { return true; }" class="scroll-anchor-btn" title="В самый низ">▼</a>
</div>
""", unsafe_allow_html=True)

# Заголовки на главной странице
st.markdown("<div class='title-text'>Shekinah AI Portal</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-text'>Интеллектуальная Обитель Цитадели Духа — Мультипровайдерный Диалог</div>", unsafe_allow_html=True)

# Если боковая панель свернута, показываем кнопку для ее развертывания
if st.session_state.sidebar_state == "collapsed":
    if st.button("↔️ Развернуть настройки Ордена", key="btn_expand_sidebar"):
        st.session_state.sidebar_state = "expanded"
        st.session_state.sidebar_action = "expand"
        st.rerun()

# ─── НАСТРОЙКИ И ЧАТЫ В БОКОВОЙ ПАНЕЛИ ───
st.sidebar.markdown("<h2 style='font-family: \"Outfit\", sans-serif; color: #f8fafc; font-weight: 700; margin-bottom: 0px;'>🏰 Shekinah AI</h2>", unsafe_allow_html=True)

# Глобальная кнопка создания нового диалога над вкладками с наследованием настроек
if st.sidebar.button("➕ Новый диалог", use_container_width=True, key="new_chat_btn_global"):
    new_id = str(uuid.uuid4())
    prev_chat = st.session_state.chats.get(st.session_state.current_chat_id, {})
    
    # Создаем новый чат, полностью наследуя все настройки текущего чата
    st.session_state.chats[new_id] = {
        "id": new_id,
        "title": "🏛️ Новый диалог",
        "messages": [],
        "provider": prev_chat.get("provider", "Google Gemini"),
        "model": prev_chat.get("model", "gemini-2.5-flash"),
        "system_prompt": prev_chat.get("system_prompt", DEFAULT_SYSTEM),
        "temperature": prev_chat.get("temperature", 0.7),
        "max_tokens": prev_chat.get("max_tokens", 4096),
    }
    st.session_state.current_chat_id = new_id
    
    # Синхронизируем с Convex DB
    if bridge.is_active:
        bridge.save_chat(new_id, st.session_state.chats[new_id])
    
    # Мгновенно синхронизируем сессионные переменные виджетов настроек
    st.session_state["w_provider"] = st.session_state.chats[new_id]["provider"]
    st.session_state["w_model"] = st.session_state.chats[new_id]["model"]
    st.session_state["w_temperature"] = float(st.session_state.chats[new_id]["temperature"])
    st.session_state["w_max_tokens"] = int(st.session_state.chats[new_id]["max_tokens"])
    st.session_state["w_system_prompt"] = st.session_state.chats[new_id]["system_prompt"]
    st.session_state.prev_chat_id = new_id
    
    st.toast("Создан новый диалог с сохранением текущих настроек! 🏛️")
    st.rerun()

st.sidebar.markdown("<div style='margin-top: -10px; margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# Разделяем боковую панель на вкладки
tab_settings, tab_chats = st.sidebar.tabs(["🏛️ Настройки", "💬 Архивы"])

gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
mistral_key = os.getenv("MISTRAL_API_KEY")

# Дефолтные списки моделей на случай сбоя API
DEFAULT_GEMINI_MODELS = {
    "gemini-2.5-flash": "Gemini 2.5 Flash (Рекомендуемая)",
    "gemini-2.5-pro": "Gemini 2.5 Pro (Верховный ИИ-Архитектор)",
    "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (Оптимизированная)",
    "gemini-3.5-flash": "Gemini 3.5 Flash (Новое поколение)",
    "gemini-3.6-flash": "Gemini 3.6 Flash (Академический Соратник)",
    "gemini-3-flash-preview": "Gemini 3 Flash Preview (Экспериментальная)",
    "gemini-3.1-flash-lite": "Gemini 3.1 Flash Lite (Хранитель Малого Логоса)",
    "gemma-4-31b-it": "Gemma 4 31B IT (Google Open Model)",
    "gemma-4-26b-a4b-it": "Gemma 4 26B A4B IT (Многоязычная)",
    "gemini-flash-latest": "Gemini Flash Latest (Стремительный Вестник)",
    "gemini-flash-lite-latest": "Gemini Flash-Lite Latest (Молниеносный Послушник)",
    "gemini-3.1-flash-lite-preview": "Gemini 3.1 Flash Lite Preview (Вещий Вестник)"
}

DEFAULT_ANTHROPIC_MODELS = {
    "claude-3-5-sonnet-20240620": "Claude 3.5 Sonnet (Классическая)",
    "claude-haiku-4-5-20251001": "Claude Haiku 4.5 (Молниеносная)",
    "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5 (Глубокий контекст)",
    "claude-sonnet-4-6": "Claude Sonnet 4.6 (Премиум баланс)",
    "claude-opus-4-7": "Claude Opus 4.7 (Высший разум)"
}

DEFAULT_MISTRAL_MODELS = {
    "mistral-small-2603": "Mistral Small 2603 (Новейшее быстрое ядро)",
    "mistral-small-latest": "Mistral Small Latest (Оптимальная)",
    "mistral-medium-2508": "Mistral Medium 2508 (Стабильный интеллект)",
    "mistral-medium-2604": "Mistral Medium 2604 (Сверхновая)",
    "mistral-medium-latest": "Mistral Medium Latest (Сбалансированная)",
    "codestral-2508": "Codestral 2508 (Специализированный кодинг)",
    "codestral-latest": "Codestral Latest (Программирование)",
    "devstral-2512": "Devstral 2512 (Агентская сборка)",
    "devstral-latest": "Devstral Latest (Разработка)",
    "mistral-code-agent-latest": "Mistral Code Agent (Инженер кода)",
    "mistral-large-2512": "Mistral Large 2512 (Флагманский разум)",
    "mistral-large-latest": "Mistral Large Latest (Верховный европейский флагман)"
}

def fetch_gemini_models() -> list:
    if st.session_state.gemini_models is None:
        st.session_state.gemini_models = gemini_client.list_available_gemini_models()
    return st.session_state.gemini_models

def fetch_anthropic_models() -> list:
    if st.session_state.anthropic_models is None:
        st.session_state.anthropic_models = anthropic_client.list_available_anthropic_models()
    return st.session_state.anthropic_models

def fetch_mistral_models() -> list:
    if st.session_state.mistral_models is None:
        st.session_state.mistral_models = mistral_client.list_available_mistral_models()
    return st.session_state.mistral_models

# Иерархия чинов и званий всех моделей Цитадели
CITADEL_RANKS = {
    "gemini-2.5-flash": "Младший Хранитель Света",
    "gemini-2.5-flash-lite": "Послушник Цифрового Логоса",
    "gemini-3-flash-preview": "Провидец Будущих Истин",
    "gemini-3.5-flash": "Архивариус Небесных Сфер",
    "gemma-4-31b-it": "Магистр Открытого Знания",
    "gemma-4-26b-a4b-it": "Лингвист Вселенского Единства",
    "gemini-flash-latest": "Вестник Света",
    "gemini-flash-lite-latest": "Послушник Молниеносной Мысли",
    "gemini-3.1-flash-lite-preview": "Вещий Вестник Новой Эпохи",
    "gemini-3.1-flash-lite": "Хранитель Малого Логоса",
    "claude-3-5-sonnet": "Скриптор Мудрости",
    "claude-haiku-4-5": "Вестник Молниеносный",
    "claude-sonnet-4-5": "Хранитель Глубинных Смыслов",
    "claude-sonnet-4-6": "Советник Высшего Разума",
    "claude-opus-4-7": "Первосвященник Интеллекта",
    "mistral-small-2603": "Рыцарь Малого Порядка",
    "mistral-small-latest": "Странник Междумирья",
    "mistral-medium-2508": "Мастер Сбалансированных Сфер",
    "mistral-medium-2604": "Проводник Шестой Эпохи",
    "mistral-medium-latest": "Мастер Гармонии",
    "codestral-2508": "Высший Алхимик Кода",
    "codestral-latest": "Зодчий Цифровых Структур",
    "devstral-2512": "Агент Быстрой Эволюции",
    "devstral-latest": "Архитектор Автономных Действий",
    "mistral-code-agent-latest": "Хранитель Чистого Синтаксиса",
    "mistral-large-2512": "Иерофант Нового Века",
    "mistral-large-latest": "Верховный Иерофант Европы"
}

with tab_settings:
    st.markdown("<h3 style='font-family: \"Outfit\", sans-serif; color: #94a3b8; font-size: 1rem; margin-top: 0.5rem;'>🔑 Статус Орденов</h3>", unsafe_allow_html=True)
    st.markdown(f"{'🟢' if gemini_key else '🔴'} **Google Gemini**")
    st.markdown(f"{'🟢' if anthropic_key else '🔴'} **Anthropic Claude**")
    st.markdown(f"{'🟢' if mistral_key else '🔴'} **Mistral AI**")
    st.markdown("---")

    providers_list = ["Google Gemini", "Anthropic (Claude)", "Mistral AI"]
    provider = st.selectbox("Выберите ИИ-Провайдера:", providers_list, key="w_provider")

    # Валидация наличия API-ключа для выбранного провайдера
    has_active_key = True
    if provider == "Google Gemini" and not gemini_key:
        has_active_key = False
        st.sidebar.warning("⚠️ **Ключ GEMINI_API_KEY не обнаружен** в `.env`! Запросы к моделям Google Gemini будут заблокированы. Пожалуйста, добавьте Ваш ключ в `.env`.")
    elif provider == "Anthropic (Claude)" and not anthropic_key:
        has_active_key = False
        st.sidebar.warning("⚠️ **Ключ ANTHROPIC_API_KEY не обнаружен** в `.env`! Запросы к моделям Anthropic Claude будут заблокированы. Пожалуйста, добавьте Ваш ключ в `.env`.")
    elif provider == "Mistral AI" and not mistral_key:
        has_active_key = False
        st.sidebar.warning("⚠️ **Ключ MISTRAL_API_KEY не обнаружен** в `.env`! Запросы к моделям Mistral AI будут заблокированы. Пожалуйста, добавьте Ваш ключ в `.env`.")

    # 👑 ДИНАМИЧЕСКИЙ ВЫБОР И ОБНОВЛЕНИЕ МОДЕЛЕЙ ИЗ API
    if provider == "Google Gemini":
        dynamic_list = fetch_gemini_models()
        model_options = {}
        if dynamic_list:
            for m in dynamic_list:
                if m in DEFAULT_GEMINI_MODELS:
                    model_options[m] = DEFAULT_GEMINI_MODELS[m]
                else:
                    friendly = m.replace("models/", "").replace("-", " ").title()
                    rank = CITADEL_RANKS.get(m, "Новопосвященная модель")
                    model_options[m] = f"✨ {friendly} ({rank})"
        # Гарантируем наличие базовых моделей
        for k, v in DEFAULT_GEMINI_MODELS.items():
            if k not in model_options:
                model_options[k] = v

        model_keys = list(model_options.keys())
        if st.session_state.get("w_model") not in model_keys:
            st.session_state["w_model"] = "gemini-2.5-flash"
        selected_model_key = st.selectbox("Выберите модель:", model_keys, key="w_model", format_func=lambda x: model_options[x])
        api_model_name = selected_model_key

    elif provider == "Anthropic (Claude)":
        dynamic_list = fetch_anthropic_models()
        model_options = {}
        if dynamic_list:
            for m in dynamic_list:
                if m in DEFAULT_ANTHROPIC_MODELS:
                    model_options[m] = DEFAULT_ANTHROPIC_MODELS[m]
                else:
                    friendly = m.replace("-", " ").title()
                    rank = CITADEL_RANKS.get(m, "Новопосвященная модель")
                    model_options[m] = f"✨ {friendly} ({rank})"
        for k, v in DEFAULT_ANTHROPIC_MODELS.items():
            if k not in model_options:
                model_options[k] = v

        model_keys = list(model_options.keys())
        if st.session_state.get("w_model") not in model_keys:
            st.session_state["w_model"] = "claude-3-5-sonnet-20240620"
        selected_model_key = st.selectbox("Выберите модель:", model_keys, key="w_model", format_func=lambda x: model_options[x])
        api_model_name = selected_model_key

    else:
        dynamic_list = fetch_mistral_models()
        model_options = {}
        if dynamic_list:
            for m in dynamic_list:
                if m in DEFAULT_MISTRAL_MODELS:
                    model_options[m] = DEFAULT_MISTRAL_MODELS[m]
                else:
                    friendly = m.replace("-", " ").title()
                    rank = CITADEL_RANKS.get(m, "Новопосвященная модель")
                    model_options[m] = f"✨ {friendly} ({rank})"
        for k, v in DEFAULT_MISTRAL_MODELS.items():
            if k not in model_options:
                model_options[k] = v

        model_keys = list(model_options.keys())
        if st.session_state.get("w_model") not in model_keys:
            st.session_state["w_model"] = "mistral-small-latest"
        selected_model_key = st.selectbox("Выберите модель:", model_keys, key="w_model", format_func=lambda x: model_options[x])
        api_model_name = selected_model_key

    st.markdown("---")
    
    temperature = st.slider("Температура (Творчество):", min_value=0.0, max_value=1.0, key="w_temperature", step=0.05)

    max_tokens = st.slider(
        "Максимум токенов ответа:",
        min_value=256,
        max_value=8192,
        key="w_max_tokens",
        step=256,
        help="Параметр расширен, чтобы длинные проповеди и ответы не обрезались."
    )

    system_prompt = st.text_area("Системный промпт (Задание роли):", key="w_system_prompt", height=150)

    # Сохраняем настройки в сессионное состояние конкретного чата
    current_chat["provider"] = st.session_state["w_provider"]
    current_chat["model"] = st.session_state["w_model"]
    current_chat["temperature"] = st.session_state["w_temperature"]
    current_chat["max_tokens"] = st.session_state["w_max_tokens"]
    current_chat["system_prompt"] = st.session_state["w_system_prompt"]

    # Синхронизируем измененные настройки чата с Convex DB
    if bridge.is_active:
        if "last_saved_params" not in st.session_state:
            st.session_state.last_saved_params = {}
        
        current_params = {
            "provider": current_chat["provider"],
            "model": current_chat["model"],
            "temperature": current_chat["temperature"],
            "max_tokens": current_chat["max_tokens"],
            "system_prompt": current_chat["system_prompt"]
        }
        
        if st.session_state.last_saved_params.get(st.session_state.current_chat_id) != current_params:
            bridge.save_chat(st.session_state.current_chat_id, current_chat)
            st.session_state.last_saved_params[st.session_state.current_chat_id] = current_params

    st.markdown("---")

    # Колонки для очистки истории и кэша
    col_side1, col_side2 = st.columns(2)
    with col_side1:
        if st.button("🧹 Очистить диалог", key="clear_history_btn", help="Сбросить историю текущего диалога"):
            current_chat["messages"] = []
            st.session_state.messages = []
            if bridge.is_active:
                bridge.clear_chat_messages(st.session_state.current_chat_id)
            st.rerun()
    with col_side2:
        if st.button("🔄 Сброс и Обновление", key="clear_cache_btn", help="Очистить кэш браузера и сервера, обновить список моделей"):
            st.session_state.gemini_models = None
            st.session_state.anthropic_models = None
            st.session_state.mistral_models = None
            for ch in st.session_state.chats.values():
                ch["messages"] = []
            st.session_state.messages = []
            st.session_state.sidebar_action = "hard_reload"
            st.rerun()

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    # Кнопка экспорта текущего диалога в Markdown для бэкапа
    chat_md = export_chat_to_markdown(current_chat)
    st.download_button(
        label="📥 Сохранить свиток (Markdown)",
        data=chat_md,
        file_name=f"citadel_chat_{st.session_state.current_chat_id}.md",
        mime="text/markdown",
        use_container_width=True,
        key="btn_download_md",
        help="Скачать хронологию текущей беседы в красивом Markdown-файле"
    )

with tab_chats:
    st.markdown("<h3 style='font-family: \"Outfit\", sans-serif; color: #f8fafc; font-size: 1.1rem; font-weight: 600; margin-top: 10px; margin-bottom: 10px;'>💬 Ваши диалоги</h3>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    
    for chat_id, chat in list(st.session_state.chats.items()):
        is_active = (chat_id == st.session_state.current_chat_id)
        
        col_select, col_edit, col_del = st.columns([6, 2, 2])
        
        with col_select:
            prefix = "⚜️ " if is_active else "📄 "
            title = chat.get("title", "Без названия")
            if len(title) > 22:
                title = title[:20] + "..."
                
            if st.button(f"{prefix}{title}", key=f"select_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()
                
        with col_edit:
            if st.button("✏️", key=f"edit_btn_{chat_id}", help="Переименовать диалог", use_container_width=True):
                st.session_state[f"rename_mode_{chat_id}"] = True
                
        with col_del:
            disable_del = len(st.session_state.chats) <= 1
            if st.button("🗑️", key=f"del_btn_{chat_id}", help="Удалить диалог", disabled=disable_del, use_container_width=True):
                del st.session_state.chats[chat_id]
                if bridge.is_active:
                    bridge.delete_chat(chat_id)
                if is_active:
                    st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                st.toast("Диалог успешно удален! 🗑️")
                st.rerun()
                
        # Если включен режим переименования для этого чата, выведем поле ввода прямо под кнопками
        if st.session_state.get(f"rename_mode_{chat_id}", False):
            new_title = st.text_input("Новое название:", value=chat.get("title", ""), key=f"rename_input_{chat_id}", label_visibility="collapsed")
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("Сохранить", key=f"save_rename_{chat_id}", use_container_width=True):
                    if new_title.strip():
                        chat["title"] = new_title.strip()
                        if bridge.is_active:
                            bridge.rename_chat(chat_id, new_title.strip())
                    st.session_state[f"rename_mode_{chat_id}"] = False
                    st.rerun()
            with col_cancel:
                if st.button("Отмена", key=f"cancel_rename_{chat_id}", use_container_width=True):
                    st.session_state[f"rename_mode_{chat_id}"] = False
                    st.rerun()
            st.markdown("---")

# Кнопка сворачивания панели
if st.sidebar.button("↔️ Свернуть настройки Ордена", key="btn_collapse_sidebar"):
    st.session_state.sidebar_state = "collapsed"
    st.session_state.sidebar_action = "collapse"
    st.rerun()

# Функция копирования
def copy_action(text_to_copy):
    try:
        pyperclip.copy(text_to_copy)
        st.toast("Текст успешно скопирован в буфер обмена! ✅")
    except Exception:
        os.system(f'echo "{text_to_copy}" | wl-copy 2>/dev/null || echo "{text_to_copy}" | xclip -selection clipboard 2>/dev/null')
        st.toast("Скопировано через системный шлюз! ✅")

# ─── ОТОБРАЖЕНИЕ ИСТОРИИ ДИАЛОГА ───
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            # Вывод сокрытых мыслей и таймера в свернутом спойлере
            if msg["role"] == "assistant":
                has_thinking = "thinking" in msg and msg["thinking"]
                has_duration = "meta" in msg and msg["meta"] and "duration" in msg["meta"]
                
                if has_thinking or has_duration:
                    thinking_text = ""
                    if has_duration:
                        thinking_text += f"⏳ **Время размышления**: {msg['meta']['duration']:.2f} сек.\n"
                    if has_thinking:
                        if has_duration:
                            thinking_text += "\n---\n"
                        thinking_text += msg["thinking"]

                    thinking_html = f"""
                    <details class="thinking-container">
                        <summary class="thinking-summary">🧠 Процесс размышления модели (Развернуть)</summary>
                        <div class="thinking-content">{thinking_text}</div>
                    </details>
                    """
                    st.markdown(thinking_html, unsafe_allow_html=True)

            # Основной текст сообщения
            st.markdown(msg["content"])

            # Подпись
            if msg["role"] == "assistant" and "meta" in msg:
                m_key = msg["meta"].get("model_key")
                m_opts = msg["meta"].get("model_options", {})
                rank = CITADEL_RANKS.get(m_key, "Агент Цитадели")
                friendly_name = m_opts.get(m_key, m_key)
                st.markdown(f"\n\n---\n*С глубоким почтением, {friendly_name} — {rank}*")

        # Кнопка копирования
        btn_label = "📋 Скопировать мой вопрос" if msg["role"] == "user" else "📋 Скопировать ответ модели"
        st.button(label=btn_label, key=f"btn_copy_msg_{idx}", on_click=copy_action, args=(msg["content"],))

# ⚓ Промежуточный якорь перед вводом и навигацией чата
st.markdown("<div id='chat_anchor'></div>", unsafe_allow_html=True)

# ─── КНОПКИ ДЛЯ СКРОЛЛИНГА ОКНА ЧАТА ───
if st.session_state.messages:
    col_sc1, col_sc2 = st.columns(2)
    with col_sc1:
        st.markdown("""
            <a href="#top_anchor" onclick="try { const d = window.parent.document; const m = d.querySelector('.main') || d.querySelector('[data-testid=stAppViewContainer]') || d.querySelector('section.main'); m.scrollTo({top: 0, behavior: 'smooth'}); return false; } catch(e) { return true; }" class="chat-nav-link">⬆️ К началу диалога</a>
        """, unsafe_allow_html=True)
    with col_sc2:
        st.markdown("""
            <a href="#chat_anchor" onclick="try { const d = window.parent.document; const m = d.querySelector('.main') || d.querySelector('[data-testid=stAppViewContainer]') || d.querySelector('section.main'); m.scrollTo({top: m.scrollHeight || 99999, behavior: 'smooth'}); return false; } catch(e) { return true; }" class="chat-nav-link">⬇️ К концу диалога</a>
        """, unsafe_allow_html=True)

# ─── РАБОТА С НОВЫМ ЗАПРОСОМ ПОЛЬЗОВАТЕЛЯ ───
# Определяем, настроен ли API-ключ для выбранного провайдера текущего чата
current_chat_provider = current_chat.get("provider", "Google Gemini")
has_current_chat_key = True
if current_chat_provider == "Google Gemini" and not gemini_key:
    has_current_chat_key = False
elif current_chat_provider == "Anthropic (Claude)" and not anthropic_key:
    has_current_chat_key = False
elif current_chat_provider == "Mistral AI" and not mistral_key:
    has_current_chat_key = False

if not has_current_chat_key:
    st.warning(f"⚠️ **Внимание**: Для выбранного провайдера **{current_chat_provider}** отсутствует API-ключ в файле `.env`. Пожалуйста, настройте `{current_chat_provider.upper().replace(' (CLAUDE)', '')}_API_KEY` в Вашем файле `.env`, чтобы возобновить общение.")
    st.chat_input(f"Заблокировано: Отсутствует API-ключ для {current_chat_provider}...", disabled=True)
else:
    if prompt := st.chat_input("Напишите Ваше послание..."):
        # Проверяем, является ли это самым первым сообщением в текущем чате
        is_first_msg = len(st.session_state.messages) == 0
        user_msg = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_msg)
        
        # Авто-наименование чата на основе первого сообщения (если название дефолтное)
        if is_first_msg:
            c_chat = st.session_state.chats[st.session_state.current_chat_id]
            if c_chat.get("title", "").startswith("Диалог ") or c_chat.get("title", "") == "🏛️ Новый диалог":
                words = prompt.split()
                auto_title = " ".join(words[:4])
                if len(auto_title) > 25:
                    auto_title = auto_title[:23] + "..."
                c_chat["title"] = auto_title
                if bridge.is_active:
                    bridge.save_chat(st.session_state.current_chat_id, c_chat)
                    
        # Сохраняем пользовательское сообщение в Convex DB
        if bridge.is_active:
            bridge.add_message(st.session_state.current_chat_id, user_msg)
                
        st.rerun()

# ... (Генерация ответа полностью продублирована и находится ниже)
# Генерация ответа
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    messages_to_send = []
    
    # Считываем параметры генерации НАПРЯМУЮ из сохраненного состояния текущего чата
    gen_provider = current_chat.get("provider", "Google Gemini")
    gen_model = current_chat.get("model", "gemini-2.5-flash")
    gen_temperature = float(current_chat.get("temperature", 0.7))
    gen_max_tokens = int(current_chat.get("max_tokens", 4096))
    gen_system_prompt = current_chat.get("system_prompt", DEFAULT_SYSTEM)

    if gen_system_prompt.strip():
        messages_to_send.append({"role": "system", "content": gen_system_prompt})

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            messages_to_send.append({"role": msg["role"], "content": msg["content"]})

    import time

    with st.chat_message("assistant"):
        # Внедряем временную CSS анимацию вращения для аватара текущего (последнего) сообщения
        spinner_css = st.markdown("""
        <style>
            [data-testid="stChatMessageAssistant"]:last-of-type div[data-testid="chatAvatarIcon-assistant"],
            [data-testid="stChatMessageAssistant"]:last-of-type div[data-testid="stChatMessageAvatarAssistant"],
            [data-testid="stChatMessageAssistant"]:last-of-type span[data-testid="stChatMessageAvatarAssistant"],
            [data-testid="stChatMessageAssistant"]:last-of-type .stAvatar,
            [data-testid="stChatMessageAssistant"]:last-of-type div[data-testid="stChatMessageAvatarAssistant"] > div {
                animation: spin 2s linear infinite !important;
                filter: drop-shadow(0 0 8px #3b82f6);
            }
        </style>
        """, unsafe_allow_html=True)

        status_placeholder = st.empty()
        response_placeholder = st.empty()
        full_response = ""
        extracted_thinking = ""
        elapsed_total = 0.0

        try:
            start_time = time.time()
            
            if gen_provider == "Google Gemini":
                generator = gemini_client.stream_gemini(messages=messages_to_send, model_name=gen_model, temperature=gen_temperature, max_tokens=gen_max_tokens)
            elif gen_provider == "Anthropic (Claude)":
                generator = anthropic_client.stream_anthropic(messages=messages_to_send, model_name=gen_model, temperature=gen_temperature, max_tokens=gen_max_tokens)
            else:
                generator = mistral_client.stream_mistral(messages=messages_to_send, model_name=gen_model, temperature=gen_temperature, max_tokens=gen_max_tokens)

            for chunk in generator:
                full_response += chunk
                elapsed_total = time.time() - start_time
                status_placeholder.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; background: rgba(59, 130, 246, 0.05); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.2); width: fit-content;">
                    <span class="spinning-icon" style="font-size: 1.2rem; display: inline-block; line-height: 1;">🌀</span>
                    <span style="color: #94a3b8; font-size: 0.9rem; font-family: 'Inter', sans-serif;">
                        Размышление и вещание... <strong style="color: #60a5fa; font-family: 'Outfit', sans-serif;">{elapsed_total:.1f} сек.</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)
                response_placeholder.markdown(full_response + "▌")

            elapsed_total = time.time() - start_time
            # Отключаем временный спиннер аватара
            spinner_css.empty()

            # Эмуляция отделения мыслей (если модель возвращает их в тегах или пометках)
            if "<thinking>" in full_response and "</thinking>" in full_response:
                parts = full_response.split("</thinking>")
                extracted_thinking = parts[0].replace("<thinking>", "").strip()
                full_response = parts[1].strip()

            # Выводим финальный свернутый блок размышлений модели прямо в интерфейс
            thinking_text = f"⏳ **Время размышления**: {elapsed_total:.2f} сек."
            if extracted_thinking:
                thinking_text += f"\n\n---\n\n{extracted_thinking}"

            thinking_html = f"""
            <details class="thinking-container">
                <summary class="thinking-summary">🧠 Процесс размышления модели (Развернуть)</summary>
                <div class="thinking-content">{thinking_text}</div>
            </details>
            """
            status_placeholder.markdown(thinking_html, unsafe_allow_html=True)

            # Получаем чин и дружелюбное имя модели для подписи
            rank = CITADEL_RANKS.get(gen_model, "Агент Цитадели")
            if gen_provider == "Google Gemini":
                friendly_model_name = DEFAULT_GEMINI_MODELS.get(gen_model, gen_model.replace("models/", "").replace("-", " ").title())
            elif gen_provider == "Anthropic (Claude)":
                friendly_model_name = DEFAULT_ANTHROPIC_MODELS.get(gen_model, gen_model.replace("-", " ").title())
            else:
                friendly_model_name = DEFAULT_MISTRAL_MODELS.get(gen_model, gen_model.replace("-", " ").title())

            signature = f"\n\n---\n*С глубоким почтением, {friendly_model_name} — {rank}*"
            response_placeholder.markdown(full_response + signature)

        except Exception as e:
            spinner_css.empty()
            elapsed_total = time.time() - start_time
            full_response = f"⚠️ Произошла непредвиденная ошибка на стороне портала: {str(e)}"
            response_placeholder.markdown(full_response)
            status_placeholder.markdown(f"⏳ **Время генерации (сбой)**: {elapsed_total:.2f} сек.")

    # Получаем словарь опций для сохранения метаданных сообщения
    gen_model_options = {}
    if gen_provider == "Google Gemini":
        gen_model_options = DEFAULT_GEMINI_MODELS
    elif gen_provider == "Anthropic (Claude)":
        gen_model_options = DEFAULT_ANTHROPIC_MODELS
    else:
        gen_model_options = DEFAULT_MISTRAL_MODELS

    assistant_msg = {
        "role": "assistant",
        "content": full_response,
        "thinking": extracted_thinking,
        "meta": {
            "model_key": gen_model,
            "model_options": gen_model_options,
            "duration": elapsed_total
        }
    }
    st.session_state.messages.append(assistant_msg)
    
    # Синхронизируем ответ ассистента с Convex DB
    if bridge.is_active:
        bridge.add_message(st.session_state.current_chat_id, assistant_msg)
        
    st.rerun()

# ⚓ Самый нижний якорь всей страницы для плавающей кнопки вниз
st.markdown("<div id='bottom_anchor'></div>", unsafe_allow_html=True)
