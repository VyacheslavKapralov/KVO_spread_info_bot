import pandas as pd

from loguru import logger

from tinkoff.invest import Client, SecurityTradingStatus
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.utils import quotation_to_decimal

from settings import TinkoffSettings

TOKEN = TinkoffSettings().tinkoff_api.get_secret_value()

#
@logger.catch()
async def searching_ticker_figi(ticker: str) -> str or None:
    count = 2
    while count > 0:
        try:
            data = pd.read_csv('tinkoff_investments/ticker_to_figi.csv')
            figi_value = data.loc[data['ticker'] == ticker, 'figi']
            return figi_value.values[0]

        except FileNotFoundError:
            await get_figi_to_tinkoff().to_csv('tinkoff_investments/ticker_to_figi.csv', mode='w')
            continue

        except IndexError:
            await get_figi_to_tinkoff().to_csv('tinkoff_investments/ticker_to_figi.csv', mode='a')
            count -= 1
            continue

    logger.info(f'Не найден инструмент {ticker} в файле с инструментами биржи.')



@logger.catch()
async def get_figi_to_tinkoff() -> pd.DataFrame:
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
                        "min_price_increment": quotation_to_decimal(
                            item.min_price_increment
                        ),
                        "scale": 9 - len(str(item.min_price_increment.nano)) + 1,
                        "lot": item.lot,
                        "trading_status": str(
                            SecurityTradingStatus(item.trading_status).name
                        ),
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


if __name__ == "__main__":
    logger.info('Running get_figi_for_ticker.py from module tinkoff_investments')
