from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_perpetual_futures, menu_quarterly_futures_and_stock
from utils.calculate_spread import calculate_spread


async def get_spread_moex(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MainInfo.spread_type.set()
    async with state.proxy() as data:
        await callback.message.answer(f"Спред для {' '.join(data['tickers'])}")
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    if callback.data == 'money':
        text = 'Значение спреда в валюте'
    else:
        text = 'Значение спреда в процентах'
    await callback.message.answer(text)
    await get_spread(callback, state)


async def get_spread(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.expectation_answer())
        data['spread'] = await calculate_spread(data['coefficients'], data['spread_type'], data['tickers'])
    await sending_signal_spread(callback, data)
    await MainInfo.type_info.set()


async def sending_signal_spread(callback: types.CallbackQuery, data):
    if data['perpetual']:
        reply_markup = menu_perpetual_futures
    else:
        reply_markup = menu_quarterly_futures_and_stock
    await callback.message.answer(
        BotAnswers().result_calculation_indicator(data['spread'], 'Спред', data['tickers'],
                                                      data['spread_type']), reply_markup=reply_markup())


async def register_handlers_command_spread(dp: Dispatcher):
    dp.register_callback_query_handler(get_spread_moex, lambda callback: callback.data == 'spread',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type)


if __name__ == '__main__':
    logger.info('Running get_spread_moex.py from module telegram_api/handlers')
