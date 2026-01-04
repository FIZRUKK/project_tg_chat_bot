import asyncio
from aiohttp import web
from typing import Optional
from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler, setup_application
)
from aiogram.client.bot import DefaultBotProperties

from app.routers import all_routers
from app.configs import tg_bot_config, db_config
from app.all_middlewares import all_middlewares



class TelegramBotManager:
    _instance: Optional['TelegramBotManager'] = None
    _bot: Optional[Bot] = None
    _dp: Optional[Dispatcher] = None
    _bot_name: Optional[str] = None
    _app: Optional[web.Application] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
    
    async def initialize(self):
        """Инициализация бота и диспетчера"""
        try:
            logger.info("Начинаю инициализацию бота...")
            
            self._bot = Bot(
                token=tg_bot_config.BOT_TOKEN,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML
                )
            )
            
            self._dp = Dispatcher()

            self._setup_middlewares()
            self._dp.include_routers(*all_routers)
            
            info = await self._bot.get_me()
            self._bot_name = info.username
            
            # Создаем aiohttp приложение
            self._app = web.Application()
            
            logger.info(
                "Бот успешно инициализирован", 
                extra={"bot_username": self._bot_name}
            )
            return self._bot, self._dp
            
        except Exception as e:
            logger.error("Ошибка при инициализации бота", exc_info=True)
            raise
    
    def _setup_middlewares(self):
        """Регистрирует все миддлвари из единого списка"""
        try:
            for middleware in all_middlewares:
                # Регистрируем каждую миддлварь на уровень update
                self._dp.update.middleware(middleware)
                logger.info(f"Миддлварь {middleware.__class__.__name__} подключена")
            logger.info(f"Успешно зарегистрировано миддлварей: {len(all_middlewares)}")
        except Exception as e:
            logger.error(f"Ошибка при регистрации миддлварей: {e}")
            raise

    async def setup_webhook(self):
        """Настройка webhook"""
        if not self.is_initialized():
            await self.initialize()
        
        try:
            # Устанавливаем webhook
            webhook_url = f"{tg_bot_config.WEBHOOK_URL}{tg_bot_config.WEBHOOK_PATH}"
            await self._bot.set_webhook(
                url=webhook_url,
                secret_token=tg_bot_config.WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            
            logger.info(
                "Webhook успешно установлен",
                extra={"webhook_url": webhook_url}
            )
            
        except Exception as e:
            logger.error("Ошибка при установке webhook", exc_info=True)
            raise
    
    async def start_webhook(self):
        """Запуск бота в режиме webhook"""
        if not self.is_initialized():
            await self.initialize()
        
        await self.setup_webhook()
        
        # Настраиваем обработчик webhook
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=self._dp,
            bot=self._bot,
            secret_token=tg_bot_config.WEBHOOK_SECRET,
        )
        
        # Регистрируем webhook путь
        webhook_requests_handler.register(self._app, path=tg_bot_config.WEBHOOK_PATH)
        
        # Настраиваем приложение
        setup_application(self._app, self._dp, bot=self._bot)
        
        # Запускаем aiohttp сервер
        runner = web.AppRunner(self._app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            tg_bot_config.WEBHOOK_HOST, 
            tg_bot_config.WEBHOOK_PORT
        )
        await site.start()
        
        logger.info("Telegram бот успешно запущен в режиме webhook!")
        logger.info(f"Имя пользователя бота: @{self._bot_name}")
        logger.info(f"Webhook URL: {tg_bot_config.WEBHOOK_URL}{tg_bot_config.WEBHOOK_PATH}")
        logger.info(f"Сервер запущен на {tg_bot_config.WEBHOOK_HOST}:{tg_bot_config.WEBHOOK_PORT}")
        logger.info("Готов принимать запросы через webhook")
        
        # Сохраняем runner для корректного завершения
        self._runner = runner
        
        # Бесконечное ожидание (удерживаем приложение запущенным)
        await asyncio.Future()
    
    async def start_polling(self):
        """Запуск бота в режиме polling (для разработки)"""
        if not self.is_initialized():
            await self.initialize()
        
        logger.info("Telegram бот успешно запущен в режиме polling!")
        logger.info(f"Имя пользователя бота: @{self._bot_name}")
        logger.info("Готов принимать запросы")

        await self._bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("Webhook очищен, ожидаю новые сообщения")
        logger.info("Начинаю процесс polling...")
        
        await self._dp.start_polling(self._bot, polling_timeout=10)
    
    async def stop(self):
        """Остановка бота и очистка всех ресурсов (БД, Сессии)"""
        logger.info("Запуск процесса остановки Telegram бота...")
        
        if self._bot:
            try:
                # 1. Удаляем webhook (если использовался)
                await self._bot.delete_webhook()
                logger.info("Webhook успешно удален")
            except Exception as e:
                logger.warning(f"Не удалось удалить webhook: {e}")

            # 2. Закрываем сессию бота (aiohttp клиент)
            await self._bot.session.close()
            try:
                await db_config.engine.dispose()
                logger.info("Все соединения с базой данных закрыты (engine disposed)")
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединений БД: {e}")

            # Обнуляем ссылки
            self._bot = None
            self._dp = None
            self._bot_name = None
            self._app = None
            
            logger.info("Telegram бот и сопутствующие ресурсы полностью остановлены")

    
    def get_bot(self) -> Optional[Bot]:
        """Возвращает текущий экземпляр бота"""
        return self._bot
    
    def get_dispatcher(self) -> Optional[Dispatcher]:
        """Возвращает текущий экземпляр диспетчера"""
        return self._dp
    
    def get_bot_name(self) -> Optional[str]:
        """Возвращает имя бота"""
        return self._bot_name
    
    def get_app(self) -> Optional[web.Application]:
        """Возвращает aiohttp приложение"""
        return self._app
    
    def is_initialized(self) -> bool:
        """Проверяет, инициализирован ли бот"""
        return self._bot is not None and self._dp is not None
    
    async def ensure_bot_initialized(self) -> Bot:
        """Гарантирует, что бот инициализирован, и возвращает его"""
        if not self.is_initialized():
            await self.initialize()
        return self._bot

# Создаем экземпляр менеджера (синглтон)
tg_bot_manager = TelegramBotManager()