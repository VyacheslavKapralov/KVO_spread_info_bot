from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from database.database_bot import BotDatabase
from moex_api.search_current_ticker import get_ticker
from settings import PARAMETERS
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import (main_menu, menu_perpetual_futures, menu_quarterly_futures_and_stock,
                                            menu_instruments)
from telegram_api.essence.state_machine import MainInfo, Alert


async def command_chancel(message: types.Message, state: FSMContext):
    PARAMETERS['non_stop'] = False
    current_state = await state.get_state()
    if current_state:
        await state.finish()
        await message.answer(BotAnswers.command_chancel_answer(), reply_markup=main_menu())


async def command_start(message: types.Message):
    user_db = await BotDatabase().get_user('user_name', 'allowed_ids')
    if user_db is None or message.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {message.from_user.username} id: {message.from_user.id}")
        await BotDatabase().db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='incoming_ids',
            user_name=message.from_user.username,
            user_id=message.from_user.id,
            info='command_start'
        )
        return
    await message.answer(BotAnswers().start_message(message.from_user.first_name), reply_markup=main_menu())


async def command_main_menu(message: types.Message):
    await message.answer(BotAnswers().main_menu(), reply_markup=main_menu())


async def command_main_menu_callback(callback: types.CallbackQuery):
    await callback.message.answer(BotAnswers().main_menu(), reply_markup=main_menu())


async def get_tickers_at_settings(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MainInfo.type_info.set()
    async with state.proxy() as data:
        data['tickers'] = []
        data['coefficients'] = callback.data.split(';')[1].strip('()').replace(' ', '').split(',')
        tickers = callback.data.split(';')[0]
        data['perpetual'] = False
        for elem in tickers.split('_'):
            if elem[-1] == 'F':
                data['perpetual'] = True
            ticker = await get_ticker(elem)
            if not ticker:
                raise
            data['tickers'].append(ticker)
        if data['perpetual']:
            await callback.message.answer(BotAnswers.what_needs_sent(' '.join(data['tickers'])), reply_markup=menu_perpetual_futures())
            return
        await callback.message.answer(BotAnswers.what_needs_sent(' '.join(data['tickers'])),
                                      reply_markup=menu_quarterly_futures_and_stock())


async def command_get_info_spread(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_db = await BotDatabase().get_user('user_name', 'allowed_ids')
    if user_db is None or callback.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {callback.from_user.username} "
                       f"id: {callback.from_user.id}")
        await BotDatabase().db_write(
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
        text = 'Установка оповещения по спреду'
    else:
        text = 'Получение информации по спреду'
    await callback.message.answer(text)
    await callback.message.answer(BotAnswers.command_back_main_menu(), reply_markup=menu_instruments())


async def command_enable_alerts(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_db = await BotDatabase().get_user('user_name', 'allowed_ids')
    if user_db is None or callback.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {callback.from_user.username} "
                       f"id: {callback.from_user.id}")
        await BotDatabase().db_write(
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
        text = 'Установка оповещения по спреду'
    else:
        text = 'Получение информации по спреду'
    await callback.message.answer(text)
    await callback.message.answer(BotAnswers.command_alerts(), reply_markup=menu_instruments())


async def command_history(message: types.Message):
    user_db = await BotDatabase().get_user('user_name', 'allowed_ids')
    if user_db is None or message.from_user.username not in user_db:
        logger.warning(f"Попытка подключиться к боту: {message.from_user.username} id: {message.from_user.id}")
        await BotDatabase().db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='incoming_ids',
            user_name=message.from_user.username,
            user_id=message.from_user.id,
            info='command_start'
        )
        return
    history_line = await BotDatabase().db_read('bot_lines_signals', message.from_user.username)
    history_bollinger = await BotDatabase().db_read('bot_bb_signals', message.from_user.username)
    if not history_line and not history_bollinger:
        return await message.answer(BotAnswers.not_info_database())
    if history_line:
        for elem in history_line:
            await message.answer(BotAnswers.info_signal_database(elem[0], elem[4], elem[1], elem[2]))
    if history_bollinger:
        for elem in history_bollinger:
            await message.answer(BotAnswers.info_signal_database(elem[0], elem[4], elem[1], elem[2]))


async def register_handlers_commands(dp: Dispatcher):
    dp.register_message_handler(command_chancel, commands=['сброс', 'прервать', 'chancel'], state='*')
    dp.register_message_handler(command_chancel, Text(equals=['сброс', 'прервать', 'chancel'], ignore_case=True),
                                state='*')
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
