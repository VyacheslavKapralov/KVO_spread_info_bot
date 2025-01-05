from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_futures_tool, menu_spot_tool
from settings import PARAMETERS
from utils.calculate_spread import calculate_spread


@logger.catch()
async def get_spread_moex(callback: types.CallbackQuery):
    logger.info('Получена команда на расчет спреда')
    await MainInfo.spread_type.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


@logger.catch()
async def set_spread_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spread_type'] = callback.data
        data['tool_1'] = PARAMETERS['tool_1']
        data['tool_2'] = PARAMETERS['tool_2']
    await get_spread(callback, state)


@logger.catch()
async def get_spread(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.spread_moex(data['tool_1'], data['tool_2'], data['spread_type']))
        await callback.message.answer(BotAnswers.expectation_answer())
        data['spread'] = await calculate_spread(data)
    logger.info(f'sending_signal_spread:\n{data}\n{PARAMETERS}')
    await sending_signal_spread(callback, data)
    await MainInfo.type_info.set()


@logger.catch()
async def sending_signal_spread(callback: types.CallbackQuery, data):
    if PARAMETERS['type_tool'] == 'futures' or PARAMETERS['type_tool'] == 'stocks_futures':
        await callback.message.answer(f"Спред {data['tool_1']} к {data['tool_2']}: {data['spread']}",
                                      reply_markup=menu_futures_tool())
    else:
        await callback.message.answer(f"Спред {data['tool_1']} к {data['tool_2']}: {data['spread']}",
                                      reply_markup=menu_spot_tool())


@logger.catch()
def register_handlers_command_spread(dp: Dispatcher):
    dp.register_callback_query_handler(get_spread_moex, lambda callback: callback.data == 'spread',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type)


if __name__ == '__main__':
    logger.info('Running get_spread_moex.py from module telegram_api/handlers')
