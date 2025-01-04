from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import SMA
from telegram_api.handlers.keyboards import menu_spread_type, menu_futures_tool
from settings import PARAMETERS
from utils.calculate_spread import calculate_spread
from utils.data_frame_pandas import calculate_sma, create_dataframe_spread


@logger.catch()
async def simple_ma(callback: types.CallbackQuery):
    logger.info('Получена команда на расчет SMA спреда')
    await SMA.spread_type.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


@logger.catch()
async def set_spread_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spread_type'] = callback.data
        data['tool_1'] = PARAMETERS['tool_1']
        data['tool_2'] = PARAMETERS['tool_2']
    await get_spread(callback.message, state)


@logger.catch()
async def get_spread(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(BotAnswers.spread_sma_moex(data['tool_1'], data['tool_2'], data['spread_type']))
        await message.answer(BotAnswers.expectation_answer())
        data['spread'] = await calculate_spread(data)
        df = await create_dataframe_spread(data['tool_1'], data['tool_2'])
        sma = round(calculate_sma(df)['sma'].iloc[-1], 3)
        logger.info(f"SMA {data['tool_1']}/{data['tool_2']} = {sma}")
        data['sma'] = sma
        await sending_signal(message, data)
    await state.finish()


@logger.catch()
async def sending_signal(message: types.Message, data: dict):
    await message.answer(f"SMA спреда {data['tool_1']} к {data['tool_2']} ({data['spread']}): {data['sma']}",
                         reply_markup=menu_futures_tool())


@logger.catch()
def register_handlers_command_sma(dp: Dispatcher):
    dp.register_callback_query_handler(simple_ma, lambda callback: callback.data == 'sma')
    # dp.register_message_handler(simple_ma, Text(equals=['SMA', 'sma', 'средняя']))
    dp.register_callback_query_handler(set_spread_type, state=SMA.spread_type)


if __name__ == '__main__':
    logger.info('Running get_sma_spread_moex.py from module telegram_api/handlers')
