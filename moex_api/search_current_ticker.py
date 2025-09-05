import asyncio
import requests

from datetime import datetime

from loguru import logger

from database.database_bot import db


@logger.catch()
async def get_ticker(name: str) -> None or str:
    if len(name) != 2:
        return name
    current_date = datetime.now().date()
    expiration_months = await db.get_expiration_months()
    for key, val in expiration_months.items():
        month_num = int(val)
        if month_num < datetime.now().month:
            continue
        ticker = name + key + str(datetime.now().year)[-1]
        expiration = await get_expiration_date(ticker)
        if not expiration:
            continue
        expiration_date = datetime.strptime(expiration, "%Y-%m-%d").date()
        if current_date < expiration_date:
            return ticker
    next_year_short = str(datetime.now().year + 1)[-1]
    for key, val in expiration_months.items():
        ticker = name + key + next_year_short
        expiration = await get_expiration_date(ticker)
        if not expiration:
            continue
        expiration_date = datetime.strptime(expiration, "%Y-%m-%d").date()
        if current_date < expiration_date:
            return ticker
    return None


@logger.catch()
async def get_expiration_date(ticker: str) -> list or None:
    count = 0
    url = f"https://iss.moex.com/iss/securities/{ticker}.json"
    while count < 5:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()['description']['data'][5][2]
        except IndexError:
            logger.warning(f"Неудачный запрос даты экспирации инструмента: {ticker}")
            return
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except TimeoutError as error:
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
        count += 1
        logger.debug(f"Повтор получения данных инструмента от МОЕХ. Количество попыток - {count}")
        await asyncio.sleep(5)


@logger.catch()
async def get_all_futures_moex() -> list or None:
    count = 0
    url = 'https://iss.moex.com/iss/engines/futures/markets/forts/securities.json'
    while count < 5:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()["securities"]["data"]
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except TimeoutError as error:
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
        count += 1
        logger.debug(f"Повтор получения списка фьючерсов от МОЕХ. Количество попыток - {count}")
        await asyncio.sleep(5)


if __name__ == '__main__':
    logger.info('Running search_current_ticker.py from module utils')
