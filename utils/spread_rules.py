from time import sleep

from loguru import logger

from settings import PARAMETERS
from utils.calculate_spread import calculate_spread
from utils.data_frame_pandas import add_dataframe_spread_bb

from utils.spread_chart import add_plot_spread
from utils.waiting_time import get_waiting_time


@logger.catch()
def signal_line(data: dict) -> bool:
    tool_min = f"{data['tool_2']}_min_spread"
    tool_max = f"{data['tool_2']}_max_spread"
    # logger.info(f"{data['tool_1']}-{data['tool_2']} = {data['spread']}: {PARAMETERS[tool_min]} --- {PARAMETERS[tool_max]}")
    if PARAMETERS[tool_max] <= float(data['spread']):
        PARAMETERS[tool_max] = float(data['spread'])
        return True
    elif PARAMETERS[tool_min] >= float(data['spread']):
        PARAMETERS[tool_min] = float(data['spread'])
        return True

    return False


@logger.catch()
def signal_bollinger(data: dict):
    data_frame = rule_bb(data)
    plot = add_plot_spread(data['tool_1'], data_frame)
    return plot


@logger.catch()
def rule_bb(data: dict):
    spread_data = add_dataframe_spread_bb(data['tool_1'], data['tool_2'])
    while True:
        last_row = spread_data.iloc[-1]
        if last_row['High'] > last_row['BB_Upper'] or last_row['Low'] < last_row['BB_Lower']:
            return True
        if get_waiting_time(PARAMETERS['time_frame_minutes']) < 2:
            return rule_bb(data)
        spread = calculate_spread(data)
        if spread < last_row['BB_Lower'] or spread > last_row['BB_Upper']:
            return True
        sleep(1)


if __name__ == '__main__':
    logger.info('Running spread_rules.py from module utils')
