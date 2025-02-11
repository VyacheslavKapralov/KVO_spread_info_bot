import requests

from datetime import datetime

from loguru import logger

from moex_api.get_data_moex import get_ticker_data


@logger.catch()
def get_candles_moex(interval_day: int, ticker: str) -> tuple[list, list] or None:  # задержка 25 минут. Не годится.
    ticker_data = get_ticker_data(ticker)
    engines = ticker_data["boards"]["data"][0][7]
    markets = ticker_data["boards"]["data"][0][5]
    board_groups = ticker_data["boards"]["data"][0][3]
    url = (f'https://iss.moex.com/cs/engines/{engines}/markets/{markets}/boardgroups/{board_groups}/'
           f'securities/{ticker}.json')
    params = {
        's1.type': 'candles',
        'interval': 1,
        'candles': interval_day * 14 * 60
    }
    count = 0
    while count < 5:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            candles = response.json()['zones'][0]['series'][0]['candles']
            volumes = response.json()['zones'][1]['series'][0]['candles']
            return remove_keys(candles, volumes)
        except ConnectionResetError as error:
            logger.error(f"Error - {error}: {error.with_traceback()}")
        except requests.HTTPError as error:
            logger.error(
                f"HTTP error occurred: {error}\nStatus code: {error.response.status_code} - "
                f"Response: {error.response.text}"
            )
        count += 1


@logger.catch()
def remove_keys(list_1: list, list_2: list):
    keys_remove_1 = ['close_time', 'close_y', 'high_y', 'low_y', 'open_time_x', 'open_y']
    keys_remove_2 = ['close_time', 'open_time_x', 'value_y']
    cleaned_list_1 = [clean_dict(data, keys_remove_1) for data in list_1]
    cleaned_list_2 = [clean_dict(data, keys_remove_2) for data in list_2]
    combined_list = [
        {**item_1, **item_2, 'date': datetime.utcfromtimestamp(item_1['open_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}
        for item_1 in cleaned_list_1
        for item_2 in cleaned_list_2
        if item_1['open_time'] == item_2['open_time']
    ]
    for item in combined_list:
        item.pop('open_time', None)
    result = [
        [elem['date'], elem['open'], elem['high'], elem['low'], elem['close'], elem['value']]
        for elem in combined_list
    ]
    return result


@logger.catch()
def clean_dict(data: dict, keys_to_remove: list) -> dict:
    return {k: v for k, v in data.items() if k not in keys_to_remove}


if __name__ == '__main__':
    logger.info('Running get_data_moex.py from module utils')
