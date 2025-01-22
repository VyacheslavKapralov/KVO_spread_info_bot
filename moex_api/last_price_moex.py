import requests

from loguru import logger


@logger.catch()
async def get_last_price_moex(ticker: str) -> float or None:
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
            return float(response.json()["marketdata"]["data"][0][8])
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
        count += 1


@logger.catch()
def get_ticker_data(ticker: str) -> dict or None:
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


if __name__ == '__main__':
    logger.info('Running last_price_moex.py from module utils')
