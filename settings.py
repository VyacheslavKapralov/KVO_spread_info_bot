import os

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseSettings, SecretStr

load_dotenv()

EXPIRATION_MONTHS = {
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
}
VALID_TIMEFRAMES = [
    '1m',
    '2m',
    '3m',
    '5m',
    '10m',
    '15m',
    '30m',
    '1h',
    '2h',
    '4h',
    '1d',
    '1w',
    '1M']
TECHNICAL_SETTINGS = [
    'time_frame_minutes',
    'bollinger_period',
    'bollinger_deviation',
    'sma_period',
    'ema_period',
    'atr_period',
    'signals'
]
CURRENCY_ABBREVIATIONS = {
    'Si': 'USD',
    'CNY': 'CNY',
    'Eu': 'EUR',
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
