import os

from loguru import logger
from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr

load_dotenv()

PARAMETERS = {
    'expiration_months': {
        'F': '01',
        'G': '02',
        'H': '03',
        'J': '04',
        'K': '05',
        'M': '06',
        'N': '07',
        'Q': '08',
        'U': '09',
        'V': '10',
        'X': '11',
        'Z': '12'
    },
    'time_frame_minutes': '1m',
    'bollinger_period': 200,
    'bollinger_deviation': 2.0,
    'sma_period': 200,
    'ema_period': 200,
    'atr_period': 200,
    'pairs': {
        'Валютные фьючерсы вечные к квартальным': (
            (('CR', 'CNYRUBF'), (1, 1)),
            (('Eu', 'EURRUBF'), (0.001, 1)),
            (('Si', 'USDRUBF'), (0.001, 1)),
        ),
        'Gold': (
            (('Si', 'GD', 'GLDRUBF'), (0.001, 1, 31.105)),
            (('USDRUBF', 'GD', 'GLDRUBF'), (1, 1, 31.105)),
        ),
        'Фьючерсы на акции вечные к квартальным': (
            (('GZ', 'GAZPF'), (0.01, 1)),
            (('MX', 'IMOEXF'), (0.1, 1)),
            (('SP', 'SBERF'), (0.01, 1)),
            (('SR', 'SBERF'), (0.01, 1)),
        ),
        'Синтетические валюты к квартальным фьючерсам': (
            (('Eu', 'Si', 'ED'), (1, 1, 1)),
            (('EURRUBF', 'USDRUBF', 'ED'), (1, 1, 1)),
            (('Si', 'CR', 'UC'), (0.001, 1, 1)),
            (('USDRUBF', 'CNYRUBF', 'UC'), (1, 1, 1)),
        ),
        'Акции': (
            (('TATN', 'TATNP'), (1, 1)),
            (('MTLR', 'MTLRP'), (1, 1)),
            (('RTKM', 'RTKMP'), (1, 1)),
            (('SBER', 'SBERP'), (1, 1)),
            (('ROSN', 'TATN'), (1, 1)),
            (('ROSN', 'NVTK'), (1, 1)),
            (('ROSN', 'GAZP'), (1, 1)),
            (('SNGS', 'SNGSP'), (1, 1)),
            (('GMKN', 'NLMK'), (1, 1)),
            (('GMKN', 'PLZL'), (1, 1)),
            (('GMKN', 'MAGN'), (1, 1)),
            (('LKOH', 'TATN'), (1, 1)),
            (('SBER', 'VTBR'), (1, 1)),
            (('SBER', 'MOEX'), (1, 1)),
            (('CHMF', 'NLMK'), (1, 1)),
            (('CHMF', 'MAGN'), (1, 1)),
        )
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
