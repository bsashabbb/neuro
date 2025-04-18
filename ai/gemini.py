import base64
import mimetypes
import httpx
from typing import Optional, List, Dict

async def gemini_gen(
    user_prompt: str,
    api_key: str,
    context: Optional[List[Dict]] = None,
    system_instruction: Optional[str] = None,
    image_path: Optional[str] = None,
    model_name: str = "gemini-2.0-flash-exp"
) -> str:
    """
    Асинхронная генерация контента через Gemini API с поддержкой:
    - Изображений (JPG/PNG/WEBP/HEIC)
    - Контекста диалога
    - Системных инструкций
    - Прокси-соединения
    """
    
    # Формирование тела запроса
    content_parts = [{"text": user_prompt}]
    
    if image_path:
        # Асинхронное чтение и кодирование изображения
        async with httpx.AsyncClient() as client:
            image_data = await client.read_file(image_path)
        
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or mime_type not in ['image/jpeg', 'image/png', 'image/webp', 'image/heic']:
            mime_type = 'image/jpeg'
        
        content_parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": base64.b64encode(image_data).decode("utf-8")
            }
        })
    
    # Сборка полного контекста
    messages = context.copy() if context else []
    messages.append({"role": "user", "parts": content_parts})
    
    payload = {
        "contents": messages,
        "systemInstruction": {"parts": [{"text": system_instruction}]} if system_instruction else None
    }
    
    # Настройки подключения
    proxy = "http://default:M3b3SZ5Zlv@5.78.57.199:5228"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    async with httpx.AsyncClient(
        proxy=proxy,
        timeout=httpx.Timeout(60.0)
    ) as client:
        response = await client.post(
            url,
            params={"key": api_key},
            json=payload
        )
        response.raise_for_status()
        
        response_data = response.json()
        
        # Извлечение ответа с проверкой структуры
        if "candidates" not in response_data:
            raise ValueError("Некорректный ответ API")
        
        return response_data["candidates"][0]["content"]["parts"][0]["text"]