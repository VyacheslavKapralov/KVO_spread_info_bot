from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from loguru import logger

from database.database_bot import db


def main_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Информация по спреду', callback_data='spread_info'),
        InlineKeyboardButton(text='Оповещения по спреду', callback_data='set_alerts'),
        InlineKeyboardButton(text='Список работающих мониторингов', callback_data='list_monitors'),
        InlineKeyboardButton(text='Корреляция инструментов', callback_data='correlation'),
        InlineKeyboardButton(text='История корреляции инструментов', callback_data='correlation_history'),
    )


def back_main_menu():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/back_main_menu'))


async def menu_instruments(message: types.Message):
    pairs = await db.get_pairs_formatted()
    if not pairs:
        await db.initialize_default_pairs()
        pairs = await db.get_pairs_formatted()
    for group_name, pair_list in pairs.items():
        if group_name == 'perpetual':
            group_name_text = 'Фьюч. валюты: квартальные к вечным'
        elif group_name == 'gold':
            group_name_text = 'Золото'
        elif group_name == 'stock_future':
            group_name_text = 'Фьюч. акций: квартальные к вечным'
        elif group_name == 'synthetic_spot':
            group_name_text = 'Синтетические валюты'
        elif group_name == 'stocks':
            group_name_text = 'Акции'
        else:
            continue
        keyboard = InlineKeyboardMarkup()
        row = []
        for pair_index, (symbols, coefficients) in enumerate(pair_list):
            text_button = ' '.join(symbols)
            callback_data = f"{group_name};{pair_index}"
            button = InlineKeyboardButton(text=text_button, callback_data=callback_data)
            row.append(button)
            if len(row) == 2:
                keyboard.add(*row)
                row = []
        if row:
            keyboard.add(*row)
        await message.answer(f"<b>{group_name_text}</b>", parse_mode="HTML", reply_markup=keyboard)


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


def menu_type_alert_futures():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Пересечение горизонтальной линии', callback_data='line_alert'),
        InlineKeyboardButton(text='Пересечение линий Боллинджера', callback_data='bollinger_bands_alert'),
        InlineKeyboardButton(text='Отклонение от справедливого спреда', callback_data='deviation_fair_spread'),
    )


def menu_type_alert_stocks():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='Пересечение горизонтальной линии', callback_data='line_alert'),
        InlineKeyboardButton(text='Пересечение линий Боллинджера', callback_data='bollinger_bands_alert'),
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


def correlation_menu():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("Ввести тикеры", callback_data="correlation_custom"),
        InlineKeyboardButton("Все акции", callback_data="correlation_all")
    )


def correlation_months():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text="1 месяц", callback_data='1_month'),
        InlineKeyboardButton(text="3 месяца", callback_data='3_month'),
        InlineKeyboardButton(text="6 месяцев", callback_data='6_month'),
        InlineKeyboardButton(text="1 год", callback_data='1_year'),
    )


def correlation_all_menu():
    keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("1 месяц", callback_data="all_1_month"),
        InlineKeyboardButton("3 месяца", callback_data="all_3_month"),
        InlineKeyboardButton("6 месяцев", callback_data="all_6_month"),
        InlineKeyboardButton("1 год", callback_data="all_1_year")
    )
    return keyboard


def correlation_database():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("1 месяц", callback_data="saved_30"),
        InlineKeyboardButton("3 месяца", callback_data="saved_90"),
        InlineKeyboardButton("6 месяцев", callback_data="saved_180"),
        InlineKeyboardButton("1 год", callback_data="saved_365")
    )


if __name__ == '__main__':
    logger.info('Running keyboards.py from module telegram_api/essence')
