import asyncio
from loguru import logger
from app import tg_bot_manager

async def main():
    try:
        logger.info("Запуск приложения...")
        # Инициализируем и запускаем бота
        await tg_bot_manager.start_polling() 
    except Exception as e:
        logger.exception(f"Ошибка во время работы бота: {e}")
    finally:
        # Это сработает и при Ctrl+C, и при ошибке
        logger.info("Начинаю процесс остановки...")
        await tg_bot_manager.stop()
        logger.info("Все ресурсы успешно очищены")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Саму ошибку прерывания логируем коротко
        logger.warning("Приложение принудительно остановлено (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Приложение упало с критической ошибкой: {e}")