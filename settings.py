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
    'coefficient_tool_1': 1,
    'coefficient_tool_2': 1,
    'futures_pairs': {
        'CNYRUBF': {
            'pair': ['CR', 'CNYRUBF'],
            'coefficient_1': 1,
            'coefficient_2': 1
        },
        'USDRUBF': {
            'pair': ['Si', 'USDRUBF'],
            'coefficient_1': 1,
            'coefficient_2': 1000
        },
        'EURRUBF': {
            'pair': ['Eu', 'EURRUBF'],
            'coefficient_1': 1,
            'coefficient_2': 1000
        },
        'GLDRUBF': {
            'pair': ['GD', 'GLDRUBF'],
            'coefficient_1': 1,
            'coefficient_2': 1
        },
        'GAZPF': {
            'pair': ['GZ', 'GAZPF'],
            'coefficient_1': 1,
            'coefficient_2': 100
        },
        'SBERF_R': {
            'pair': ['SR', 'SBERF'],
            'coefficient_1': 1,
            'coefficient_2': 100
        },
        'SBERF_P': {
            'pair': ['SP', 'SBERF'],
            'coefficient_1': 1,
            'coefficient_2': 100
        },
    },
    'stocks_pairs': {
        'TATN': 'TATNP',
        'MTLR': 'MTLRP',
        'RTKM': 'RTKMP',
        'SBER': 'SBERP',
    },
    'spots_pairs': {
        'EURUSD': 'ED',
    },
    'commands': {
        'start': 'Запустить бота',
        'main_menu': 'Вернуться в главное меню',

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
