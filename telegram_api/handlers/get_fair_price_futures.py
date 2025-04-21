from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_perpetual_futures
from utils.fair_price_futures import get_fair_price_futures


@logger.catch()
async def fair_price(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if len(data['tickers']) == 2:
            ticker = data['tickers'][0]
            data[f"fair_price_{ticker}"] = await get_fair_price_futures(ticker)
            await callback.message.answer(
                BotAnswers().result_fair_price_futures(data[f"fair_price_{ticker}"], ticker),
                reply_markup=menu_perpetual_futures())
        elif len(data['tickers']) == 3:
            for num in range(len(data['tickers']) - 1):
                data[f"fair_price_{data['tickers'][num]}"] = await get_fair_price_futures(data['tickers'][num])
                await callback.message.answer(
                    BotAnswers().result_fair_price_futures(data[f"fair_price_{data['tickers'][num]}"],
                                                           data['tickers'][num]),
                    reply_markup=menu_perpetual_futures())
    await MainInfo.type_info.set()


@logger.catch()
async def register_handlers_command_fair_price(dp: Dispatcher):
    dp.register_callback_query_handler(fair_price, lambda callback: callback.data == 'fair_price',
                                       state=MainInfo.type_info)


if __name__ == '__main__':
    logger.info('Running get_fair_price_futures.py from module telegram_api/handlers')
