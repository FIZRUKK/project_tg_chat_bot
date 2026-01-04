import os
from dotenv import load_dotenv
import pytz
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)

# Загружаем переменные окружения
load_dotenv()

class DatabaseConfig:
    """Конфигурация подключения к базе данных MySQL (Async)"""
    
    # Работа с таймзоной (берем из .env или ставим Москву по умолчанию)
    tz_name = os.getenv("TZ", "Europe/Moscow")
    tz = pytz.timezone(tz_name)

    # Параметры подключения
    _user = os.getenv("DATABASE_USER")
    _password = os.getenv("DATABASE_PASSWORD")
    _hostname = os.getenv("DATABASE_HOSTNAME")
    _schema = os.getenv("DATABASE_SCHEMA")
    _port = int(os.getenv("DATABASE_PORT", 3306))

    # Сборка URL через объект URL (защита от спецсимволов в пароле/логине)
    url = URL.create(
        drivername="mysql+aiomysql",
        username=_user,
        password=_password,
        host=_hostname,
        port=_port,
        database=_schema,
        query={"charset": "utf8mb4"} # Поддержка эмодзи из ТГ
    )

    # Создание движка с "прод" настройками
    engine = create_async_engine(
        url=url,
        echo=False,           # Ставим True только при локальной отладке
        
        # ПАРАМЕТРЫ ПУЛА (Решают проблему "MySQL server has gone away")
        pool_size=10,         # Сколько соединений держать открытыми постоянно
        max_overflow=20,      # Сколько можно открыть сверх лимита при пиках
        
        pool_recycle=1800,    # Пересоздавать соединение каждые 30 минут (защита от таймаута MySQL)
        pool_pre_ping=True,   # Проверять "живое" ли соединение перед каждым запросом
        pool_use_lifo=True,   # Использовать последнее возвращенное соединение (оно самое свежее)
        
        pool_timeout=30,      # Сколько ждать свободного слота в пуле
        connect_args={
            "connect_timeout": 60  # Таймаут самого подключения к серверу
        }
    )

# Фабрика сессий
async_session = async_sessionmaker(
    bind=DatabaseConfig.engine, 
    class_=AsyncSession, 
    expire_on_commit=False  # Чтобы объекты не превращались в "тыкву" после коммита
)

# Синглтон конфига (на случай если понадобятся параметры в других частях кода)
db_config = DatabaseConfig()