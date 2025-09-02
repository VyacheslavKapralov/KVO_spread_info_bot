from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_expiring_futures, menu_futures_and_stock
from utils.data_frame_pandas import calculate_atr, create_dataframe_spread


async def get_average_true_range(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await MainInfo.spread_type_atr.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_atr(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await set_spread_atr(callback, state)


async def set_spread_atr(callback: types.CallbackQuery, state: FSMContext):
    time_frame_minutes = await db.get_setting('technical', 'time_frame_minutes')
    atr_period = await db.get_setting('technical', 'atr_period')
    async with state.proxy() as data:
        df = await create_dataframe_spread(time_frame_minutes, data['coefficients'], data['tickers'],
                                           data['spread_type'])
        df_atr = await calculate_atr(df, atr_period)
        data['atr'] = round(df_atr['atr'].iloc[-1], 3)
    await sending_atr(callback, data)
    await MainInfo.type_info.set()


async def sending_atr(callback: types.CallbackQuery, data: dict):
    if data['expiring_futures']:
        reply_markup = menu_expiring_futures
    else:
        reply_markup = menu_futures_and_stock
    await callback.message.answer(
        BotAnswers().result_calculation_indicator(data['atr'], 'ATR', data['tickers'],
                                                      data['spread_type']), reply_markup=reply_markup())


async def register_handlers_command_atr(dp: Dispatcher):
    dp.register_callback_query_handler(get_average_true_range, lambda callback: callback.data == 'atr',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_atr, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_atr)


if __name__ == '__main__':
    logger.info('Running get_atr_spread_moex.py from module telegram_api/handlers')
