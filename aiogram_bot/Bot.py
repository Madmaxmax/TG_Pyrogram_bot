import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from log import logger
from aiogram_bot.handlers.handlers import reg_admin_handler


def reg_all_handlers(dp, queue):
    reg_admin_handler(dp, queue)


async def main(queue):
    logger.info("Starting bot")

    storage = MemoryStorage()

    bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(LoggingMiddleware())

    # Ловим сообщения
    reg_all_handlers(dp, queue)

    # start
    try:
        await dp.start_polling()
    finally:
        # Остановили бота и закрываем сессию
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

#
# if __name__ == '__main__':
#     try:
#         asyncio.run(main())
#     except (KeyboardInterrupt, SystemExit):
#         logger.error("Bot stopped!")
