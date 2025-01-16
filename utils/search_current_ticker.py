import requests

from loguru import logger


@logger.catch()
async def get_ticker_future(name: str) -> None or str:
    try:
        futures_all: list = await get_all_futures_moex()
        return next((item[0] for item in futures_all if item[0].startswith(name)), None)
    except ValueError as error:
        logger.error(f"Error - {error}: {error.with_traceback()}")


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
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
        count += 1


if __name__ == '__main__':
    logger.info('Running search_current_ticker.py from module utils')
