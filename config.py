import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("Проблема с загрузкой переменной окружения BOT_TOKEN.")
