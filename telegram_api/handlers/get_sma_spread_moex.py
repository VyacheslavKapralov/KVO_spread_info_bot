from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_futures_tool, menu_spot_tool
from settings import PARAMETERS
from utils.calculate_spread import calculate_spread
from utils.data_frame_pandas import calculate_sma, create_dataframe_spread


@logger.catch()
async def simple_ma(callback: types.CallbackQuery):
    logger.info('Получена команда на расчет SMA спреда')
    await MainInfo.spread_type_sma.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


@logger.catch()
async def set_spread_type_sma(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spread_type'] = callback.data
        data['tool_1'] = PARAMETERS['tool_1']
        data['tool_2'] = PARAMETERS['tool_2']
    await get_spread_sma(callback, state)


@logger.catch()
async def get_spread_sma(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.spread_sma_moex(data['tool_1'], data['tool_2'], data['spread_type']))
        await callback.message.answer(BotAnswers.expectation_answer())
        data['spread'] = await calculate_spread(data, PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'])
        df = await create_dataframe_spread(
            data,
            PARAMETERS['time_frame_minutes'],
            PARAMETERS['coefficient_tool_1'],
            PARAMETERS['coefficient_tool_2']
        )
        df_sma = await calculate_sma(df, PARAMETERS['sma_period'])
        data['sma'] = round(df_sma['sma'].iloc[-1], 3)
    await sending_signal_sma(callback, data)
    await MainInfo.type_info.set()


@logger.catch()
async def sending_signal_sma(callback: types.CallbackQuery, data: dict):
    if PARAMETERS['type_tool'] == 'futures' or PARAMETERS['type_tool'] == 'stocks_futures':
        await callback.message.answer(f"SMA спреда {data['tool_1']} к {data['tool_2']}: {data['sma']}",
                                      reply_markup=menu_futures_tool())
    else:
        await callback.message.answer(f"SMA спреда {data['tool_1']} к {data['tool_2']}: {data['sma']}",
                                      reply_markup=menu_spot_tool())


@logger.catch()
def register_handlers_command_sma(dp: Dispatcher):
    dp.register_callback_query_handler(simple_ma, lambda callback: callback.data == 'sma',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_sma, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_sma)


if __name__ == '__main__':
    logger.info('Running get_sma_spread_moex.py from module telegram_api/handlers')
