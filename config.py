# config.py

class Config:
    # Токен бота
    BOT_TOKEN = "7487465375:AAHCiPV8G0XU5lvhxIFQWPsnSI3O8ontWzw"

    # ID чатов
    CREATOR = 7561325825  # ID создателя бота
    PROMPTS_CHANNEL = -1002326305124  # ID канала для промптов
    LOG_CHAT = -1002309109516  # ID лог-чата
    SUPPORT_CHAT = -1002273538234  # ID чата поддержки
    MAIN_CHAT = None  # Основной чат (если есть)

    # Настройки безопасности для Google Generative AI
    SAFETY_SETTINGS = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        }
    ]

    # Другие настройки
    DEFAULT_USER_SETTINGS = {
        "reset": True,
        "pictures_in_dialog": True,
        "pictures_count": 5,
        "imageai": "sd"
    }

    # Параметры базы данных
    DB_FILE = "neuro_db.sqlite"