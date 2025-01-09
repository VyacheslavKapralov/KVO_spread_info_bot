from datetime import timedelta
from loguru import logger

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now

from settings import TinkoffSettings
from tinkoff_investments.get_last_price import format_nano

TOKEN = TinkoffSettings().tinkoff_api.get_secret_value()


@logger.catch()
async def get_candles(candle_interval: str, figi: str, interval_day: int = 10) -> list:
    interval = await get_candle_interval(candle_interval)
    candles_list = []
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
                instrument_id=figi,
                from_=now() - timedelta(days=interval_day),
                to=now(),
                interval=interval,
        ):
            candles_list.append([
                f'{candle.time.year}-{candle.time.month}-{candle.time.day} '
                f'{candle.time.hour + 3}:{candle.time.minute}:{candle.time.second}',
                f'{candle.open.units}.{format_nano(candle.open.nano)}',
                f'{candle.high.units}.{format_nano(candle.high.nano)}',
                f'{candle.low.units}.{format_nano(candle.low.nano)}',
                f'{candle.close.units}.{format_nano(candle.close.nano)}',
                candle.volume
            ])
    return candles_list


@logger.catch()
async def get_candle_interval(candle_interval: str) -> CandleInterval:
    intervals = {
        '1m': CandleInterval.CANDLE_INTERVAL_1_MIN,
        '2m': CandleInterval.CANDLE_INTERVAL_2_MIN,
        '3m': CandleInterval.CANDLE_INTERVAL_3_MIN,
        '5m': CandleInterval.CANDLE_INTERVAL_5_MIN,
        '10m': CandleInterval.CANDLE_INTERVAL_10_MIN,
        '15m': CandleInterval.CANDLE_INTERVAL_15_MIN,
        '30m': CandleInterval.CANDLE_INTERVAL_30_MIN,
        '1h': CandleInterval.CANDLE_INTERVAL_HOUR,
        '2h': CandleInterval.CANDLE_INTERVAL_2_HOUR,
        '4h': CandleInterval.CANDLE_INTERVAL_4_HOUR,
        '1d': CandleInterval.CANDLE_INTERVAL_DAY,
        '1w': CandleInterval.CANDLE_INTERVAL_WEEK,
        '1M': CandleInterval.CANDLE_INTERVAL_MONTH,
        'UNSPECIFIED': CandleInterval.CANDLE_INTERVAL_UNSPECIFIED,
    }
    return intervals.get(candle_interval)


if __name__ == "__main__":
    logger.info('Running get_candles.py from module tinkoff_investments')
