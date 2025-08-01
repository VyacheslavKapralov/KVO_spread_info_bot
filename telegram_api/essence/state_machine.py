from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

class MainInfo(StatesGroup):
    type_ticker = State()
    pare_ticker = State()
    type_info = State()
    spread_type = State()
    spread_type_ema = State()
    spread_type_sma = State()
    spread_type_atr = State()
    spread_type_bb = State()
    volume_position = State()
    direction_position = State()


class Alert(StatesGroup):
    tickers = State()
    type_alert = State()
    type_spread = State()
    min_line = State()
    max_line = State()


class AdminPanel(StatesGroup):
    what_edit = State()
    access_bot = State()
    add_user = State()
    set_user_nik = State()
    del_user = State()


if __name__ == '__main__':
    logger.info('Running state_machine.py from module telegram_api/essence')
