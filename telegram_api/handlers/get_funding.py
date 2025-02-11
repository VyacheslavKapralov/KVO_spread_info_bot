from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_futures_ticker, menu_spot_ticker
from utils.calculate_funding import calculate_funding
from utils.decorators import check_int


@logger.catch()
async def funding(callback: types.CallbackQuery):
    await MainInfo.position.set()
    await callback.message.answer(BotAnswers.position())


@logger.catch()
@check_int
async def set_position(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['position'] = int(message.text)
    await get_funding(message, state)


@logger.catch()
async def get_funding(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(BotAnswers.expectation_answer())
        if len(data['tickers']) == 2:
            data['funding'] = await calculate_funding(data['tickers'][1])
        elif len(data['tickers']) == 3:
            data['funding'] = await calculate_funding(data['tickers'][2])
    await sending_signal_funding(message, data)
    await MainInfo.type_info.set()


@logger.catch()
async def sending_signal_funding(message: types.Message, data: dict):
    if data['type_ticker'] == 'futures' or data['type_ticker'] == 'stocks_futures':
        keyboard = menu_futures_ticker
    else:
        keyboard = menu_spot_ticker
    if len(data['tickers']) == 2:
        await message.answer(
            BotAnswers().result_calculation_funding(data['funding'] * data['position'], data['tickers'][1]),
            reply_markup=keyboard())
    elif len(data['tickers']) == 3:
        await message.answer(
            BotAnswers().result_calculation_funding(data['funding'] * data['position'], data['tickers'][1],
                                                    data['tickers'][2]), reply_markup=keyboard())


@logger.catch()
async def register_handlers_command_funding(dp: Dispatcher):
    dp.register_callback_query_handler(funding, lambda callback: callback.data == 'funding',
                                       state=MainInfo.type_info)
    dp.register_message_handler(set_position, state=MainInfo.position)


if __name__ == '__main__':
    logger.info('Running get_funding.py from module telegram_api/handlers')
