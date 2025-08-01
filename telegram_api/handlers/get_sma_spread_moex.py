from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_perpetual_futures, menu_quarterly_futures_and_stock
from settings import PARAMETERS
from utils.data_frame_pandas import calculate_sma, create_dataframe_spread


async def simple_ma(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MainInfo.spread_type_sma.set()
    async with state.proxy() as data:
        await callback.message.answer(f"SMA спреда для {' '.join(data['tickers'])}")
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_sma(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    if callback.data == 'money':
        text = BotAnswers.money_spread()
    else:
        text = BotAnswers.percent_spread()
    await callback.message.answer(text)
    await get_spread_sma(callback, state)


async def get_spread_sma(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.expectation_answer())
        df = await create_dataframe_spread(PARAMETERS['time_frame_minutes'], data['coefficients'], data['tickers'],
                                           data['spread_type'])
        df_sma = await calculate_sma(df, PARAMETERS['sma_period'])
        data['sma'] = round(df_sma['sma'].iloc[-1], 3)
    await sending_signal_sma(callback, data)
    await MainInfo.type_info.set()


async def sending_signal_sma(callback: types.CallbackQuery, data: dict):
    if data['perpetual']:
        reply_markup = menu_perpetual_futures
    else:
        reply_markup = menu_quarterly_futures_and_stock
    await callback.message.answer(
        BotAnswers().result_calculation_indicator(data['sma'], 'SMA', data['tickers'],
                                                      data['spread_type']), reply_markup=reply_markup())


async def register_handlers_command_sma(dp: Dispatcher):
    dp.register_callback_query_handler(simple_ma, lambda callback: callback.data == 'sma',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_sma, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_sma)


if __name__ == '__main__':
    logger.info('Running get_sma_spread_moex.py from module telegram_api/handlers')
