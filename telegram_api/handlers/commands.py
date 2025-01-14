from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import (
    main_menu,
    menu_futures_tool,
    stocks_menu,
    futures_menu,
    stocks_futures_menu,
    spot_menu,
    menu_spot_tool
)
from settings import PARAMETERS
from utils.search_current_ticker import get_ticker_future


@logger.catch()
async def command_back_main_menu(callback: types.CallbackQuery):
    await MainInfo.type_tool.set()
    await callback.message.answer(BotAnswers.command_back_main_menu(), reply_markup=main_menu())


@logger.catch()
async def command_back_main_menu_message(message: types.Message):
    await MainInfo.type_tool.set()
    await message.answer(BotAnswers.command_back_main_menu(), reply_markup=main_menu())


@logger.catch()
async def command_start(message: types.Message):
    await MainInfo.type_tool.set()
    await message.answer(BotAnswers().start_message(message.from_user.first_name), reply_markup=main_menu())


@logger.catch()
async def command_tool(callback: types.CallbackQuery):
    await MainInfo.pare_tool.set()
    if callback.data == 'stocks':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_menu())
    if callback.data == 'spot_futures':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=futures_menu())
    if callback.data == 'stocks_futures':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_futures_menu())
    if callback.data == 'spot':
        await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=spot_menu())


@logger.catch()
async def command_futures_tool(callback: types.CallbackQuery):
    PARAMETERS['type_tool'] = 'futures'
    await MainInfo.type_info.set()
    if callback.data == 'CNYRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('CR')
        PARAMETERS['tool_2'] = 'CNYRUBF'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'] = 1, 1
    if callback.data == 'USDRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('Si')
        PARAMETERS['tool_2'] = 'USDRUBF'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'] = 1, 1000
    if callback.data == 'EURRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('Eu')
        PARAMETERS['tool_2'] = 'EURRUBF'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'] = 1, 1000
    if callback.data == 'GLDRUBF':
        PARAMETERS['tool_1'] = await get_ticker_future('GD')
        PARAMETERS['tool_2'] = 'GLDRUBF'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'] = 1, 1
    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_tool())


@logger.catch()
async def command_stocks_futures_tool(callback: types.CallbackQuery):
    PARAMETERS['type_tool'] = 'stocks_futures'
    await MainInfo.type_info.set()
    if callback.data == 'GAZPF':
        PARAMETERS['tool_1'] = await get_ticker_future('GZ')
        PARAMETERS['tool_2'] = 'GAZPF'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'] = 1, 100
    if callback.data == 'SBERF_R':
        PARAMETERS['tool_1'] = await get_ticker_future('SR')
        PARAMETERS['tool_2'] = 'SBERF'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'] = 1, 100
    if callback.data == 'SBERF_P':
        PARAMETERS['tool_1'] = await get_ticker_future('SP')
        PARAMETERS['tool_2'] = 'SBERF'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_2'] = 1, 100
    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_tool())


@logger.catch()
async def command_stocks_tool(callback: types.CallbackQuery):
    PARAMETERS['type_tool'] = 'stocks'
    await MainInfo.type_info.set()
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
    await MainInfo.type_info.set()
    if callback.data == 'EURUSD':
        PARAMETERS['tool_1'] = await get_ticker_future('GD')
        PARAMETERS['tool_2'] = 'EURUSD'
        PARAMETERS['coefficient_tool_1'], PARAMETERS['coefficient_tool_1'] = 1, 1
    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_spot_tool())


@logger.catch()
def register_handlers_commands(dp: Dispatcher):
    dp.register_callback_query_handler(command_back_main_menu, lambda callback: callback.data == 'main_menu',
                                       state='*')
    dp.register_message_handler(command_back_main_menu_message, commands=['main_menu'], state='*')
    dp.register_message_handler(command_start, commands=['start', 'старт', 'info', 'инфо', 'help', 'помощь'], state='*')
    dp.register_message_handler(command_start, Text(equals=['start', 'старт', 'info', 'инфо', 'help', 'помощь'],
                                                    ignore_case=True), state='*')
    dp.register_callback_query_handler(command_tool, lambda callback: callback.data in [
        'stocks', 'spot_futures', 'stocks_futures', 'spot'], state=MainInfo.type_tool)
    dp.register_callback_query_handler(command_futures_tool, lambda callback: callback.data in [
        'CNYRUBF', 'USDRUBF', 'EURRUBF', 'GLDRUBF'], state=MainInfo.pare_tool)
    dp.register_callback_query_handler(command_stocks_futures_tool, lambda callback: callback.data in [
        'GAZPF', 'SBERF_R', 'SBERF_P'], state=MainInfo.pare_tool)
    dp.register_callback_query_handler(command_stocks_tool, lambda callback: callback.data in [
        'TATN', 'MTLR', 'RTKM', 'SBER'], state=MainInfo.pare_tool)
    dp.register_callback_query_handler(command_spot_tool, lambda callback: callback.data in ['EURUSD'],
                                       state=MainInfo.pare_tool)

    # dp.register_message_handler(command_history, commands=['history', 'история'])


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
