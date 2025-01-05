import os

from loguru import logger
from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr

load_dotenv()

PARAMETERS = {
    'time_frame_minutes': '5m',
    'bollinger_period': 200,
    'bollinger_deviation': 2.0,
    'sma_period': 200,
    'ema_period': 200,
    'atr_period': 200,
    'commands': {
        'start': 'Запустить бота',
        'main_menu': 'Вернуться в главное меню',

        # 'spread': 'Прислать спред инструментов',
        # 'ema': 'Прислать EMA спреда',
        # 'sma': 'Прислать SMA спреда',
        # 'atr': 'Прислать ATR спреда',
        # 'plot_bb': 'Прислать график спреда с полосами Боллинджера',
        # 'funding': 'Прислать значение фандинга',
        # 'new_bot': 'Перезапустить бота',
        # 'chancel': 'Остановить бота',
        # 'help': 'Помощь в работе с ботом',
        # 'history': 'Вывести историю',
    }
}


class TinkoffSettings(BaseSettings):
    tinkoff_api: SecretStr = os.getenv('TINKOFF_API_KEY', None)


class BotSettings(BaseSettings):
    telebot_api: SecretStr = os.getenv('TELEGRAM_TOKEN', None)


if __name__ == '__main__':
    logger.info('Running settings.py')
