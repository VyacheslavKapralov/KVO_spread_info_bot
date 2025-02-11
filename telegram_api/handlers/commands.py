from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import (
    main_menu,
    menu_futures_ticker,
    stocks_menu,
    futures_menu,
    stocks_futures_menu,
    spot_menu,
    menu_spot_ticker
)
from settings import PARAMETERS
from moex_api.search_current_ticker import get_ticker_future


@logger.catch()
async def command_back_main_menu(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await MainInfo.type_ticker.set()
    await callback.message.answer(BotAnswers.command_back_main_menu(), reply_markup=main_menu())


@logger.catch()
async def command_back_main_menu_message(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await MainInfo.type_ticker.set()
    await message.answer(BotAnswers.command_back_main_menu(), reply_markup=main_menu())


@logger.catch()
async def command_start(message: types.Message):
    await command_back_main_menu_message(message)
    await message.answer(BotAnswers().start_message(message.from_user.first_name), reply_markup=main_menu())


@logger.catch()
async def command_ticker(callback: types.CallbackQuery):
    await MainInfo.pare_ticker.set()
    if callback.data == 'stocks':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_menu())
    if callback.data == 'spot_futures':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=futures_menu())
    if callback.data == 'stocks_futures':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=stocks_futures_menu())
    if callback.data == 'spot':
        return await callback.message.answer(BotAnswers.pare_need_info(), reply_markup=spot_menu())


@logger.catch()
async def command_futures_ticker(callback: types.CallbackQuery, state: FSMContext):
    await MainInfo.type_info.set()
    async with state.proxy() as data:
        data['type_ticker'] = 'futures'
        data['tickers'] = []
        data['coefficients'] = []
        for elem in PARAMETERS['futures_pairs'][callback.data]['pair']:
            ticker = await get_ticker_future(elem)
            data['tickers'].append(ticker)
        for elem in PARAMETERS['futures_pairs'][callback.data]['coefficients']:
            data['coefficients'].append(elem)
        return await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_futures_ticker())


@logger.catch()
async def command_stocks_ticker(callback: types.CallbackQuery, state: FSMContext):
    await MainInfo.type_info.set()
    async with state.proxy() as data:
        data['type_ticker'] = 'stocks'
        data['tickers'] = [callback.data, PARAMETERS['stocks_pairs'].get(callback.data)]
        data['coefficients'] = [1, 1]
    await callback.message.answer(BotAnswers.what_needs_sent(), reply_markup=menu_spot_ticker())


@logger.catch()
async def register_handlers_commands(dp: Dispatcher):
    dp.register_callback_query_handler(command_back_main_menu, lambda callback: callback.data == 'main_menu',
                                       state='*')
    dp.register_message_handler(command_back_main_menu_message, commands=['main_menu'], state='*')
    dp.register_message_handler(command_start, commands=['start', 'старт', 'info', 'инфо', 'help', 'помощь'], state='*')
    dp.register_message_handler(command_start, Text(equals=['start', 'старт', 'info', 'инфо', 'help', 'помощь'],
                                                    ignore_case=True), state='*')
    dp.register_callback_query_handler(command_ticker, lambda callback: callback.data in [
        'stocks', 'spot_futures', 'stocks_futures', 'spot'], state=MainInfo.type_ticker)
    dp.register_callback_query_handler(command_futures_ticker, lambda callback: callback.data in [
        'CNYRUBF', 'EURRUBF', 'GAZPF', 'GLDRUBF', 'IMOEXF', 'SBERF_R', 'SBERF_P', 'USDRUBF'], state=MainInfo.pare_ticker)
    dp.register_callback_query_handler(command_stocks_ticker, lambda callback: callback.data in [
        'TATN', 'MTLR', 'RTKM', 'SBER'], state=MainInfo.pare_ticker)


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
