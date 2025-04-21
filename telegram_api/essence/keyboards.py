from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from settings import PARAMETERS


@logger.catch()
def main_menu():
    keyboard = InlineKeyboardMarkup()
    for type_tool, value in PARAMETERS['pairs'].items():
        keyboard.add(InlineKeyboardButton(text=type_tool, callback_data="None"))
        row = []
        for elem in value:
            text_button = ' '.join(elem[0])
            callback_data = f"{text_button.replace(' ', '_')};{elem[1]}"
            button = InlineKeyboardButton(text=text_button, callback_data=callback_data)
            row.append(button)
            if len(row) == 2:
                keyboard.add(*row)
                row = []
        if row:
            keyboard.add(*row)
    return keyboard


@logger.catch()
def menu_perpetual_futures():
    return InlineKeyboardMarkup(row_width=4).add(
        InlineKeyboardButton(text='Spread', callback_data='spread'),
        InlineKeyboardButton(text='Funding', callback_data='funding'),
        InlineKeyboardButton(text='EMA', callback_data='ema'),
        InlineKeyboardButton(text='SMA', callback_data='sma'),
        InlineKeyboardButton(text='ATR', callback_data='atr'),
        InlineKeyboardButton(text='BollingerBands', callback_data='bollinger_bands'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


@logger.catch()
def menu_quarterly_futures_and_stock():
    return InlineKeyboardMarkup(row_width=4).add(
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
