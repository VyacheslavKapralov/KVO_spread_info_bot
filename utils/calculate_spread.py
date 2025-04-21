from loguru import logger

from tinkoff_investments.figi_for_ticker import searching_ticker_figi
from tinkoff_investments.last_price_tinkoff import get_last_price
from moex_api.get_data_moex import get_last_price_moex


@logger.catch()
async def calculate_spread(data: dict) -> float or None:
    last_prices = []
    for num in range(len(data['tickers'])):
        last_price = await get_price_for_figi(data['tickers'][num])
        if not last_price:
            return
        last_prices.append(last_price * float(data['coefficients'][num]))
    spread = last_prices[0]
    if data['spread_type'] == 'percent':
        for elem in last_prices[1:]:
            spread /= elem
        return round((spread - 1) * 100, 2)
    elif data['spread_type'] == 'money':
        for elem in last_prices[1:]:
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
