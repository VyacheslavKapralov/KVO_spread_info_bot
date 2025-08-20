import asyncio

from loguru import logger
from tinkoff.invest import Client
from tinkoff.invest.exceptions import RequestError

from  settings import TinkoffSettings

TOKEN = TinkoffSettings().tinkoff_api.get_secret_value()


@logger.catch()
async def get_last_price_tinkoff(figi: str) -> str or None:
    count = 0
    while count < 3:
        with Client(TOKEN) as client:
            try:
                response = client.market_data.get_order_book(figi=figi, depth=1)
                nano = await format_nano(response.last_price.nano)
                last_price = f'{response.last_price.units}.{nano}'
                return last_price
            except RequestError as error:
                logger.error(f"{error}: {error.code} - {error.metadata} --- {error.details}")
                count += 1
                await asyncio.sleep(5)
                continue


async def format_nano(nano: int) -> str:
    number_str = str(nano)
    while len(number_str) < 9:
        number_str = '0' + number_str
    return number_str


if __name__ == "__main__":
    logger.info('Running get_last_price.py from module tinkoff_investments')
