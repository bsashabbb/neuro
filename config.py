import dotenv
import os

dotenv.load_dotenv()

class Config:
    # Токен бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    # ID чатов
    CREATOR = os.getenv('CREATOR') or 7561325825  # ID создателя бота
    PROMPTS_CHANNEL = os.getenv('PROMPTS_CHANNEL') or -1002326305124  # ID канала для промптов
    LOG_CHAT = os.getenv('LOG_CHAT') or -1002309109516  # ID лог-чата
    SUPPORT_CHAT = os.getenv('SUPPORT_CHAT') or -1002273538234  # ID чата поддержки
    MAIN_CHAT = os.getenv('MAIN_CHAT') or None  # Основной чат (если есть)

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
    DB_FILE = os.getenv('DB_FILE') or "neuro_db.sqlite"