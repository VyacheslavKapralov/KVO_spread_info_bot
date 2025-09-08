from loguru import logger

from settings import VALID_TIMEFRAMES
from telegram_api.essence.answers_bot import BotAnswers


@logger.catch()
def check_float(func):
    async def wrapper(message, state):
        try:
            if ',' in message.text:
                message.text = message.text.replace(',', '.')
            float(message.text)
            await func(message, state)
        except ValueError:
            await message.answer(BotAnswers.check_float_answer(message.text))
    return wrapper


@logger.catch()
def check_int(func):
    async def wrapper(message, state):
        try:
            int(message.text)
            await func(message, state)
        except ValueError:
            await message.answer(BotAnswers.check_int_answer(message.text))
    return wrapper


@logger.catch()
def check_timeframe(func):
    async def wrapper(message, state):
        if message.text in VALID_TIMEFRAMES:
            await func(message, state)
        else:
            await message.answer(BotAnswers.check_timeframe(VALID_TIMEFRAMES))
    return wrapper


if __name__ == '__main__':
    logger.info('Running decorators.py from module utils')
