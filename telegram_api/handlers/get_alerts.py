import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from moex_api.search_current_ticker import get_ticker
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import (menu_type_alert, menu_spread_type, menu_monitor_control, main_menu,
                                            back_main_menu)
from telegram_api.essence.spread_monitor import SpreadMonitor, generate_monitor_id
from telegram_api.essence.state_machine import Alert, MonitoringControl
from telegram_api.handlers.spread_rules import signal_line, signal_bb
from utils.decorators import check_float

spread_monitor = SpreadMonitor()


async def set_tickers_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await Alert.type_alert.set()
    async with state.proxy() as data:
        data['tickers'] = []
        data['coefficients'] = callback.data.split(';')[1].strip('()').replace(' ', '').split(',')
        tickers = callback.data.split(';')[0]
        for elem in tickers.split('_'):
            ticker = await get_ticker(elem)
            if not ticker:
                raise
            data['tickers'].append(ticker)
    await callback.message.answer(f"Спред для {' '.join(data['tickers'])}")
    await callback.message.answer(BotAnswers.what_alert_set(' '.join(data['tickers'])), reply_markup=menu_type_alert())


async def set_type_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await Alert.type_spread.set()
    async with state.proxy() as data:
        data['type_alert'] = callback.data
    if callback.data == 'line_alert':
        text = BotAnswers.line_alert()
    else:
        text = BotAnswers.bb_alert()
    await callback.message.answer(text)
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_type_spread_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
        monitor_id = generate_monitor_id(data['tickers'], data['type_alert'])
        data['monitor_id'] = monitor_id
    if callback.data == 'money':
        text = BotAnswers.money_spread()
    else:
        text = BotAnswers.percent_spread()
    await callback.message.answer(text)
    if data['type_alert'] == 'line_alert':
        await Alert.min_line.set()
        await callback.message.answer(BotAnswers.grid_min_price_answer())
    else:
        await callback.message.answer(BotAnswers.expectation_answer())
        task = asyncio.create_task(signal_bb(data, callback, monitor_id, spread_monitor))
        await spread_monitor.add_monitor(callback.from_user.id, monitor_id, task, data)
        await callback.message.answer(BotAnswers.start_monitoring(monitor_id), reply_markup=back_main_menu())


@check_float
async def set_minimum_line_alert(message: types.Message, state: FSMContext):
    await Alert.max_line.set()
    async with state.proxy() as data:
        data['min_line'] = message.text
    await message.answer(BotAnswers.grid_max_price_answer())


@check_float
async def set_maximum_line_alert(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['max_line'] = message.text
        monitor_id = data['monitor_id']
    await message.answer(BotAnswers.expectation_answer())
    task = asyncio.create_task(signal_line(data, message, monitor_id, spread_monitor))
    await spread_monitor.add_monitor(message.from_user.id, monitor_id, task, data)
    await message.answer(BotAnswers.start_monitoring(monitor_id), reply_markup=back_main_menu())


async def stop_monitor(message: types.Message):
    success = await spread_monitor.remove_monitor(message.from_user.id, message.text)
    if success:
        await message.answer(BotAnswers.stop_monitoring(message.text), reply_markup=menu_monitor_control())
    else:
        await message.answer(BotAnswers.not_monitoring(), reply_markup=menu_monitor_control())


async def stop_all_monitors(callback: types.CallbackQuery):
    count = await spread_monitor.remove_all_user_monitors(callback.from_user.id)
    await callback.message.answer(BotAnswers.stop_all_monitoring(count), reply_markup=main_menu())


async def list_monitors(callback: types.CallbackQuery):
    monitors = await spread_monitor.get_user_monitors(callback.from_user.id)
    if not monitors:
        await callback.message.answer(BotAnswers.not_active_monitoring())
        return
    await callback.message.answer(BotAnswers.active_monitoring())
    for monitor_id, data in monitors.items():
        await callback.message.answer(BotAnswers.get_active_monitoring(monitor_id, data))
    await callback.message.answer(BotAnswers.select_action_monitoring(), reply_markup=menu_monitor_control())


async def select_action_monitoring(callback: types.CallbackQuery):
    if callback.data == 'stop_all':
        await stop_all_monitors(callback)
    else:
        await MonitoringControl.del_monitoring.set()
        await callback.message.answer(BotAnswers.stop_one_monitor())


async def command_back_main_menu(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await message.answer(BotAnswers().main_menu(), reply_markup=main_menu())


async def register_handlers_alerts(dp: Dispatcher):
    dp.register_message_handler(command_back_main_menu, commands=['сброс', 'назад', 'back_main_menu'], state='*')
    dp.register_message_handler(command_back_main_menu, Text(equals=['сброс', 'назад', 'back_main_menu'], ignore_case=True),
                                state='*')
    dp.register_callback_query_handler(set_tickers_alert, state=Alert.tickers)
    dp.register_callback_query_handler(set_type_alert, state=Alert.type_alert)
    dp.register_callback_query_handler(set_type_spread_alert, state=Alert.type_spread)
    dp.register_message_handler(set_minimum_line_alert, state=Alert.min_line)
    dp.register_message_handler(set_maximum_line_alert, state=Alert.max_line)
    dp.register_message_handler(stop_monitor, state=MonitoringControl.del_monitoring)
    dp.register_callback_query_handler(select_action_monitoring,
                                       lambda callback: callback.data in ['stop_all', 'stop_one'],
                                       state='*')
    dp.register_callback_query_handler(list_monitors, lambda callback: callback.data == 'list_monitors',
                                       state='*')


if __name__ == '__main__':
    logger.info('Running get_alerts.py from module telegram_api/handlers')
