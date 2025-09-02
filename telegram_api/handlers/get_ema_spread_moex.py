from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_expiring_futures, menu_futures_and_stock
from utils.data_frame_pandas import calculate_ema, create_dataframe_spread


async def exponential_ma(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await MainInfo.spread_type_ema.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_ema(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await get_spread_ema(callback, state)


async def get_spread_ema(callback: types.CallbackQuery, state: FSMContext):
    time_frame_minutes = await db.get_setting('technical', 'time_frame_minutes')
    ema_period = await db.get_setting('technical', 'ema_period')
    async with state.proxy() as data:
        df = await create_dataframe_spread(time_frame_minutes, data['coefficients'], data['tickers'],
                                           data['spread_type'])
        df_ema = await calculate_ema(df, ema_period)
        data['ema'] = round(df_ema['ema'].iloc[-1], 3)
    await sending_signal_ema(callback, data)
    await MainInfo.type_info.set()


async def sending_signal_ema(callback: types.CallbackQuery, data: dict):
    if data['expiring_futures']:
        reply_markup = menu_expiring_futures
    else:
        reply_markup = menu_futures_and_stock
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
