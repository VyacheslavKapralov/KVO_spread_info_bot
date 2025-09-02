import asyncio
import requests

from datetime import datetime, timedelta
from loguru import logger
from bs4 import BeautifulSoup


# "https://www.cbr.ru/scripts/XML_daily.asp" или "https://www.cbr-xml-daily.ru/latest.js"- курс валют

@logger.catch()
async def get_last_price_moex(ticker: str) -> list or None:
    ticker_data = await get_ticker_data(ticker)
    boards = ticker_data["boards"]["data"][0][1]
    engines = ticker_data["boards"]["data"][0][7]
    markets = ticker_data["boards"]["data"][0][5]
    url = f'https://iss.moex.com/iss/engines/{engines}/markets/{markets}/boards/{boards}/securities/{ticker}.json'
    count = 0
    while count < 5:
        try:
            response = requests.get(url)
            response.raise_for_status()
            response_json = response.json()
            columns = response_json["marketdata"]["columns"]
            for col, num in enumerate(columns):
                if markets == 'index' and col == 'CURRENTVALUE':
                    return response_json["marketdata"]["data"][0][num]
                if col == 'LAST':
                    return response_json["marketdata"]["data"][0][num]
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
        logger.debug(f"Повтор получения последней цены инструмента от МОЕХ. Количество попыток - {count}")
        await asyncio.sleep(5)


@logger.catch()
async def get_ticker_data(ticker: str) -> dict or None:
    url = f'https://iss.moex.com/iss/securities/{ticker}.json'
    count = 0
    while count < 5:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
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
async def get_fixing(ticker: str) -> float or None:
    date_finish = datetime.now()
    date_start = date_finish - timedelta(days=3)
    url = f'https://iss.moex.com/iss/history/engines/currency/markets/index/securities/{ticker}.json'
    params = {
        'from': date_start.strftime("%Y-%m-%d"),
        'till': date_finish.strftime("%Y-%m-%d")
    }
    count = 0
    while count < 5:
        try:
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            return response.json()['history']['data'][0][6]
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
        logger.debug(f"Повтор получения фиксинга инструмента от МОЕХ. Количество попыток - {count}")
        await asyncio.sleep(5)


@logger.catch()
async def get_key_rate_soup() -> float or None:
    url = 'https://www.cbr.ru/hd_base/keyrate/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table_wrapper = soup.find('div', class_='table-wrapper').text.strip()
        if table_wrapper:
            rows = table_wrapper.split()
            today = datetime.now().strftime('%d.%m.%Y')
            for num, row in enumerate(rows):
                if row == today:
                    return float(rows[num + 1].replace(",", "."))
    except ConnectionResetError as error:
        logger.error(f"Error - {error}: {error.with_traceback()}")
    except TimeoutError as error:
        logger.error(f"Error - {error}: {error.with_traceback()}")
    except requests.HTTPError as error:
        logger.error(
            f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
            f"Response: {error.response.text}"
        )


@logger.catch()
async def get_exchange_rate_soup(ticker: str) -> float or None:
    url = 'https://www.cbr.ru/currency_base/daily/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='data')
        if not table:
            return None
        rows = table.find_all('tr')[1:]
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 5:
                currency_code = cells[1].text.strip()
                if currency_code == ticker:
                    rate = cells[4].text.strip().replace(',', '.')
                    return float(rate)
        return None
    except ConnectionResetError as error:
        logger.error(f"Error - {error}: {error.with_traceback()}")
    except TimeoutError as error:
        logger.error(f"Error - {error}: {error.with_traceback()}")
    except requests.HTTPError as error:
        logger.error(
            f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
            f"Response: {error.response.text}"
        )


if __name__ == '__main__':
    logger.info('Running get_data_moex.py from module utils')
