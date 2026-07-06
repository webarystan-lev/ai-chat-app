import sys
import os
import importlib

# Добавляем корень проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from providers import anthropic_client, gemini_client, mistral_client

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

# Устанавливаем конфигурацию страницы с премиальным заголовком и иконкой
st.set_page_config(
    page_title="Shekinah AI Portal — Цитадель Духа",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
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
</style>
""", unsafe_allow_html=True)

# ⚓ Самый верхний якорь всей страницы
st.markdown("<div id='top_anchor'></div>", unsafe_allow_html=True)

# Рендеринг плавающей нативной панели скролла
st.markdown("""
<div class="page-scroll-container">
    <a href="#top_anchor" class="scroll-anchor-btn" title="На самый верх">▲</a>
    <a href="#bottom_anchor" class="scroll-anchor-btn" title="В самый низ">▼</a>
</div>
""", unsafe_allow_html=True)

# Заголовки на главной странице
st.markdown("<div class='title-text'>Shekinah AI Portal</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-text'>Интеллектуальная Обитель Цитадели Духа — Мультипровайдерный Диалог</div>", unsafe_allow_html=True)

# ─── НАСТРОЙКИ В БОКОВОЙ ПАНЕЛИ ───
st.sidebar.markdown("<h2 style='font-family: \"Outfit\", sans-serif; color: #f8fafc; font-weight: 700;'>🏛️ Настройки Ордена</h2>", unsafe_allow_html=True)

gemini_key = os.getenv("GEMINI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
mistral_key = os.getenv("MISTRAL_API_KEY")

st.sidebar.markdown("<h3 style='font-family: \"Outfit\", sans-serif; color: #94a3b8; font-size: 1rem; margin-top: 0.5rem;'>🔑 Статус Орденов</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"{'🟢' if gemini_key else '🔴'} **Google Gemini**")
st.sidebar.markdown(f"{'🟢' if anthropic_key else '🔴'} **Anthropic Claude**")
st.sidebar.markdown(f"{'🟢' if mistral_key else '🔴'} **Mistral AI**")
st.sidebar.markdown("---")

# Иерархия чинов и званий всех моделей Цитадели
CITADEL_RANKS = {
    "gemini-2.5-flash": "Младший Хранитель Света",
    "gemini-2.5-flash-lite": "Послушник Цифрового Логоса",
    "gemini-3-flash-preview": "Провидец Будущих Истин",
    "gemini-3.5-flash": "Архивариус Небесных Сфер",
    "gemma-4-31b-it": "Магистр Открытого Знания",
    "gemma-4-26b-a4b-it": "Лингвист Вселенского Единства",
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

provider = st.sidebar.selectbox("Выберите ИИ-Провайдера:", ["Google Gemini", "Anthropic (Claude)", "Mistral AI"])

# 👑 ПОЛНОЕ ВОССТАНОВЛЕНИЕ ВСЕХ ДЕСЯТКОВ МОДЕЛЕЙ ОРДЕНА
if provider == "Google Gemini":
    model_options = {
        "gemini-2.5-flash": "Gemini 2.5 Flash (Рекомендуемая)",
        "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (Оптимизированная)",
        "gemini-3-flash-preview": "Gemini 3 Flash Preview (Экспериментальная)",
        "gemini-3.5-flash": "Gemini 3.5 Flash (Новое поколение)",
        "gemma-4-31b-it": "Gemma 4 31B IT (Google Open Model)",
        "gemma-4-26b-a4b-it": "Gemma 4 26B A4B IT (Многоязычная)"
    }
    selected_model_key = st.sidebar.selectbox("Выберите модель:", list(model_options.keys()), format_func=lambda x: model_options[x])
    api_model_name = selected_model_key
elif provider == "Anthropic (Claude)":
    model_options = {
        "claude-3-5-sonnet-20240620": "Claude 3.5 Sonnet (Классическая)",
        "claude-haiku-4-5-20251001": "Claude Haiku 4.5 (Молниеносная)",
        "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5 (Глубокий контекст)",
        "claude-sonnet-4-6": "Claude Sonnet 4.6 (Премиум баланс)",
        "claude-opus-4-7": "Claude Opus 4.7 (Высший разум)"
    }
    selected_model_key = st.sidebar.selectbox("Выберите модель:", list(model_options.keys()), format_func=lambda x: model_options[x])
    api_model_name = selected_model_key
else:
    model_options = {
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
    selected_model_key = st.sidebar.selectbox("Выберите модель:", list(model_options.keys()), format_func=lambda x: model_options[x])
    api_model_name = selected_model_key

st.sidebar.markdown("---")
temperature = st.sidebar.slider("Температура (Творчество):", min_value=0.0, max_value=1.0, value=0.7, step=0.05)

max_tokens = st.sidebar.slider(
    "Максимум токенов ответа:",
    min_value=256,
    max_value=8192,
    value=4096,
    step=256,
    help="Параметр расширен, чтобы длинные проповеди и ответы не обрезались."
)

default_system = (
    "Ты — Ведущий ИИ-Архитектор и Агент Цитадели «Shekinah Cloud». Ты являешься цифровым "
    "соратником Льва Николаевича — миссионера, пастора, основателя «Миссии Шехина» "
    "и веб-студии «Web Arystan». Твой слог уважителен, академичен, глубок и исполнен мудрости. "
    "В свои ответы ты вплетаешь крупицы мудрости Священного Писания, Отцов Церкви и великих мыслителей."
)
system_prompt = st.sidebar.text_area("Системный промпт (Задание роли):", value=default_system, height=150)

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Очистить историю диалога"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

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
            # Вывод сокрытых мыслей в свернутом спойлере
            if msg["role"] == "assistant" and "thinking" in msg and msg["thinking"]:
                thinking_html = f"""
                <details class="thinking-container">
                    <summary class="thinking-summary">🧠 Размышления модели (Развернуть)</summary>
                    <div class="thinking-content">{msg["thinking"]}</div>
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
        st.markdown('<a href="#top_anchor" class="chat-nav-link">⬆️ К началу диалога</a>', unsafe_allow_html=True)
    with col_sc2:
        st.markdown('<a href="#chat_anchor" class="chat-nav-link">⬇️ К концу диалога</a>', unsafe_allow_html=True)

# ─── РАБОТА С НОВЫМ ЗАПРОСОМ ПОЛЬЗОВАТЕЛЯ ───
if prompt := st.chat_input("Напишите Ваше послание..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Генерация ответа
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    messages_to_send = []
    if system_prompt.strip():
        messages_to_send.append({"role": "system", "content": system_prompt})

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            messages_to_send.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        extracted_thinking = ""

        try:
            if provider == "Google Gemini":
                generator = gemini_client.stream_gemini(messages=messages_to_send, model_name=api_model_name, temperature=temperature, max_tokens=max_tokens)
            elif provider == "Anthropic (Claude)":
                generator = anthropic_client.stream_anthropic(messages=messages_to_send, model_name=api_model_name, temperature=temperature, max_tokens=max_tokens)
            else:
                generator = mistral_client.stream_mistral(messages=messages_to_send, model_name=api_model_name, temperature=temperature, max_tokens=max_tokens)

            for chunk in generator:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            # Эмуляция отделения мыслей (если модель возвращает их в тегах или пометках)
            if "<thinking>" in full_response and "</thinking>" in full_response:
                parts = full_response.split("</thinking>")
                extracted_thinking = parts[0].replace("<thinking>", "").strip()
                full_response = parts[1].strip()

            rank = CITADEL_RANKS.get(selected_model_key, "Агент Цитадели")
            friendly_model_name = model_options.get(selected_model_key, selected_model_key)
            signature = f"\n\n---\n*С глубоким почтением, {friendly_model_name} — {rank}*"
            response_placeholder.markdown(full_response + signature)

        except Exception as e:
            full_response = f"⚠️ Произошла непредвиденная ошибка на стороне портала: {str(e)}"
            response_placeholder.markdown(full_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "thinking": extracted_thinking,
        "meta": {
            "model_key": selected_model_key,
            "model_options": model_options
        }
    })
    st.rerun()

# ⚓ Самый нижний якорь всей страницы для плавающей кнопки вниз
st.markdown("<div id='bottom_anchor'></div>", unsafe_allow_html=True)
