from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger


class Spread(StatesGroup):
    spread_type = State()

class SMA(StatesGroup):
    spread_type = State()

class EMA(StatesGroup):
    spread_type = State()

class Plot(StatesGroup):
    spread_type = State()

class ATR(StatesGroup):
    spread_type = State()

class Position(StatesGroup):
    position = State()


if __name__ == '__main__':
    logger.info('Running state_machine.py from module telegram_api/essence')
