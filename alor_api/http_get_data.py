import requests

from loguru import logger

from alor_api.alor_connect import AlorTokenManager
from settings import AlorSettings


def get_all_instruments_exchange(exchange: str = 'MOEX') -> list or None:
    url = f"https://api.alor.ru/md/v2/Securities/{exchange}"
    if AlorTokenManager().check_token_valid():
        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {AlorSettings().alor_access_token.get_secret_value()}'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            return response.text
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.__traceback__}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
    else:
        logger.error("Просроченный или некорректный Access Токен")
        return None


async def get_info_symbol(symbol: str, exchange: str = 'MOEX') -> dict or None:
    url = f"https://api.alor.ru/md/v2/Securities/{exchange}/{symbol}"
    if AlorTokenManager().check_token_valid():
        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {AlorSettings().alor_access_token.get_secret_value()}'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json()
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.__traceback__}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
    else:
        logger.error("Просроченный или некорректный Access Токен")
        return None


async def get_symbol_board(symbol: str, exchange: str = 'MOEX') -> list or None:
    url = f"https://api.alor.ru/md/v2/Securities/{exchange}/{symbol}/availableBoards"
    if AlorTokenManager().check_token_valid():
        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {AlorSettings().alor_access_token.get_secret_value()}'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            return response.text
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.__traceback__}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
    else:
        logger.error("Просроченный или некорректный Access Токен")
        return None


async def get_last_price_alor(symbol: str, exchange: str = 'MOEX') -> str or None:
    url = f"https://api.alor.ru/md/v2/Securities/{exchange}:{symbol}/quotes"
    if AlorTokenManager().check_token_valid():
        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {AlorSettings().alor_access_token.get_secret_value()}'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json()[0]['last_price']
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.__traceback__}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
    else:
        logger.error("Просроченный или некорректный Access Токен")
        return None


if __name__ == "__main__":
    logger.info('Running http_get_data.py from module alor_api')