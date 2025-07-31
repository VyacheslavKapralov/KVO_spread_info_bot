from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import Alert
from telegram_api.essence.keyboards import menu_type_alert, menu_spread_type
from moex_api.search_current_ticker import get_ticker
from telegram_api.handlers.spread_rules import signal_line, signal_bb
from utils.decorators import check_float


@logger.catch()
async def set_tickers_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
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


@logger.catch()
async def set_type_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await Alert.type_spread.set()
    async with state.proxy() as data:
        data['type_alert'] = callback.data
    if callback.data == 'line_alert':
        text = 'Пересечение горизонтальной линии'
    else:
        text = 'Пересечение линий Боллинджера'
    await callback.message.answer(text)
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


@logger.catch()
async def set_type_spread_alert(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    if callback.data == 'money':
        text = 'Значение спреда в валюте'
    else:
        text = 'Значение спреда в процентах'
    await callback.message.answer(text)
    if data['type_alert'] == 'line_alert':
        await Alert.min_line.set()
        await callback.message.answer(BotAnswers.grid_min_price_answer())
    else:
        await callback.message.answer(BotAnswers.expectation_answer())
        await signal_bb(data, callback.message)


@logger.catch()
@check_float
async def set_minimum_line_alert(message: types.Message, state: FSMContext):
    await Alert.max_line.set()
    async with state.proxy() as data:
        data['min_line'] = message.text
    await message.answer(BotAnswers.grid_max_price_answer())


@logger.catch()
@check_float
async def set_maximum_line_alert(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['max_line'] = message.text
    await message.answer(BotAnswers.expectation_answer())
    await signal_line(data, message)


@logger.catch()
async def register_handlers_alerts(dp: Dispatcher):
    dp.register_callback_query_handler(set_tickers_alert, state=Alert.tickers)
    dp.register_callback_query_handler(set_type_alert, state=Alert.type_alert)
    dp.register_callback_query_handler(set_type_spread_alert, state=Alert.type_spread)
    dp.register_message_handler(set_minimum_line_alert, state=Alert.min_line)
    dp.register_message_handler(set_maximum_line_alert, state=Alert.max_line)


if __name__ == '__main__':
    logger.info('Running get_alerts.py from module telegram_api/handlers')
