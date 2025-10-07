import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from database.database_bot import db
from moex_api.search_current_ticker import get_ticker
from telegram_api.essence.answers_bot import bot_answers
from telegram_api.essence.keyboards import (menu_type_alert_futures, menu_spread_type, menu_monitor_control, main_menu,
                                            back_main_menu, confirm_menu, menu_type_alert_stocks)
from telegram_api.essence.spread_monitor import SpreadMonitor, generate_monitor_id
from telegram_api.essence.state_machine import Alert, MonitoringControl
from telegram_api.handlers.spread_rules import signal_line, signal_bb, signal_deviation_fair_spread
from utils.decorators import check_float, check_timeframe, check_int

spread_monitor = SpreadMonitor()


async def set_tickers_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await Alert.type_alert.set()
    data_parts = callback.data.split(';')
    group_name = data_parts[0]
    pair_index = int(data_parts[1])
    pairs = await db.get_pairs(group_name)
    pair_list = pairs[group_name]
    symbols, coefficients = pair_list[pair_index]
    keyboard_markup = menu_type_alert_futures()
    async with state.proxy() as data:
        data['tickers'] = []
        data['coefficients'] = coefficients
        for elem in symbols:
            ticker = await get_ticker(elem)
            if not ticker:
                raise
            data['tickers'].append(ticker)
        if group_name == 'stocks':
            keyboard_markup = menu_type_alert_stocks()
    await callback.message.answer(bot_answers.spread_tickers(data['tickers']))
    await callback.message.answer(bot_answers.what_alert_set(), reply_markup=keyboard_markup)


async def set_type_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await Alert.type_spread.set()
    async with state.proxy() as data:
        data['type_alert'] = callback.data
    if callback.data == 'line_alert':
        await callback.message.answer(bot_answers.line_alert())
        await callback.message.answer(bot_answers.spread_type(), reply_markup=menu_spread_type())
    elif callback.data == 'bollinger_bands_alert':
        await Alert.update_settings.set()
        await callback.message.answer(bot_answers.bb_alert())
        await callback.message.answer(bot_answers.setting_update(), reply_markup=confirm_menu())
    elif callback.data == 'deviation_fair_spread':
        await callback.message.answer(bot_answers.fair_price_alert())
        await callback.message.answer(bot_answers.spread_type(), reply_markup=menu_spread_type())


async def settings_correction(callback: types.CallbackQuery):
    await callback.message.delete()
    if callback.data == 'no':
        await Alert.type_spread.set()
        await callback.message.answer(bot_answers.spread_type(), reply_markup=menu_spread_type())
    else:
        await Alert.timeframe.set()
        await callback.message.answer(bot_answers.set_time_frame())


@check_timeframe
async def set_time_frame(message: types.Message, state: FSMContext):
    await Alert.period.set()
    async with state.proxy() as data:
        data['time_frame'] = message.text
    await message.answer(bot_answers.set_period())


@check_int
async def set_period(message: types.Message, state: FSMContext):
    await Alert.type_spread.set()
    async with state.proxy() as data:
        data['period'] = message.text
    await message.answer(bot_answers.spread_type(), reply_markup=menu_spread_type())


async def set_type_spread_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
        monitor_id = generate_monitor_id(data['tickers'], data['type_alert'])
        data['monitor_id'] = monitor_id
    if callback.data == 'money':
        text = bot_answers.money_spread()
    else:
        text = bot_answers.percent_spread()
    await callback.message.answer(text)
    if data['type_alert'] == 'line_alert':
        await Alert.min_line.set()
        await callback.message.answer(bot_answers.grid_min_price_answer())
    elif data['type_alert'] == 'bollinger_bands_alert':
        task = asyncio.create_task(signal_bb(data, callback, monitor_id, spread_monitor))
        await spread_monitor.add_monitor(callback.from_user.id, monitor_id, task, data)
        await callback.message.answer(bot_answers.start_monitoring(monitor_id), reply_markup=back_main_menu())
        await state.finish()
    elif data['type_alert'] == 'deviation_fair_spread':
        await Alert.deviation_fair_spread.set()
        await callback.message.answer(bot_answers.deviation_fair_spread_answer())


@check_float
async def set_minimum_line_alert(message: types.Message, state: FSMContext):
    await Alert.max_line.set()
    async with state.proxy() as data:
        data['min_line'] = message.text
    await message.answer(bot_answers.grid_max_price_answer())


@check_float
async def set_maximum_line_alert(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['max_line'] = message.text
        monitor_id = data['monitor_id']
    task = asyncio.create_task(signal_line(data, message, monitor_id, spread_monitor))
    await spread_monitor.add_monitor(message.from_user.id, monitor_id, task, data)
    await message.answer(bot_answers.start_monitoring(monitor_id), reply_markup=back_main_menu())
    await state.finish()


@check_float
async def set_deviation_fair_spread_alert(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['deviation_fair_spread'] = message.text
        monitor_id = data['monitor_id']
    task = asyncio.create_task(signal_deviation_fair_spread(data, message, monitor_id, spread_monitor))
    await spread_monitor.add_monitor(message.from_user.id, monitor_id, task, data)
    await message.answer(bot_answers.start_monitoring(monitor_id), reply_markup=back_main_menu())
    await state.finish()


async def stop_monitor(message: types.Message, state: FSMContext):
    success = await spread_monitor.remove_monitor(message.from_user.id, message.text)
    if success:
        await message.answer(bot_answers.stop_monitoring(message.text), reply_markup=menu_monitor_control())
    else:
        await message.answer(bot_answers.not_monitoring(), reply_markup=menu_monitor_control())
    await state.finish()


async def stop_all_monitors(callback: types.CallbackQuery, state: FSMContext):
    count = await spread_monitor.remove_all_user_monitors(callback.from_user.id)
    await callback.message.answer(bot_answers.stop_all_monitoring(count), reply_markup=main_menu())
    await state.finish()


async def list_monitors(callback: types.CallbackQuery, state: FSMContext):
    monitors = await spread_monitor.get_user_monitors(callback.from_user.id)
    if not monitors:
        await callback.message.answer(bot_answers.not_active_monitoring())
        await state.finish()
        return
    await callback.message.answer(bot_answers.active_monitoring())
    for monitor_id, data in monitors.items():
        await callback.message.answer(bot_answers.get_active_monitoring(monitor_id, data))
    await callback.message.answer(bot_answers.select_action_monitoring(), reply_markup=menu_monitor_control())


async def select_action_monitoring(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'stop_all':
        await stop_all_monitors(callback, state)
    else:
        await MonitoringControl.del_monitoring.set()
        await callback.message.answer(bot_answers.stop_one_monitor())


async def command_back_main_menu(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await message.answer(bot_answers.main_menu(), reply_markup=main_menu())


async def register_handlers_alerts(dp: Dispatcher):
    dp.register_message_handler(command_back_main_menu, commands=['сброс', 'назад', 'back_main_menu'], state='*')
    dp.register_message_handler(command_back_main_menu,
                                Text(equals=['сброс', 'назад', 'back_main_menu'], ignore_case=True),
                                state='*')
    dp.register_callback_query_handler(set_tickers_alert, state=Alert.tickers)
    dp.register_callback_query_handler(set_type_alert, state=Alert.type_alert)
    dp.register_callback_query_handler(set_type_spread_alert, state=Alert.type_spread)
    dp.register_callback_query_handler(settings_correction, lambda callback: callback.data in ['yes', 'no'],
                                       state=Alert.update_settings)
    dp.register_message_handler(set_minimum_line_alert, state=Alert.min_line)
    dp.register_message_handler(set_maximum_line_alert, state=Alert.max_line)
    dp.register_message_handler(set_time_frame, state=Alert.timeframe)
    dp.register_message_handler(set_period, state=Alert.period)
    dp.register_message_handler(set_deviation_fair_spread_alert, state=Alert.deviation_fair_spread)
    dp.register_message_handler(stop_monitor, state=MonitoringControl.del_monitoring)
    dp.register_callback_query_handler(select_action_monitoring,
                                       lambda callback: callback.data in ['stop_all', 'stop_one'],
                                       state='*')
    dp.register_callback_query_handler(list_monitors, lambda callback: callback.data == 'list_monitors',
                                       state='*')


if __name__ == '__main__':
    logger.info('Running set_alerts.py from module telegram_api/handlers')
