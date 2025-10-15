from loguru import logger

from settings import VALID_TIMEFRAMES
from telegram_api.essence.answers_bot import bot_answers


@logger.catch()
def check_float(func):
    async def wrapper(message, state):
        try:
            if ',' in message.text:
                message.text = message.text.replace(',', '.')
            float(message.text)
            await func(message, state)
        except ValueError:
            await message.answer(bot_answers.check_float_answer(message.text))

    return wrapper


@logger.catch()
def check_int(func):
    async def wrapper(message, state):
        try:
            int(message.text)
            await func(message, state)
        except ValueError:
            await message.answer(bot_answers.check_int_answer(message.text))

    return wrapper


def check_min_max_line(func):
    async def wrapper(message, state):
        if ',' in message.text:
            message.text = message.text.replace(',', '.')
        async with state.proxy() as data:
            min_line = data['min_line']
        try:
            if float(message.text) > float(min_line):
                await func(message, state)
            else:
                await message.answer(bot_answers.maximum_line_test_failed(message.text, min_line))
        except ValueError:
            await message.answer(bot_answers.check_float_answer(message.text))

    return wrapper


@logger.catch()
def check_timeframe(func):
    async def wrapper(message, state):
        if message.text in VALID_TIMEFRAMES:
            await func(message, state)
        else:
            await message.answer(bot_answers.check_timeframe(VALID_TIMEFRAMES))

    return wrapper


if __name__ == '__main__':
    logger.info('Running decorators.py from module utils')
