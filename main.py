import asyncio

from aiogram.types import BotCommand, BotCommandScope
from aiogram.utils import executor, exceptions
from loguru import logger

from database.database_bot import db
from logs.start_log import log_telegram_bot
from telegram_api.connect_telegrambot import bot, dp
from telegram_api.handlers import (
    commands,
    get_atr_spread_moex,
    get_ema_spread_moex,
    get_fair_price_futures,
    get_funding,
    get_plot_spread_bb,
    get_sma_spread_moex,
    get_spread_moex,
    get_alerts,
    admin_panel,
)


@logger.catch()
async def set_bot_commands():
    try:
        scope = BotCommandScope()
        scope.type = "all_private_chats"
        await bot.delete_my_commands(scope)
        commands_dict = await db.get_bot_commands()
        bot_commands = [BotCommand(command=cmd, description=desc) for cmd, desc in commands_dict.items()]
        await bot.set_my_commands(bot_commands)
    except exceptions.NetworkError as error:
        logger.error(f"Сетевая ошибка: {error}")
        await asyncio.sleep(5)
        await set_bot_commands()
    except Exception as error:
        logger.error(f"Ошибка при установке команд бота: {error}")
        default_commands = [
            BotCommand(command='start', description='Запустить бота'),
            BotCommand(command='main_menu', description='Вернуться в главное меню'),
            BotCommand(command='history', description='Вывести историю')
        ]
        await bot.set_my_commands(default_commands)


@logger.catch()
async def main(_):
    count = 5
    while count > 0:
        try:
            await db.create_tables()
            await set_bot_commands()
            await commands.register_handlers_commands(dp)
            await get_atr_spread_moex.register_handlers_command_atr(dp)
            await get_ema_spread_moex.register_handlers_command_ema(dp)
            await get_fair_price_futures.register_handlers_command_fair_price(dp)
            await get_funding.register_handlers_command_funding(dp)
            await get_plot_spread_bb.register_handlers_command_bollinger_bands(dp)
            await get_sma_spread_moex.register_handlers_command_sma(dp)
            await get_spread_moex.register_handlers_command_spread(dp)
            await get_alerts.register_handlers_alerts(dp)
            await admin_panel.register_handlers_admin_panel_commands(dp)
            logger.success('Бот запущен')
            break
        except exceptions.NetworkError as error:
            logger.error(f"Сетевая ошибка: {error} --- {error.with_traceback()}")
            count -= 1
            await asyncio.sleep(5)


if __name__ == '__main__':
    log_telegram_bot()
    try:
        executor.start_polling(dp, skip_updates=False, on_startup=main)
    except (ConnectionAbortedError, OSError, TimeoutError) as error:
        logger.error(f"Error: {error} --- {error.with_traceback()}")
    logger.warning('Прервана работа бота.')
