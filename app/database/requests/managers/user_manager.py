from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from loguru import logger

from app import db_config
from ...models import User

class UserManager:
    @staticmethod
    def _get_now() -> datetime:
        """Возвращает текущее время по Москве без временной зоны для БД"""
        return datetime.now(db_config.tz).replace(tzinfo=None)

    async def add_user(self, session: AsyncSession, user_data: dict) -> bool:
        """
        Добавляет нового пользователя в базу данных.
        
        Ожидаемая структура user_data:
        {
            'tg_id': int,      # ID пользователя в Telegram (BigInt)
            'full_name': str,  # Полное имя (до 128 символов)
            'username': str    # Юзернейм (до 32 символов, может быть None)
        }
        """
        tg_id = user_data.get('tg_id')
        full_name = user_data.get('full_name')

        # Базовая валидация обязательных полей перед обращением к БД
        if not tg_id or not full_name:
            logger.error("Не удалось добавить пользователя: отсутствуют tg_id или full_name")
            return False

        try:
            # Создаем объект модели User
            new_user = User(
                tg_id=tg_id,
                full_name=full_name,
                username=user_data.get('username'),
                registered_at=self._get_now()
            )

            session.add(new_user)
            
            # Фиксируем изменения в базе
            await session.commit()
            
            logger.info(f"Пользователь {tg_id} успешно зарегистрирован в системе")
            return True

        except IntegrityError:
            # Срабатывает, если нарушена уникальность tg_id
            await session.rollback()
            logger.info(f"Пользователь {tg_id} уже существует в базе данных")
            return False
            
        except Exception as e:
            # Откатываем сессию при любой другой непредвиденной ошибке
            await session.rollback()
            logger.error(f"Ошибка при сохранении пользователя {tg_id}: {e}")
            return False