import math
from datetime import datetime


from loguru import logger


from moex_api.get_data_moex import get_ticker_data, get_last_price_moex, get_key_rate_soup, get_fixing


async def calculate_futures_price(spot_price: float, interest_rate: float, expiration_date: str) -> float:
    current_date = datetime.now()
    expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
    days_to_expiration = (expiration_date - current_date).days
    futures_price = spot_price * math.exp((interest_rate / 100) * (days_to_expiration / 365))
    return futures_price


async def get_fair_price_futures(ticker: str) -> float or None:
    ticker_data = await get_ticker_data(ticker)
    spot_price = None
    if not ticker_data:
        return
    interest_rate = await get_key_rate_soup()
    if not interest_rate:
        return
    if ticker.startswith('CR'):
        spot_price = await get_fixing('CNYFIXME')
    elif ticker.startswith('Si'):
        spot_price = await get_fixing('USDFIXME')
    elif ticker.startswith('Eu'):
        spot_price = await get_fixing('EURFIXME')
    elif ticker.startswith('ED'):
        spot_price = await get_fixing('EURUSDFIXME')
    elif ticker.startswith('GD'):
        spot_price = await get_fixing('GOLDFIXME')
    elif ticker.startswith('SP'):
        spot_price = await get_last_price_moex('SBERP')
    elif ticker.startswith('SR'):
        spot_price = await get_last_price_moex('SBER')
    elif ticker.startswith('GZ'):
        spot_price = await get_last_price_moex('GAZP')
    elif ticker.startswith('MX'):
        spot_price = await get_last_price_moex('IMOEX')
    if not spot_price:
        return
    for elem in ticker_data['description']['data']:
        if elem[0] == 'LSTDELDATE':
            return round(await calculate_futures_price(spot_price, interest_rate, elem[2]), 2)


if __name__ == '__main__':
    logger.info('Running fair_price_futures.py from module utils')
