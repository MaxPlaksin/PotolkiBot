import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_PATH = os.getenv('DB_PATH')

# Для диагностики — можно удалить позже
print(f"BOT_TOKEN: {BOT_TOKEN}")
print(f"DB_PATH: {DB_PATH}")
