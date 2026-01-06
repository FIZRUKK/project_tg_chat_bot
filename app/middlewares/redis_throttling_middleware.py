from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from redis.asyncio import Redis

class RedisThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, limit: int = 1):
        super().__init__()
        self.redis = redis
        self.limit = limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Update):
            return await handler(event, data)

        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        
        if not user:
            return await handler(event, data)

        user_id = user.id
        redis_key = f"throttle:{user_id}"

        # Проверяем Redis
        check = await self.redis.get(redis_key)
        if check:
            # Игнорируем спам
            return 

        # Записываем в Redis
        await self.redis.set(redis_key, "1", ex=self.limit)
        
        return await handler(event, data)