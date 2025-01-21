from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
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
async def command_back_main_menu(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await MainInfo.type_tool.set()
    await callback.message.answer(BotAnswers.command_back_main_menu(), reply_markup=main_menu())


@logger.catch()
async def command_back_main_menu_message(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await MainInfo.type_tool.set()
    await message.answer(BotAnswers.command_back_main_menu(), reply_markup=main_menu())


@logger.catch()
async def command_start(message: types.Message):
    await command_back_main_menu_message(message)
    await message.answer(BotAnswers().start_message(message.from_user.first_name), reply_markup=main_menu())


@logger.catch()
async def command_tool(callback: types.CallbackQuery):
    await MainInfo.pare_tool.set()
    if callback.data == 'stocks':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_menu())
    if callback.data == 'spot_futures':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=futures_menu())
    if callback.data == 'stocks_futures':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_futures_menu())
    if callback.data == 'spot':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=spot_menu())


@logger.catch()
async def command_futures_tool(callback: types.CallbackQuery, state: FSMContext):
    await MainInfo.type_info.set()
    tool_1 = await get_ticker_future(PARAMETERS['futures_pairs'].get(callback.data)['pair'][0])
    if tool_1:
        async with state.proxy() as data:
            data['type_tool'] = 'futures'
            data['tool_1'] = tool_1
            data['tool_2'] = PARAMETERS['futures_pairs'][callback.data]['pair'][1]
            data['coefficient_tool_1'] = PARAMETERS['futures_pairs'][callback.data]['coefficient_1']
            data['coefficient_tool_2'] = PARAMETERS['futures_pairs'][callback.data]['coefficient_2']
        return await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_tool())
    await callback.message.answer(BotAnswers.not_get_ticker(), reply_markup=main_menu())
    await MainInfo.type_info.set()


@logger.catch()
async def command_stocks_futures_tool(callback: types.CallbackQuery, state: FSMContext):
    await MainInfo.type_info.set()
    tool_1 = await get_ticker_future(PARAMETERS['futures_pairs'].get(callback.data)['pair'][0])
    if tool_1:
        async with state.proxy() as data:
            data['type_tool'] = 'stocks_futures'
            data['tool_1'] = tool_1
            data['tool_2'] = PARAMETERS['futures_pairs'][callback.data]['pair'][1]
            data['coefficient_tool_1'] = PARAMETERS['futures_pairs'][callback.data]['coefficient_1']
            data['coefficient_tool_2'] = PARAMETERS['futures_pairs'][callback.data]['coefficient_2']
        return await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_tool())
    await callback.message.answer(BotAnswers.not_get_ticker(), reply_markup=main_menu())
    await MainInfo.type_tool.set()


@logger.catch()
async def command_stocks_tool(callback: types.CallbackQuery, state: FSMContext):
    await MainInfo.type_info.set()
    async with state.proxy() as data:
        data['type_tool'] = 'stocks'
        data['tool_1'] = callback.data
        data['tool_2'] = PARAMETERS['stocks_pairs'].get(callback.data)
        data['coefficient_tool_1'], data['coefficient_tool_2'] = 1, 1
    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_spot_tool())


@logger.catch()
async def command_gold_futures_tool(callback: types.CallbackQuery, state: FSMContext):
    await MainInfo.type_info.set()
    tool_1 = await get_ticker_future(PARAMETERS['futures_pairs'].get(callback.data)['pair'][0])
    tool_2 = await get_ticker_future(PARAMETERS['futures_pairs'].get(callback.data)['pair'][1])
    if tool_1 and tool_2:
        async with state.proxy() as data:
            data['type_tool'] = 'stocks_futures'
            data['tool_1'] = tool_1
            data['tool_2'] = tool_2
            data['tool_3'] = PARAMETERS['futures_pairs'][callback.data]['pair'][2]
            data['coefficient_tool_1'] = PARAMETERS['futures_pairs'][callback.data]['coefficient_1']
            data['coefficient_tool_2'] = PARAMETERS['futures_pairs'][callback.data]['coefficient_2']
            data['coefficient_tool_3'] = PARAMETERS['futures_pairs'][callback.data]['coefficient_3']
        return await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_tool())
    await callback.message.answer(BotAnswers.not_get_ticker(), reply_markup=main_menu())
    await MainInfo.type_tool.set()


@logger.catch()
async def command_spot_tool(callback: types.CallbackQuery, state: FSMContext):  # функция не готова
    await MainInfo.type_info.set()
    # tool_1 = await get_ticker_future(PARAMETERS['spots_pairs'].get(callback.data))
    tool_1 = None
    if tool_1:
        async with state.proxy() as data:
            data['type_tool'] = 'spot'
            data['tool_1'] = tool_1
            data['tool_2'] = 'EURUSD'
            data['coefficient_tool_1'], data['coefficient_tool_2'] = 1, 1
        await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_spot_tool())
    await callback.message.answer(BotAnswers.not_get_ticker(), reply_markup=main_menu())
    await MainInfo.type_tool.set()


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
        'CNYRUBF', 'USDRUBF', 'EURRUBF'], state=MainInfo.pare_tool)
    dp.register_callback_query_handler(command_gold_futures_tool,
                                       lambda callback: callback.data == 'GLDRUBF', state=MainInfo.pare_tool)
    dp.register_callback_query_handler(command_stocks_futures_tool, lambda callback: callback.data in [
        'GAZPF', 'SBERF_R', 'SBERF_P'], state=MainInfo.pare_tool)
    dp.register_callback_query_handler(command_stocks_tool, lambda callback: callback.data in [
        'TATN', 'MTLR', 'RTKM', 'SBER'], state=MainInfo.pare_tool)

    # dp.register_callback_query_handler(command_spot_tool, lambda callback: callback.data in ['EURUSD'],
    #                                    state=MainInfo.pare_tool)
    # dp.register_message_handler(command_history, commands=['history', 'история'])


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
