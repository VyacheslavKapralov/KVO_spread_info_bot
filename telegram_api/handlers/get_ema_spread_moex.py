from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_perpetual_futures, menu_quarterly_futures_and_stock
from settings import PARAMETERS
from utils.data_frame_pandas import calculate_ema, create_dataframe_spread


async def exponential_ma(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MainInfo.spread_type_ema.set()
    async with state.proxy() as data:
        await callback.message.answer(f"EMA спреда для {' '.join(data['tickers'])}")
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_ema(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    if callback.data == 'money':
        text = 'Значение спреда в валюте'
    else:
        text = 'Значение спреда в процентах'
    await callback.message.answer(text)
    await get_spread_ema(callback, state)


async def get_spread_ema(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.expectation_answer())
        df = await create_dataframe_spread(PARAMETERS['time_frame_minutes'], data['coefficients'], data['tickers'],
                                           data['spread_type'])
        df_ema = await calculate_ema(df, PARAMETERS['ema_period'])
        data['ema'] = round(df_ema['ema'].iloc[-1], 3)
    await sending_signal_ema(callback, data)
    await MainInfo.type_info.set()


async def sending_signal_ema(callback: types.CallbackQuery, data: dict):
    if data['perpetual']:
        reply_markup = menu_perpetual_futures
    else:
        reply_markup = menu_quarterly_futures_and_stock
    await callback.message.answer(
        BotAnswers().result_calculation_indicator(data['ema'], 'EMA', data['tickers'],
                                                      data['spread_type']), reply_markup=reply_markup())


async def register_handlers_command_ema(dp: Dispatcher):
    dp.register_callback_query_handler(exponential_ma, lambda callback: callback.data == 'ema',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_ema, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_ema)


if __name__ == '__main__':
    logger.info('Running get_ema_spread_moex.py from module telegram_api/handlers')
