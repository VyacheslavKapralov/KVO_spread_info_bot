from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from database.database_bot import db
from moex_api.search_current_ticker import get_ticker
from telegram_api.essence.answers_bot import bot_answers
from telegram_api.essence.keyboards import (main_menu, menu_expiring_futures, menu_futures_and_stock,
                                            menu_instruments)
from telegram_api.essence.state_machine import MainInfo, Alert


async def command_start(message: types.Message):
    user_db = await db.get_user('user_name', 'allowed_ids')
    if user_db is None or message.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {message.from_user.username} id: {message.from_user.id}")
        await db.db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='incoming_ids',
            user_name=message.from_user.username,
            user_id=message.from_user.id,
            info='command_start'
        )
        return
    await message.answer(bot_answers.start_message(message.from_user.first_name), reply_markup=main_menu())


async def command_main_menu(message: types.Message):
    await message.answer(bot_answers.main_menu(), reply_markup=main_menu())


async def command_main_menu_callback(callback: types.CallbackQuery):
    await callback.message.answer(bot_answers.main_menu(), reply_markup=main_menu())


async def get_tickers_at_settings(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MainInfo.type_info.set()
    data_parts = callback.data.split(';')
    group_name = data_parts[0]
    pair_index = int(data_parts[1])
    pairs = await db.get_pairs(group_name)
    pair_list = pairs[group_name]
    symbols, coefficients = pair_list[pair_index]
    keyboard = menu_futures_and_stock()
    async with state.proxy() as data:
        data['tickers'] = []
        data['expiring_futures'] = False
        data['coefficients'] = coefficients
        for elem in symbols:
            if group_name != 'stocks':
                data['expiring_futures'] = True
                keyboard = menu_expiring_futures()
            ticker = await get_ticker(elem)
            data['tickers'].append(ticker)
        await callback.message.answer(bot_answers.what_needs_sent(data['tickers']), reply_markup=keyboard)


async def command_get_info_spread(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_db = await db.get_user('user_name', 'allowed_ids')
    if user_db is None or callback.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {callback.from_user.username} "
                       f"id: {callback.from_user.id}")
        await db.db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='incoming_ids',
            user_name=callback.from_user.username,
            user_id=callback.from_user.id,
            info='command_start'
        )
        return
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await MainInfo.type_ticker.set()
    if callback.data == 'set_alerts':
        await callback.message.answer(bot_answers.set_alert())
    else:
        await callback.message.answer(bot_answers.get_info_spread())
    await callback.message.answer(bot_answers.command_back_main_menu())
    await menu_instruments(callback.message)


async def command_enable_alerts(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_db = await db.get_user('user_name', 'allowed_ids')
    if user_db is None or callback.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {callback.from_user.username} "
                       f"id: {callback.from_user.id}")
        await db.db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='incoming_ids',
            user_name=callback.from_user.username,
            user_id=callback.from_user.id,
            info='command_start'
        )
        return
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await Alert.tickers.set()
    if callback.data == 'set_alerts':
        text = bot_answers.set_alert()
    else:
        text = bot_answers.get_info_spread()
    await callback.message.answer(text)
    await callback.message.answer(bot_answers.command_alerts())
    await menu_instruments(callback.message)


async def command_history(message: types.Message):
    user_db = await db.get_user('user_name', 'allowed_ids')
    if user_db is None or message.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {message.from_user.username} id: {message.from_user.id}")
        await db.db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='incoming_ids',
            user_name=message.from_user.username,
            user_id=message.from_user.id,
            info='command_start'
        )
        return None
    history_line = await db.db_read('bot_lines_signals', message.from_user.username)
    history_bollinger = await db.db_read('bot_bb_signals', message.from_user.username)
    history_fair_spread = await db.db_read('bot_deviation_fair_spread_signals', message.from_user.username)
    if not history_line and not history_bollinger:
        return await message.answer(bot_answers.not_info_database())
    if history_line:
        for elem in history_line[-10:]:
            await message.answer(bot_answers.info_signal_database(elem[1], elem[4], elem[2], elem[3]))
    if history_bollinger:
        for elem in history_bollinger[-10:]:
            await message.answer(bot_answers.info_signal_database(elem[1], elem[4], elem[2], elem[3]))
    if history_fair_spread:
        for elem in history_fair_spread[-10:]:
            await message.answer(bot_answers.info_signal_database(elem[1], elem[4], elem[2], elem[3]))
    return None


async def register_handlers_commands(dp: Dispatcher):
    dp.register_callback_query_handler(command_get_info_spread, lambda callback: callback.data == 'spread_info',
                                       state='*')
    dp.register_callback_query_handler(command_enable_alerts, lambda callback: callback.data == 'set_alerts', state='*')
    dp.register_message_handler(command_start, commands=['start', 'старт', 'info', 'инфо', 'help', 'помощь'], state='*')
    dp.register_message_handler(command_start, Text(equals=['start', 'старт', 'info', 'инфо', 'help', 'помощь'],
                                                    ignore_case=True), state='*')
    dp.register_message_handler(command_main_menu, commands=['main_menu'], state='*')
    dp.register_callback_query_handler(command_main_menu_callback, lambda callback: callback.data == 'main_menu',
                                       state='*')
    dp.register_callback_query_handler(get_tickers_at_settings, state=MainInfo.type_ticker)
    dp.register_message_handler(command_history, commands=['history', 'история'], state='*')
    dp.register_message_handler(command_history, Text(equals=['история'], ignore_case=True), state='*')


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
