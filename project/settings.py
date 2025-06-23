import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Определяем движок для подключения к БД
engine = create_engine(
    f"postgresql+asyncpg://"
    f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@localhost:5432/payments_db"
)
