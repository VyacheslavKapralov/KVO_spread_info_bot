import requests
from loguru import logger


@logger.catch()
async def calculate_funding(ticker: str) -> float:
    funding_rate = await get_funding_moex(ticker)
    lot_volume = await get_lot_volume(ticker)
    return funding_rate * lot_volume


@logger.catch()
async def get_funding_moex(ticker: str):
    url = f"https://iss.moex.com/cs/engines/futures/markets/swaprates/securities/{ticker}.json"
    params = {
        'candles': 2,
        'interval': 1,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        funding_rate_now = response.json()['zones'][0]['series'][0]['candles'][1]['value']
        return funding_rate_now
    else:
        logger.info(f"Ошибка: {response.status_code} - {response.text}")


@logger.catch()
async def get_lot_volume(ticker: str):
    url = f"https://iss.moex.com/iss/engines/futures/markets/forts/securities/{ticker}.json"
    params = {
        'iss.meta': 'off',
        'iss.json': 'extended',
        'callback': 'JSON_CALLBACK',
        'ang': 'ru',
        'contractname': 1,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        lot_volume = response.json()[1]['securities'][0]['LOTVOLUME']
        return lot_volume
    else:
        logger.info(f"Ошибка в get_lot_volume: {response.status_code} - {response.text}")


if __name__ == "__main__":
    logger.info('Running calculate_funding.py from module utils')
