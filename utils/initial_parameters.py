from loguru import logger
from settings import PARAMETERS



@logger.catch()
def save_original_parameters(data: dict) -> dict:
    new_data = {}
    for key, val in data.items():
        if key == 'non_stop' or key == 'commands':
            continue
        new_data[key] = val
    return new_data


@logger.catch()
def restore_original_parameters(data: dict) -> None:
    for key, val in data['initial_parameters'].items():
        if PARAMETERS.get(key):
            PARAMETERS[key] = val


if __name__ == '__main__':
    logger.info('Running initial_parameters.py from module utils')