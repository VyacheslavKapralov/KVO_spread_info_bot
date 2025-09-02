from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from moex_api.get_data_moex import get_ticker_data
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import menu_expiring_futures, menu_spread_type
from telegram_api.essence.state_machine import MainInfo
from utils.calculate_spread import calculate_spread
from utils.fair_price_futures import get_fair_price_futures_currency, get_fair_spread_futures_currency


async def fair_price(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    async with state.proxy() as data:
        for ticker in data['tickers']:
            ticker_data = await get_ticker_data(ticker)
            for elem in ticker_data["description"]["data"]:
                if elem[0] == 'TYPE' and elem[2] == 'futures':
                    data[f"fair_price_{ticker}"] = await get_fair_price_futures_currency(ticker_data)
                    if data[f"fair_price_{ticker}"]:
                        await callback.message.answer(
                            BotAnswers().result_fair_price_futures(data[f"fair_price_{ticker}"], ticker)
                        )
    await callback.message.answer(BotAnswers().what_needs_sent(' '.join(data['tickers'])),
                                  reply_markup=menu_expiring_futures())


async def fair_spread(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await MainInfo.fair_spread_type.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_fair_spread(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await get_fair_spread(callback, state)


async def get_fair_spread(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['fair_spread'] = await get_fair_spread_futures_currency(data['tickers'], data['spread_type'])
        data['spread'] = await calculate_spread(data['coefficients'], data['spread_type'], data['tickers'])
        await callback.message.answer(
            BotAnswers().result_fair_spread_futures(data['fair_spread'], data['spread'], data['tickers'],
                                                    data['spread_type']),
            reply_markup=menu_expiring_futures()
        )
    await MainInfo.type_info.set()


async def register_handlers_command_fair_price(dp: Dispatcher):
    dp.register_callback_query_handler(fair_price, lambda callback: callback.data == 'fair_price',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(fair_spread, lambda callback: callback.data == 'fair_spread',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_fair_spread,
                                       lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.fair_spread_type)


if __name__ == '__main__':
    logger.info('Running get_fair_price_futures.py from module telegram_api/handlers')
