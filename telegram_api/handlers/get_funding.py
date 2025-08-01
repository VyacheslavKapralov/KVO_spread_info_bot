from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import menu_perpetual_futures, menu_direction_position
from telegram_api.essence.state_machine import MainInfo
from utils.calculate_funding import calculate_funding
from utils.calculate_spread import get_price_for_figi
from utils.decorators import check_int


async def get_funding(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MainInfo.volume_position.set()
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.funding(data['tickers']))
    await callback.message.answer(BotAnswers.position())


@check_int
async def set_position(message: types.Message, state: FSMContext):
    await MainInfo.direction_position.set()
    async with state.proxy() as data:
        data['position'] = int(message.text)
    await message.answer(BotAnswers.count_lots(message.text))
    await message.answer(BotAnswers.direction_position(), reply_markup=menu_direction_position())


async def set_direction_position(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['direction_position'] = callback.data
    await callback.message.answer(BotAnswers.set_direction_position(callback.data, data['tickers']))
    await get_funding_result(callback.message, state)


async def get_funding_result(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(BotAnswers.expectation_answer())
        data['funding'] = []
        for ticker in data['tickers']:
            if ticker[-1] == 'F':
                data['funding'].append((ticker, await calculate_funding(ticker)))
            else:
                data['funding'].append((ticker, 0))
    await sending_signal_funding(message, data)
    await MainInfo.type_info.set()


async def sending_signal_funding(message: types.Message, data: dict):
    volume_position = data['position']
    funding_first_ticker = data['funding'][0][1]
    funding_last_ticker = data['funding'][-1][1]
    if data['direction_position'] == 'short':
        result = (funding_first_ticker - funding_last_ticker) * volume_position
        if len(data['funding']) == 3:
            last_price_last_ticker = await get_price_for_figi(data['funding'][-1][0])
            result = (funding_first_ticker - funding_last_ticker * last_price_last_ticker) * volume_position
            volume_average_ticker = volume_position * last_price_last_ticker
            result -= data['funding'][1][1] * volume_average_ticker
    else:
        result = (-funding_first_ticker + funding_last_ticker) * volume_position
        if len(data['funding']) == 3:
            last_price_last_ticker = await get_price_for_figi(data['funding'][-1][0])
            result = (funding_first_ticker + funding_last_ticker * last_price_last_ticker) * volume_position
            volume_average_ticker = volume_position * last_price_last_ticker
            result += data['funding'][1][1] * volume_average_ticker
    await message.answer(BotAnswers().result_calculation_funding(round(result, 2), ' '.join(data['tickers'])),
                         reply_markup=menu_perpetual_futures())


async def register_handlers_command_funding(dp: Dispatcher):
    dp.register_callback_query_handler(get_funding, lambda callback: callback.data == 'funding',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_direction_position, lambda callback: callback.data in ['short', 'long'],
                                       state=MainInfo.direction_position)
    dp.register_message_handler(set_position, state=MainInfo.volume_position)


if __name__ == '__main__':
    logger.info('Running get_funding.py from module telegram_api/handlers')
