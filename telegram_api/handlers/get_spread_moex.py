from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import bot_answers
from telegram_api.essence.keyboards import menu_spread_type, menu_expiring_futures, menu_futures_and_stock
from telegram_api.essence.state_machine import MainInfo
from utils.calculate_spread import calculate_spread


async def get_spread_moex(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await MainInfo.spread_type.set()
    await callback.message.answer(text=bot_answers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await set_spread(callback, state)


async def set_spread(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spread'] = await calculate_spread(data['coefficients'], data['spread_type'], data['tickers'])
    await sending_spread(callback, data)
    await MainInfo.type_info.set()


async def sending_spread(callback: types.CallbackQuery, data):
    if data['expiring_futures']:
        reply_markup = menu_expiring_futures
    else:
        reply_markup = menu_futures_and_stock
    await callback.message.answer(bot_answers.result_calculation_indicator(data['spread'], 'Спред', data['tickers'],
                                                                           data['spread_type']),
                                  reply_markup=reply_markup())


async def register_handlers_command_spread(dp: Dispatcher):
    dp.register_callback_query_handler(get_spread_moex, lambda callback: callback.data == 'spread',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type)


if __name__ == '__main__':
    logger.info('Running get_spread_moex.py from module telegram_api/handlers')
