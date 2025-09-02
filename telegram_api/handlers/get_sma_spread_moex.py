from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_expiring_futures, menu_futures_and_stock
from utils.data_frame_pandas import calculate_sma, create_dataframe_spread


async def simple_ma(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await MainInfo.spread_type_sma.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_sma(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await get_spread_sma(callback, state)


async def get_spread_sma(callback: types.CallbackQuery, state: FSMContext):
    time_frame_minutes = await db.get_setting('technical', 'time_frame_minutes')
    sma_period = await db.get_setting('technical', 'sma_period')
    async with state.proxy() as data:
        df = await create_dataframe_spread(time_frame_minutes, data['coefficients'], data['tickers'],
                                           data['spread_type'])
        df_sma = await calculate_sma(df, sma_period)
        data['sma'] = round(df_sma['sma'].iloc[-1], 3)
    await sending_signal_sma(callback, data)
    await MainInfo.type_info.set()


async def sending_signal_sma(callback: types.CallbackQuery, data: dict):
    if data['expiring_futures']:
        reply_markup = menu_expiring_futures
    else:
        reply_markup = menu_futures_and_stock
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
