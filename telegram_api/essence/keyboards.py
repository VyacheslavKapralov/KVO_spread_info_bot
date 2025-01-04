from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger


@logger.catch()
def main_menu():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='Акции', callback_data='stocks'),
        InlineKeyboardButton(text='Фьючерсы', callback_data='futures'),
        InlineKeyboardButton(text='Акции к фьючерсам', callback_data='stocks_futures'),
        InlineKeyboardButton(text='Валюта к фьючерсам', callback_data='spot'),
    )


@logger.catch()
def futures_menu():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='CR---CNYRUBF', callback_data='CNYRUBF'),
        InlineKeyboardButton(text='Si---USDRUBF', callback_data='USDRUBF'),
        InlineKeyboardButton(text='Eu---EURRUBF', callback_data='EURRUBF'),
        InlineKeyboardButton(text='GD---GLDRUBF', callback_data='GLDRUBF'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


@logger.catch()
def stocks_menu():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='TATN---TATNP', callback_data='TATN'),
        InlineKeyboardButton(text='MTLR---MTLRP', callback_data='MTLR'),
        InlineKeyboardButton(text='RTKM---RTKMP', callback_data='RTKM'),
        InlineKeyboardButton(text='SBER---SBERP', callback_data='SBER'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


@logger.catch()
def stocks_futures_menu():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton(text='GZ---GAZPF', callback_data='GAZPF'),
        InlineKeyboardButton(text='SR---SBERF', callback_data='SBERF_R'),
        InlineKeyboardButton(text='SP---SBERF', callback_data='SBERF_P'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


@logger.catch()
def spot_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='ED---EURUSD', callback_data='EURUSD'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


@logger.catch()
def menu_futures_tool():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton(text='Spread', callback_data='spread'),
        InlineKeyboardButton(text='Funding', callback_data='funding'),
        InlineKeyboardButton(text='EMA', callback_data='ema'),
        InlineKeyboardButton(text='SMA', callback_data='sma'),
        InlineKeyboardButton(text='ATR', callback_data='atr'),
        InlineKeyboardButton(text='BollingerBands', callback_data='bollinger_bands'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )

@logger.catch()
def menu_spot_tool():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton(text='Spread', callback_data='spread'),
        InlineKeyboardButton(text='EMA', callback_data='ema'),
        InlineKeyboardButton(text='SMA', callback_data='sma'),
        InlineKeyboardButton(text='ATR', callback_data='atr'),
        InlineKeyboardButton(text='BollingerBands', callback_data='bollinger_bands'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


@logger.catch()
def menu_spread_type():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Валюта', callback_data='money'),
        InlineKeyboardButton(text='Проценты', callback_data='percent'),
    )


if __name__ == '__main__':
    logger.info('Running keyboards.py from module telegram_api/handlers')
