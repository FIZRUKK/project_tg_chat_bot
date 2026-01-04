from .middlewares import DbSessionMiddleware
from app.configs.database_config import async_session

all_middlewares = [
    DbSessionMiddleware(async_session),
    # Сюда будешь добавлять новые:
    # ThrottlingMiddleware(),
    # UserLoggingMiddleware(),
]