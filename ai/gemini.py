import base64
import mimetypes
import httpx
from io import BytesIO
from typing import Optional, List, Dict, Tuple

async def gemini_gen(
    user_prompt: str,
    api_key: str,
    context: Optional[List[Dict]] = None,
    system_instruction: Optional[str] = None,
    image_bytes_io: Optional[BytesIO] = None,
    model_name: str = "gemini-2.0-flash-exp"
) -> Tuple[str, List[Dict]]:
    """
    Асинхронная генерация с сохранением изображений в контексте
    Возвращает ответ и обновленный контекст
    """
    
    # Формируем части контента
    content_parts = [{"text": user_prompt}]
    
    if image_bytes_io:
        # Определяем MIME-тип по сигнатуре файла
        header = image_bytes_io.read(4)
        image_bytes_io.seek(0)
        
        mime_type = "image/jpeg"  # значение по умолчанию
        if header.startswith(b'\x89PNG'):
            mime_type = "image/png"
        elif header.startswith(b'\xff\xd8'):
            mime_type = "image/jpeg"
        elif header.startswith(b'RIFF') and image_bytes_io.read(8)[4:8] == b'WEBP':
            mime_type = "image/webp"
        elif header.startswith(b'heic'):
            mime_type = "image/heic"
        
        image_bytes_io.seek(0)
        image_data = image_bytes_io.read()
        
        content_parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": base64.b64encode(image_data).decode("utf-8")
            }
        })

    # Собираем полный контекст
    updated_context = context.copy() if context else []
    updated_context.append({
        "role": "user",
        "parts": content_parts
    })

    # Формируем тело запроса
    payload = {
        "contents": updated_context,
        "systemInstruction": {"parts": [{"text": system_instruction}]} if system_instruction else None
    }

    proxy = "http://default:M3b3SZ5Zlv@5.78.57.199:5228"

    # Отправка запроса (ваш код прокси)
    async with httpx.AsyncClient(proxy=proxy, timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent",
            params={"key": api_key},
            json=payload
        )
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data.get("candidates"):
            raise ValueError("API response structure error")

        # Добавляем ответ модели в контекст
        model_response = response_data["candidates"][0]["content"]["parts"][0]["text"]
        updated_context.append({
            "role": "model",
            "parts": [{"text": model_response}]
        })

        return model_response, updated_context