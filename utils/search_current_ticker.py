import requests

from loguru import logger


@logger.catch()
async def get_ticker_future(name: str) -> None or str:
    futures_all = await get_all_futures_moex()
    return next((item[0] for item in futures_all if item[0].startswith(name)), None)


@logger.catch()
async def get_all_futures_moex():
    url = 'https://iss.moex.com/iss/engines/futures/markets/forts/securities.json'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["securities"]["data"]
    else:
        logger.info(f"Ошибка в get_all_futures_moex: {response.status_code} - {response.text}")


if __name__ == '__main__':
    logger.info('Running search_current_ticker.py from module utils')
