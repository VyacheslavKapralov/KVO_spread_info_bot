import asyncio
import aiohttp
import requests

import pandas as pd

from datetime import datetime, timedelta
from loguru import logger
from bs4 import BeautifulSoup

from settings import MOEX_COLUMNS
from functools import lru_cache


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
async def get_stock_data(tickers: list, days: int = 90) -> pd.DataFrame or None:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    data_dict = {}
    for ticker in tickers:
        try:
            url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'till': end_date.strftime('%Y-%m-%d'),
                'iss.meta': 'off'
            }
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            data = response.json()
            history_data = data['history']['data']
            if history_data:
                df = pd.DataFrame(history_data, columns=MOEX_COLUMNS)
                df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'])
                df.set_index('TRADEDATE', inplace=True)
                if 'CLOSE' in df.columns:
                    df = df[['CLOSE']].rename(columns={'CLOSE': ticker})
                    data_dict[ticker] = df
                else:
                    logger.warning(f"Колонка CLOSE не найдена для тикера {ticker}")
            await asyncio.sleep(0.1)
        except requests.exceptions.RequestException as error:
            logger.error(f"Ошибка запроса для {ticker}: {error}")
    if not data_dict:
        return None
    combined_df = pd.concat(data_dict.values(), axis=1)
    combined_df = combined_df.ffill().dropna()
    if len(combined_df) < 2:
        logger.warning("Недостаточно данных для расчета корреляции")
        return None
    return combined_df


@lru_cache(maxsize=1)
@logger.catch()
async def get_all_tickers() -> list:
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"
    params = {'iss.meta': 'off'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                securities = data['securities']['data']
                tickers = [sec[0] for sec in securities if sec[1] == 'TQBR']
                return tickers
            else:
                logger.error(f"Ошибка получения тикеров: {response.status}")
                return []


async def get_all_stocks_data(days: int = 90) -> list[pd.DataFrame] or None:
    tickers = await get_all_tickers()
    if not tickers:
        return None
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    data_dict = {}
    successful_tickers = []
    async with aiohttp.ClientSession() as session:
        for ticker in tickers:
            url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'till': end_date.strftime('%Y-%m-%d'),
                'iss.meta': 'off'
            }
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    history_data = data['history']['data']
                    if history_data:
                        df = pd.DataFrame(history_data, columns=MOEX_COLUMNS)
                        if 'CLOSE' in df.columns:
                            df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'])
                            df.set_index('TRADEDATE', inplace=True)
                            df['CLOSE'] = pd.to_numeric(df['CLOSE'], errors='coerce')
                            df = df[['CLOSE']].rename(columns={'CLOSE': ticker}).dropna()
                            if not df.empty and len(df) > 10:  # Минимум 10 точек
                                data_dict[ticker] = df
                                successful_tickers.append(ticker)
            await asyncio.sleep(0.1)
    if not data_dict:
        return None
    combined_df = pd.concat(data_dict.values(), axis=1)
    combined_df = combined_df.ffill().dropna()
    return combined_df


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
    logger.info('Running get_data_moex.py from module moex_api')
