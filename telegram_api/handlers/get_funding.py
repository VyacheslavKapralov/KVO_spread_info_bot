from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_futures_tool, menu_spot_tool
from settings import PARAMETERS
from utils.calculate_funding import calculate_funding
from utils.decorators import check_int


@logger.catch()
async def funding(callback: types.CallbackQuery):
    logger.info('Получена команда для вычисления фандинга')
    await MainInfo.position.set()
    await callback.message.answer(BotAnswers.position())


@logger.catch()
@check_int
async def set_position(message: types.Message, state: FSMContext):
    logger.info(f'set_position: {message.text}')
    async with state.proxy() as data:
        data['position'] = int(message.text)
        data['tool_1'] = PARAMETERS['tool_1']
        data['tool_2'] = PARAMETERS['tool_2']
    await get_funding(message, state)


@logger.catch()
async def get_funding(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(BotAnswers.expectation_answer())
        data['funding'] = await calculate_funding(data['tool_2'])
    logger.info(f'sending_signal_funding:\n{data}\n{PARAMETERS}')
    await sending_signal_funding(message, data)
    await MainInfo.type_info.set()


@logger.catch()
async def sending_signal_funding(message: types.Message, data: dict):
    if PARAMETERS['type_tool'] == 'futures' or PARAMETERS['type_tool'] == 'stocks_futures':
        await message.answer(f"Фандинг {data['tool_2']}: {data['funding'] * data['position']}",
                             reply_markup=menu_futures_tool())
    else:
        await message.answer(f"Фандинг {data['tool_2']}: {data['funding'] * data['position']}",
                             reply_markup=menu_spot_tool())


@logger.catch()
def register_handlers_command_funding(dp: Dispatcher):
    dp.register_callback_query_handler(funding, lambda callback: callback.data == 'funding',
                                       state=MainInfo.type_info)
    dp.register_message_handler(set_position, state=MainInfo.position)


if __name__ == '__main__':
    logger.info('Running get_funding.py from module telegram_api/handlers')
