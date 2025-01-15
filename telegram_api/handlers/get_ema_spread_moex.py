from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_futures_tool, menu_spot_tool
from settings import PARAMETERS
from utils.data_frame_pandas import calculate_ema, create_dataframe_spread


@logger.catch()
async def exponential_ma(callback: types.CallbackQuery):
    await MainInfo.spread_type_ema.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


@logger.catch()
async def set_spread_type_ema(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await get_spread_ema(callback, state)


@logger.catch()
async def get_spread_ema(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.expectation_answer())
        df = await create_dataframe_spread(PARAMETERS['time_frame_minutes'], data)
        df_ema = await calculate_ema(df, PARAMETERS['ema_period'])
        data['ema'] = round(df_ema['ema'].iloc[-1], 3)
    await sending_signal_ema(callback, data)
    await MainInfo.type_info.set()


@logger.catch()
async def sending_signal_ema(callback: types.CallbackQuery, data: dict):
    if data['type_tool'] == 'futures' or data['type_tool'] == 'stocks_futures':
        if not data.get('tool_3'):
            await callback.message.answer(
                BotAnswers().result_calculation_indicator(data['ema'], 'EMA', data['tool_1'], data['tool_2'], data['spread_type']),
                reply_markup=menu_futures_tool())
        else:
            await callback.message.answer(
                BotAnswers().result_calculation_indicator(data['ema'], 'EMA', data['tool_1'], data['tool_2'], data['spread_type'],
                                                          data['tool_3']), reply_markup=menu_futures_tool())
    else:
        if not data.get('tool_3'):
            await callback.message.answer(
                BotAnswers().result_calculation_indicator(data['ema'], 'EMA', data['tool_1'], data['tool_2'], data['spread_type']),
                reply_markup=menu_spot_tool())
        else:
            await callback.message.answer(
                BotAnswers().result_calculation_indicator(data['ema'], 'EMA', data['tool_1'], data['tool_2'], data['spread_type'],
                                                          data['tool_3']), reply_markup=menu_spot_tool())


@logger.catch()
def register_handlers_command_ema(dp: Dispatcher):
    dp.register_callback_query_handler(exponential_ma, lambda callback: callback.data == 'ema',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_ema, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_ema)


if __name__ == '__main__':
    logger.info('Running get_ema_spread_moex.py from module telegram_api/handlers')
