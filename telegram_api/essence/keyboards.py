from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from database.database_bot import db


def main_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Получить информацию по спреду', callback_data='spread_info'),
        InlineKeyboardButton(text='Установить оповещения по спреду', callback_data='set_alerts'),
        InlineKeyboardButton(text='Вывести список работающих мониторингов', callback_data='list_monitors'),
    )


def back_main_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/back_main_menu'))


async def menu_instruments():
    keyboard = InlineKeyboardMarkup()
    pairs = await db.get_pairs_formatted()
    if not pairs:
        await db.initialize_default_pairs()
        pairs = await db.get_pairs_formatted()

    for type_tool, pair_list in pairs.items():
        keyboard.add(InlineKeyboardButton(text=type_tool, callback_data="None"))
        row = []
        for symbols, coefficients in pair_list:
            text_button = ' '.join(symbols)
            coeffs_str = str(coefficients).replace(' ', '')
            callback_data = f"{text_button.replace(' ', '_')};{coeffs_str}"
            button = InlineKeyboardButton(text=text_button, callback_data=callback_data)
            row.append(button)
            if len(row) == 2:
                keyboard.add(*row)
                row = []
        if row:
            keyboard.add(*row)

    return keyboard


def menu_expiring_futures():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='Spread', callback_data='spread'),
        InlineKeyboardButton(text='Funding', callback_data='funding'),
        InlineKeyboardButton(text='EMA', callback_data='ema'),
        InlineKeyboardButton(text='SMA', callback_data='sma'),
        InlineKeyboardButton(text='ATR', callback_data='atr'),
        InlineKeyboardButton(text='Bollinger', callback_data='bollinger_bands'),
        InlineKeyboardButton(text='Fair Price', callback_data='fair_price'),
        InlineKeyboardButton(text='Fair Spread', callback_data='fair_spread'),
        InlineKeyboardButton(text='Main Menu', callback_data='main_menu'),
    )


def menu_futures_and_stock():
    return InlineKeyboardMarkup(row_width=4).add(
        InlineKeyboardButton(text='Spread', callback_data='spread'),
        InlineKeyboardButton(text='EMA', callback_data='ema'),
        InlineKeyboardButton(text='SMA', callback_data='sma'),
        InlineKeyboardButton(text='ATR', callback_data='atr'),
        InlineKeyboardButton(text='Bollinger', callback_data='bollinger_bands'),
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
        InlineKeyboardButton(text='Отклонение от справедливого спреда', callback_data='deviation_fair_spread'),
    )


def menu_monitor_control():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Остановить все', callback_data='stop_all'),
        InlineKeyboardButton(text='Остановить один', callback_data='stop_one'),
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
        InlineKeyboardButton(text='Удалить пользователя из допущенных', callback_data='del_user'),
        InlineKeyboardButton(text="Назад", callback_data="back_to_admin")
    )


def confirm_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Да', callback_data='yes'),
        InlineKeyboardButton(text='Нет', callback_data='no')
    )


def settings_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Редактировать настройки', callback_data='edit_settings'),
        InlineKeyboardButton(text='Назад', callback_data='back_to_admin')
    )


def settings_edit_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    categories = [
        'expiration', 'time_frame_minutes', 'bollinger_period',
        'bollinger_deviation', 'sma_period', 'ema_period', 'atr_period',
        'signals', 'pairs', 'commands'
    ]
    for category in categories:
        keyboard.add(InlineKeyboardButton(category, callback_data=f"edit_category-{category}"))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_to_admin"))
    return keyboard


if __name__ == '__main__':
    logger.info('Running keyboards.py from module telegram_api/handlers')
