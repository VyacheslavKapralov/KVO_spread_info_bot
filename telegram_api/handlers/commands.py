from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import main_menu, menu_perpetual_futures, menu_quarterly_futures_and_stock
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
async def command_get_tickers_at_settings(callback: types.CallbackQuery, state: FSMContext):
    await MainInfo.type_info.set()
    async with state.proxy() as data:
        data['tickers'] = []
        data['coefficients'] = callback.data.split(';')[1].strip('()').replace(' ', '').split(',')
        tickers = callback.data.split(';')[0]
        data['perpetual'] = False
        for elem in tickers.split('_'):
            if elem[-1] == 'F':
                data['perpetual'] = True
            ticker = await get_ticker_future(elem)
            if not ticker:
                raise
            data['tickers'].append(ticker)
        if data['perpetual']:
            await callback.message.answer(BotAnswers.what_needs_sent(tickers), reply_markup=menu_perpetual_futures())
            return
        await callback.message.answer(BotAnswers.what_needs_sent(tickers),
                                      reply_markup=menu_quarterly_futures_and_stock())


@logger.catch()
async def register_handlers_commands(dp: Dispatcher):
    dp.register_callback_query_handler(command_back_main_menu, lambda callback: callback.data == 'main_menu',
                                       state='*')
    dp.register_message_handler(command_back_main_menu_message, commands=['main_menu'], state='*')
    dp.register_message_handler(command_start, commands=['start', 'старт', 'info', 'инфо', 'help', 'помощь'], state='*')
    dp.register_message_handler(command_start, Text(equals=['start', 'старт', 'info', 'инфо', 'help', 'помощь'],
                                                    ignore_case=True), state='*')
    dp.register_callback_query_handler(command_get_tickers_at_settings, state=MainInfo.type_ticker)


if __name__ == '__main__':
    logger.info('Running commands.py from module telegram_api/handlers')
