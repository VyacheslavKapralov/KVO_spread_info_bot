import asyncio

from aiogram.types import BotCommand, BotCommandScope
from aiogram.utils import executor, exceptions
from loguru import logger

from logs.start_log import log_telegram_bot
from settings import PARAMETERS
from telegram_api.connect_telegrambot import bot, dp
from telegram_api.handlers import (
    commands,
    get_spread_moex,
    get_atr_spread_moex,
    get_ema_spread_moex,
    get_funding,
    get_plot_spread_bb,
    get_sma_spread_moex,
)


@logger.catch()
async def set_bot_commands():
    try:
        scope = BotCommandScope()
        scope.type = "all_private_chats"
        await bot.delete_my_commands(scope)
        bot_commands = [BotCommand(command=cmd, description=desc) for cmd, desc in PARAMETERS['commands'].items()]
        await bot.set_my_commands(bot_commands)
    except exceptions.NetworkError as error:
        logger.error(f"Сетевая ошибка: {error} --- {error.with_traceback()}")
        await asyncio.sleep(5)
        await set_bot_commands()
    except Exception as error:
        logger.error(f"Произошла ошибка: {error} --- {error.with_traceback()}")


@logger.catch()
async def main(_):
    count = 5
    while count > 0:
        try:
            await set_bot_commands()
            commands.register_handlers_commands(dp)
            get_spread_moex.register_handlers_command_spread(dp)
            get_ema_spread_moex.register_handlers_command_ema(dp)
            get_funding.register_handlers_command_funding(dp)
            get_plot_spread_bb.register_handlers_command_bollinger_bands(dp)
            get_sma_spread_moex.register_handlers_command_sma(dp)
            get_atr_spread_moex.register_handlers_command_atr(dp)
            break
        except exceptions.NetworkError as error:
            logger.error(f"Сетевая ошибка: {error} --- {error.with_traceback()}")
            count -= 1
            await asyncio.sleep(5)
        except Exception as error:
            logger.error(f"Произошла ошибка: {error} --- {error.with_traceback()}")


if __name__ == '__main__':
    log_telegram_bot()
    executor.start_polling(dp, skip_updates=True, on_startup=main)
