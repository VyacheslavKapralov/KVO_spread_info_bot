from loguru import logger

from tinkoff_investments.figi_for_ticker import searching_ticker_figi
from tinkoff_investments.last_price_tinkoff import get_last_price
from moex_api.get_data_moex import get_last_price_moex


@logger.catch()
async def calculate_spread_money(ticker_1: str, ticker_2: str, coefficient_ticker_1: int, coefficient_ticker_2: int,
                                 accuracy: int = 3) -> float or None:
    try:
        return round(await get_price_for_figi(ticker_1) * coefficient_ticker_1 -
                     await get_price_for_figi(ticker_2) * coefficient_ticker_2, accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def calculate_spread_percent(ticker_1: str, ticker_2: str, coefficient_ticker_1: int, coefficient_ticker_2: int,
                                   accuracy: int = 2) -> float or None:
    try:
        return round((await get_price_for_figi(ticker_1) * coefficient_ticker_1 /
                      (await get_price_for_figi(ticker_2) * coefficient_ticker_2) - 1) * 100, accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def calculate_spread_ticker_3_money(ticker_1: str, ticker_2: str, ticker_3: str, coefficient_ticker_1: int,
                                          coefficient_ticker_2: int, coefficient_ticker_3: int,
                                          accuracy: int = 2) -> float or None:
    try:
        return round(await get_price_for_figi(ticker_1) * coefficient_ticker_1 *
                     await get_price_for_figi(ticker_2) * coefficient_ticker_2 / coefficient_ticker_3 -
                     await get_price_for_figi(ticker_3), accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def calculate_spread_ticker_3_percent(ticker_1: str, ticker_2: str, ticker_3: str, coefficient_ticker_1: int,
                                            coefficient_ticker_2: int, coefficient_ticker_3: int,
                                            accuracy: int = 2) -> float or None:
    try:
        return round((await get_price_for_figi(ticker_1) * coefficient_ticker_1 *
                      await get_price_for_figi(ticker_2) * coefficient_ticker_2 /
                      (await get_price_for_figi(ticker_3) * coefficient_ticker_3) - 1) * 100, accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def get_price_for_figi(ticker: str) -> float or None:
    ticker = await searching_ticker_figi(ticker)
    last_price = await get_last_price(ticker)
    if not ticker or not last_price:
        return await get_last_price_moex(ticker)
    return float(last_price)


@logger.catch()
async def calculate_spread(data: dict) -> str or None:
    if len(data['tickers']) == 3 and data['tickers'][3] == 'GLDRUBF':
        if data['spread_type'] == 'percent':
            spread = await calculate_spread_ticker_3_percent(
                data['tickers'][0],
                data['tickers'][1],
                data['tickers'][2],
                data['coefficients'][0],
                data['coefficients'][1],
                data['coefficients'][2]
            )
            return spread
        elif data['spread_type'] == 'money':
            spread = await calculate_spread_ticker_3_money(
                data['tickers'][0],
                data['tickers'][1],
                data['tickers'][2],
                data['coefficients'][0],
                data['coefficients'][1],
                data['coefficients'][2]
            )
            return spread
    if data['spread_type'] == 'percent':
        spread = await calculate_spread_percent(data['tickers'][0], data['tickers'][1], data['coefficients'][0],
                                                data['coefficients'][1])
        return spread
    elif data['spread_type'] == 'money':
        spread = await calculate_spread_money(data['tickers'][0], data['tickers'][1], data['coefficients'][0],
                                                data['coefficients'][1])
        return spread


if __name__ == '__main__':
    logger.info('Running calculate_spread.py from module utils')
