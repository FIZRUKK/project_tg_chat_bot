from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..keyboards import start_keyboard
from ..texts import start_text
from ...database import db_manager

start = Router()

@start.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    await message.answer(
        start_text.welcome_message_text
    )

    result = await db_manager.users.add_user(
        session=session,
        user_data={
            "tg_id": message.from_user.id,
            "full_name": message.from_user.full_name,
            "username": message.from_user.username
        }
    )

    logger.debug(f"Регистрация пользователя {message.from_user.id} в БД: {result}")

@start.message()
async def coppy_handler(message: Message):
    await message.copy_to(
        chat_id=message.from_user.id,
        reply_markup=await start_keyboard.main_menu()
    )