from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from settings import PARAMETERS


def main_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Получить информацию по спреду', callback_data='spread_info'),
        InlineKeyboardButton(text='Установить оповещения по спреду', callback_data='set_alerts'),
    )


def menu_chancel():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/chancel'))


def menu_instruments():
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


def menu_quarterly_futures_and_stock():
    return InlineKeyboardMarkup(row_width=4).add(
        InlineKeyboardButton(text='Spread', callback_data='spread'),
        InlineKeyboardButton(text='EMA', callback_data='ema'),
        InlineKeyboardButton(text='SMA', callback_data='sma'),
        InlineKeyboardButton(text='ATR', callback_data='atr'),
        InlineKeyboardButton(text='BollingerBands', callback_data='bollinger_bands'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


def menu_spread_type():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Валюта', callback_data='money'),
        InlineKeyboardButton(text='Проценты', callback_data='percent'),
    )


def menu_direction_position():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Продажа', callback_data='short'),
        InlineKeyboardButton(text='Покупка', callback_data='long'),
    )

def menu_type_alert():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Пересечение горизонтальной линии', callback_data='line_alert'),
        InlineKeyboardButton(text='Пересечение линий Боллинджера', callback_data='bollinger_bands_alert'),
    )


def admin_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Доступ к боту', callback_data='access'),
        InlineKeyboardButton(text='Параметры бота', callback_data='params'),
        InlineKeyboardButton(text='Прислать список пользователей', callback_data='get_users'),
        InlineKeyboardButton(text='Прислать историю сигналов', callback_data='get_signals'),
        InlineKeyboardButton(text='Закрыть панель администратора', callback_data='stop_admin'),
    )


def access_bot_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Добавить пользователя в допущенные', callback_data='add_user'),
        InlineKeyboardButton(text='Удалить пользователя из допущенных', callback_data='del_user')
    )


def confirm_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Да', callback_data='yes'),
        InlineKeyboardButton(text='Нет', callback_data='no')
    )


if __name__ == '__main__':
    logger.info('Running keyboards.py from module telegram_api/handlers')
