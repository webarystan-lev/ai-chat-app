import os
from mistralai.client import Mistral
from dotenv import load_dotenv
from typing import Generator, List, Dict, Optional
from providers.security import sanitize_markdown

# Загружаем ключи из .env
load_dotenv()

def ask_mistral(prompt: str, model_name: str = "mistral-large-latest", system_prompt: Optional[str] = None) -> str:
    """
    Отправляет запрос к Mistral AI и возвращает ответ (синхронно).
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return "Ошибка: не найден MISTRAL_API_KEY в .env"

    client = Mistral(api_key=api_key)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.complete(
        model=model_name,
        messages=messages
    )

    return sanitize_markdown(response.choices[0].message.content)


def stream_mistral(messages: List[Dict[str, str]], model_name: str, temperature: float, max_tokens: int, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
    """
    Отправляет историю сообщений к Mistral AI и транслирует ответ в реальном времени.
    Mistral не поддерживает роль 'system' — системный промпт вставляем в первое user-сообщение.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        yield "Ошибка: не найден MISTRAL_API_KEY в .env"
        return

    client = Mistral(api_key=api_key)

    api_messages = []
    system_injected = False
    
    for msg in messages:
        role = msg["role"]
        content = msg.get("content")
        
        # Пропускаем system-роль, её содержимое добавим к первому user-сообщению
        if role == "system":
            continue
            
        # Гарантируем, что content — всегда строка (не None)
        if content is None:
            content = ""
            
        # Внедряем системный промпт в первое user-сообщение
        if role == "user" and not system_injected and system_prompt:
            content = f"{system_prompt}\n\n{content}"
            system_injected = True
            
        api_messages.append({
            "role": role,
            "content": content
        })

    try:
        response = client.chat.stream(
            model=model_name,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        for chunk in response:
            delta = None
            if hasattr(chunk, 'data') and hasattr(chunk.data, 'choices') and chunk.data.choices:
                delta = chunk.data.choices[0].delta.content
            elif hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta.content
                
            if delta is not None:
                yield delta
    except Exception as e:
        yield f"\n[Ошибка генерации Mistral: {str(e)}]"


def list_available_mistral_models() -> List[str]:
    """
    Получает список доступных текстовых моделей от Mistral API.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return []
    try:
        client = Mistral(api_key=api_key)
        models_list = client.models.list()
        ignored_keywords = ["embed", "ocr", "moderation", "tts", "transcribe", "realtime"]
        return [
            m.id for m in models_list.data 
            if hasattr(m, 'id') and not any(k in m.id for k in ignored_keywords)
        ]
    except Exception:
        return []
