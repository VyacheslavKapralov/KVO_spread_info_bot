import math
from datetime import datetime

from loguru import logger

from moex_api.get_data_moex import get_key_rate_soup, get_exchange_rate_soup, get_ticker_data
from utils.calculate_spread import get_price_for_figi, calculate_spread, calculate_fair_spread

CURRENCY_ABBREVIATIONS = {
    'Si': 'USD',
    'CNY': 'CNY',
    'Eu': 'EUR',
}


async def calculate_futures_price(spot_price: float, interest_rate: float, expiration_date: str) -> float or None:
    current_date = datetime.now()
    expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
    days_to_expiration = (expiration_date - current_date).days
    futures_price = spot_price * math.exp((interest_rate / 100) * (days_to_expiration / 365))
    return futures_price


async def get_fair_price_futures_currency(ticker_data: dict) -> float or None:
    if not ticker_data:
        return None
    spot_price, expiration_date = None, None
    interest_rate = await get_key_rate_soup()
    for elem in ticker_data["description"]["data"]:
        if spot_price and expiration_date:
            break
        if elem[0] == 'LSTDELDATE':
            expiration_date = elem[2]
        elif elem[0] == 'ASSETCODE' and len(elem[2]) < 4:
            spot_price = await get_exchange_rate_soup(CURRENCY_ABBREVIATIONS.get(elem[2]))
        elif elem[0] == 'ASSETCODE' and len(elem[2]) > 3:
            break
    if spot_price and expiration_date and interest_rate:
        return round(await calculate_futures_price(spot_price, interest_rate, expiration_date), 2)
    return None


async def get_fair_spread_futures_currency(tickers: list, spread_type: str) -> float:
    prices = []
    for ticker in tickers:
        ticker_data = await get_ticker_data(ticker)
        for elem in ticker_data["description"]["data"]:
            if elem[0] == 'TYPE' and elem[2] == 'futures':
                fair_price = await get_fair_price_futures_currency(ticker_data)
                if fair_price:
                    prices.append(fair_price)
                else:
                    last_price = await get_price_for_figi(ticker)
                    prices.append(last_price)
    return await calculate_fair_spread(prices, spread_type)


if __name__ == '__main__':
    logger.info('Running fair_price_futures.py from module utils')
