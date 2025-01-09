from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers


@logger.catch()
def check_float(func):
    async def wrapper(message, state):
        try:
            _ = float(message.text)
            await func(message, state)
        except ValueError:
            await message.answer(BotAnswers.check_float_answer(message.text))
    return wrapper


@logger.catch()
def check_int(func):
    async def wrapper(message, state):
        try:
            _ = int(message.text)
            await func(message, state)
        except ValueError:
            await message.answer(BotAnswers.check_int_answer(message.text))
    return wrapper


if __name__ == '__main__':
    logger.info('Running decorators.py from module utils')
