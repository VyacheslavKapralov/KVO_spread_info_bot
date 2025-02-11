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
            'coefficients': [1, 1]
        },
        'EURRUBF': {
            'pair': ['Eu', 'EURRUBF'],
            'coefficients': [1, 1000]
        },
        'GAZPF': {
            'pair': ['GZ', 'GAZPF'],
            'coefficients': [1, 100]
        },
        'GLDRUBF': {
            'pair': ['Si', 'GD', 'GLDRUBF'],
            'coefficients': [0.001, 1, 31.105]
        },
        'IMOEXF': {
            'pair': ['MX', 'IMOEXF'],
            'coefficients': [1, 10]
        },
        'SBERF_P': {
            'pair': ['SP', 'SBERF'],
            'coefficients': [1, 100]
        },
        'SBERF_R': {
            'pair': ['SR', 'SBERF'],
            'coefficients': [1, 100]
        },
        'USDRUBF': {
            'pair': ['Si', 'USDRUBF'],
            'coefficients': [1, 100]
        },
    },
    'stocks_pairs': {
        'MTLR': 'MTLRP',
        'RTKM': 'RTKMP',
        'SBER': 'SBERP',
        'TATN': 'TATNP',
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
