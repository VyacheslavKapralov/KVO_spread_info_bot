import requests

from datetime import datetime, timedelta
from loguru import logger
from bs4 import BeautifulSoup


# "https://www.cbr.ru/scripts/XML_daily.asp" или "https://www.cbr-xml-daily.ru/latest.js"- курс валют

@logger.catch()
async def get_last_price_moex(ticker: str) -> float or None:
    ticker_data = get_ticker_data(ticker)
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
            for num in range(len(columns)):
                if markets == 'index' and columns[num] == 'CURRENTVALUE':
                    return float(response_json["marketdata"]["data"][0][num])
                if columns[num] == 'LAST':
                    return float(response_json["marketdata"]["data"][0][num])
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
        count += 1


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
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
        count += 1


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
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )


@logger.catch()
async def get_key_rate_soup() -> float:
    url = 'https://www.cbr.ru/hd_base/keyrate/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table_wrapper = soup.find('div', class_='table-wrapper').text.strip()
        if table_wrapper:
            rows = table_wrapper.split()
            today = datetime.now().strftime('%d.%m.%Y')
            for num in range(len(rows)):
                if rows[num] == today:
                    return float(rows[num + 1].replace(",", "."))
    except ConnectionResetError as error:
        logger.error(f"Error - {error}: {error.with_traceback()}")
    except requests.HTTPError as error:
        logger.error(
            f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
            f"Response: {error.response.text}"
        )


if __name__ == '__main__':
    logger.info('Running get_data_moex.py from module utils')
