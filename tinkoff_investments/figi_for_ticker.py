import asyncio

import pandas as pd

from loguru import logger

from tinkoff.invest import Client, SecurityTradingStatus
from tinkoff.invest.exceptions import RequestError
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.utils import quotation_to_decimal
from settings import TinkoffSettings

TOKEN = TinkoffSettings().tinkoff_api.get_secret_value()


@logger.catch()
async def searching_ticker_figi(ticker: str, call_once: bool = True) -> str or None:
    if not call_once:
        return None
    try:
        data = pd.read_csv('tinkoff_investments/ticker_to_figi.csv')
        figi_value = data.loc[data['ticker'] == ticker, 'figi']
        return figi_value.values[0]
    except (FileNotFoundError, IndexError):
        tickers_df = await get_figi_to_tinkoff()
        if tickers_df:
            tickers_df.to_csv('tinkoff_investments/ticker_to_figi.csv', mode='w')
            return await searching_ticker_figi(ticker, False)


@logger.catch()
async def get_figi_to_tinkoff() -> pd.DataFrame or None:
    count = 0
    while count < 3:
        try:
            with Client(TOKEN) as client:
                instruments: InstrumentsService = client.instruments
                tickers = []
                for method in ["shares", "bonds", "etfs", "currencies", "futures"]:
                    for item in getattr(instruments, method)().instruments:
                        tickers.append(
                            {
                                # "name": item.name,
                                "ticker": item.ticker,
                                "class_code": item.class_code,
                                "figi": item.figi,
                                "uid": item.uid,
                                "type": method,
                                "min_price_increment": quotation_to_decimal(item.min_price_increment),
                                "scale": 9 - len(str(item.min_price_increment.nano)) + 1,
                                "lot": item.lot,
                                "trading_status": str(SecurityTradingStatus(item.trading_status).name),
                                "api_trade_available_flag": item.api_trade_available_flag,
                                "currency": item.currency,
                                "exchange": item.exchange,
                                "buy_available_flag": item.buy_available_flag,
                                "sell_available_flag": item.sell_available_flag,
                                "short_enabled_flag": item.short_enabled_flag,
                                "klong": quotation_to_decimal(item.klong),
                                "kshort": quotation_to_decimal(item.kshort),
                            }
                        )
                tickers_df = pd.DataFrame(tickers)
                return tickers_df
        except RequestError as error:
            logger.error(f"{error}: {error.code} - {error.metadata} --- {error.details}")
            count += 1
            await asyncio.sleep(5)
            continue
    return None


if __name__ == "__main__":
    logger.info('Running get_figi_for_ticker.py from module tinkoff_investments')
