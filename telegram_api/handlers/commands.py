from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.handlers.keyboards import (
    main_menu,
    menu_futures_tool,
    stocks_menu,
    futures_menu,
    stocks_futures_menu,
    spot_menu, menu_spot_tool
)
from settings import PARAMETERS
from utils.search_current_ticker import get_ticker_future


@logger.catch()
async def command_back(callback: types.CallbackQuery):
    logger.info("Получена команда назад.")
    await callback.message.answer(BotAnswers.command_back(), reply_markup=main_menu())


@logger.catch()
async def command_back_message(message: types.Message):
    logger.info("Получена команда назад.")
    await message.answer(BotAnswers.command_back(), reply_markup=main_menu())


@logger.catch()
async def command_start(message: types.Message):
    await message.answer(BotAnswers(message.from_user).start_message(), reply_markup=main_menu())


@logger.catch()
async def command_tool(callback: types.CallbackQuery):
    if callback.data == 'stocks':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_menu())

    if callback.data == 'futures':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=futures_menu())

    if callback.data == 'stocks_futures':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_futures_menu())

    if callback.data == 'spot':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=spot_menu())


@logger.catch()
async def command_futures_tool(callback: types.CallbackQuery):
    PARAMETERS['type_tool'] = 'futures'

    if callback.data == 'CNYRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('CR')
        PARAMETERS['tool_2'] = 'CNYRUBF'

    if callback.data == 'USDRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('Si')
        PARAMETERS['tool_2'] = 'USDRUBF'

    if callback.data == 'EURRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('Eu')
        PARAMETERS['tool_2'] = 'EURRUBF'

    if callback.data == 'GLDRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('GD')
        PARAMETERS['tool_2'] = 'GLDRUBF'

    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_tool())


@logger.catch()
async def command_stocks_futures_tool(callback: types.CallbackQuery):
    PARAMETERS['type_tool'] = 'stocks_futures'

    if callback.data == 'GAZPF':
        PARAMETERS['tool_1'] = await get_ticker_future('GZ')
        PARAMETERS['tool_2'] = 'GAZPF'

    if callback.data == 'SBERF_R':
        PARAMETERS['tool_1'] = await get_ticker_future('SR')
        PARAMETERS['tool_2'] = 'SBERF'

    if callback.data == 'SBERF_P':
        PARAMETERS['tool_1'] = await get_ticker_future('SP')
        PARAMETERS['tool_2'] = 'SBERF'

    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_tool())


@logger.catch()
async def command_stocks_tool(callback: types.CallbackQuery):
    PARAMETERS['type_tool'] = 'stocks'

    if callback.data == 'TATN':
        PARAMETERS['tool_1'] = 'TATN'
        PARAMETERS['tool_2'] = 'TATNP'

    if callback.data == 'MTLR':
        PARAMETERS['tool_1'] = 'MTLR'
        PARAMETERS['tool_2'] = 'MTLRP'

    if callback.data == 'RTKM':
        PARAMETERS['tool_1'] = 'RTKM'
        PARAMETERS['tool_2'] = 'RTKMP'

    if callback.data == 'SBER':
        PARAMETERS['tool_1'] = 'SBER'
        PARAMETERS['tool_2'] = 'SBERP'

    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_spot_tool())


@logger.catch()
async def command_spot_tool(callback: types.CallbackQuery):
    PARAMETERS['type_tool'] = 'spot'

    if callback.data == 'EURUSD':
        PARAMETERS['tool_1'] = await get_ticker_future('GD')
        PARAMETERS['tool_2'] = 'EURUSD'

    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_spot_tool())


@logger.catch()
def register_handlers_commands(dp: Dispatcher):
    dp.register_callback_query_handler(command_back, lambda callback: callback.data == 'main_menu')
    dp.register_message_handler(command_back_message, commands=['main_menu'])
    dp.register_message_handler(command_start, commands=['start', 'старт', 'info', 'инфо', 'help', 'помощь'])
    dp.register_message_handler(command_start,
                                Text(equals=['start', 'старт', 'info', 'инфо', 'help', 'помощь'], ignore_case=True),
                                state='*')
    dp.register_callback_query_handler(command_tool, lambda callback: callback.data in [
        'stocks', 'futures', 'stocks_futures', 'spot'
    ])
    dp.register_callback_query_handler(command_futures_tool, lambda callback: callback.data in [
        'CNYRUBF', 'USDRUBF', 'EURRUBF', 'GLDRUBF'
    ])
    dp.register_callback_query_handler(command_stocks_futures_tool, lambda callback: callback.data in [
        'GAZPF', 'SBERF_R', 'SBERF_P'
    ])
    dp.register_callback_query_handler(command_stocks_tool, lambda callback: callback.data in [
        'TATN', 'MTLR', 'RTKM', 'SBER'
    ])
    dp.register_callback_query_handler(command_spot_tool, lambda callback: callback.data in ['EURUSD'])

    # dp.register_message_handler(command_history, commands=['history', 'история'])


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
