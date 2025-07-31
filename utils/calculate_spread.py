from loguru import logger

from tinkoff_investments.figi_for_ticker import searching_ticker_figi
from tinkoff_investments.last_price_tinkoff import get_last_price
from moex_api.get_data_moex import get_last_price_moex


@logger.catch()
async def calculate_spread(coefficients_list: list, spread_type: str, tickers_list: list) -> float or None:
    last_prices_list = []
    for num, ticker in enumerate(tickers_list):
        last_price = await get_price_for_figi(ticker)
        if not last_price:
            return
        last_prices_list.append(last_price * float(coefficients_list[num]))
    spread = last_prices_list[0]
    if spread_type == 'percent':
        for elem in last_prices_list[1:]:
            spread /= elem
        return round((spread - 1) * 100, 2)
    else:
        for elem in last_prices_list[1:]:
            spread -= elem
        return round(spread, 3)


@logger.catch()
async def get_price_for_figi(ticker: str) -> float or None:
    ticker = await searching_ticker_figi(ticker)
    last_price = await get_last_price(ticker)
    if not ticker or not last_price:
        return await get_last_price_moex(ticker)
    return float(last_price)


if __name__ == '__main__':
    logger.info('Running calculate_spread.py from module utils')
