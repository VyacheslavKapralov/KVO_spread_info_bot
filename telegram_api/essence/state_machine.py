from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

class MainInfo(StatesGroup):
    type_tool = State()
    pare_tool = State()
    type_info = State()
    spread_type = State()
    spread_type_ema = State()
    spread_type_sma = State()
    spread_type_atr = State()
    spread_type_bb = State()
    position = State()


if __name__ == '__main__':
    logger.info('Running state_machine.py from module telegram_api/essence')
