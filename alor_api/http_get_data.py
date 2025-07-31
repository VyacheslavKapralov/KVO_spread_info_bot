import requests

from loguru import logger

from alor_api.alor_connect import AlorTokenManager
from settings import AlorSettings


def get_all_instruments_exchange(exchange: str = 'MOEX') -> list:
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
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
    else:
        logger.error("Просроченный или некорректный Access Токен")


async def get_info_symbol(symbol: str, exchange: str = 'MOEX') -> dict:
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
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
    else:
        logger.error("Просроченный или некорректный Access Токен")


async def get_symbol_board(symbol: str, exchange: str = 'MOEX') -> list:
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
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
    else:
        logger.error("Просроченный или некорректный Access Токен")


if __name__ == "__main__":
    logger.info(get_all_instruments_exchange('MOEX'))