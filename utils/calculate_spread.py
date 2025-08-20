from loguru import logger

from alor_api.http_get_data import get_last_price_alor
from tinkoff_investments.figi_for_ticker import searching_ticker_figi
from tinkoff_investments.last_price_tinkoff import get_last_price_tinkoff
from moex_api.get_data_moex import get_last_price_moex


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


async def get_price_for_figi(ticker: str) -> float or None:
    figi = await searching_ticker_figi(ticker)
    if figi:
        last_price_tinkoff = await get_last_price_tinkoff(figi)
        if last_price_tinkoff:
            return float(last_price_tinkoff)
    if not figi:
        last_price_alor = await get_last_price_alor(ticker)
        if last_price_alor:
            return float(last_price_alor)
    last_price_moex = await get_last_price_moex(ticker)
    return float(last_price_moex)


if __name__ == '__main__':
    logger.info('Running calculate_spread.py from module utils')
