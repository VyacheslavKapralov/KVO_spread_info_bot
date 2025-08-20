import os

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings, SecretStr

load_dotenv()

PARAMETERS = {
    'expiration_months': {
        # 'F': '01',
        # 'G': '02',
        'H': '03',
        # 'J': '04',
        # 'K': '05',
        'M': '06',
        # 'N': '07',
        # 'Q': '08',
        'U': '09',
        # 'V': '10',
        # 'X': '11',
        'Z': '12'
    },
    'time_frame_minutes': '5m',
    'bollinger_period': 100,
    'bollinger_deviation': 2.0,
    'sma_period': 200,
    'ema_period': 200,
    'atr_period': 200,
    'signals': 3,
    'pairs': {
        'Валютные фьючерсы вечные к квартальным': (
            (('CR', 'CNYRUBF'), (1, 1)),
            (('Eu', 'EURRUBF'), (0.001, 1)),
            (('Si', 'USDRUBF'), (0.001, 1)),
        ),
        'Gold': (
            (('GL', 'GLDRUBF'), (1, 1)),
            (('GLDRUBF', 'Si', 'GD'), (31.1035, 0.001, 1)),
            (('GLDRUBF', 'USDRUBF', 'GD'), (31.1035, 1, 1)),
            (('GD', 'SV'), (1, 1))
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
            (('Eu', 'USDRUBF', 'ED'), (0.001, 1, 1)),
            (('EURRUBF', 'Si', 'ED'), (1, 0.001, 1)),
            (('Si', 'CR', 'UC'), (0.001, 1, 1)),
            (('Si', 'CNYRUBF', 'UC'), (0.001, 1, 1)),
            (('USDRUBF', 'CR', 'UC'), (1, 1, 1)),
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
        'history': 'Вывести историю',

        # 'help': 'Помощь в работе с ботом',
    }
}


class TinkoffSettings(BaseSettings):
    tinkoff_api: SecretStr = os.getenv('TINKOFF_API_KEY', None)


class AlorSettings(BaseSettings):
    alor_refresh_token: SecretStr = os.getenv('ALOR_REFRESH_TOKEN', None)
    alor_access_token: SecretStr = os.getenv('ALOR_ASSET_TOKEN', None)


class BotSettings(BaseSettings):
    telebot_api: SecretStr = os.getenv('TELEGRAM_TOKEN', None)


if __name__ == '__main__':
    logger.info('Running settings.py')
