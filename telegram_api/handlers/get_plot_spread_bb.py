from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from settings import PARAMETERS
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import menu_spread_type, menu_perpetual_futures, menu_quarterly_futures_and_stock
from telegram_api.essence.state_machine import MainInfo
from utils.data_frame_pandas import add_dataframe_spread_bb
from utils.spread_chart import add_plot_spread


async def bollinger_bands(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await MainInfo.spread_type_bb.set()
    async with state.proxy() as data:
        await callback.message.answer(f"График с линиями Боллинджера спреда для {' '.join(data['tickers'])}")
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_bb(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    if callback.data == 'money':
        text = 'Значение спреда в валюте'
    else:
        text = 'Значение спреда в процентах'
    await callback.message.answer(text)
    await get_spread_bb(callback, state)


async def get_spread_bb(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.expectation_answer())
    df = await add_dataframe_spread_bb(
        PARAMETERS['time_frame_minutes'],
        data['coefficients'],
        PARAMETERS['bollinger_deviation'],
        PARAMETERS['bollinger_period'],
        data['tickers'],
        data['spread_type']
    )
    if data['spread_type'] == 'money':
        spread_formula = f"{' - '.join(data['tickers'])}"
    else:
        spread_formula = f"{' / '.join(data['tickers'])}"
    plot = await add_plot_spread(df, spread_formula)
    await sending_signal_bb(callback, data, plot)
    await MainInfo.type_info.set()


async def sending_signal_bb(callback: types.CallbackQuery, data, plot):
    if data['perpetual']:
        reply_markup = menu_perpetual_futures
    else:
        reply_markup = menu_quarterly_futures_and_stock
    await callback.message.answer_photo(photo=plot,
                                        caption=BotAnswers.result_bb(data['tickers'], data['spread_type']),
                                        reply_markup=reply_markup())


async def register_handlers_command_bollinger_bands(dp: Dispatcher):
    dp.register_callback_query_handler(bollinger_bands, lambda callback: callback.data == 'bollinger_bands',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_bb, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_bb)


if __name__ == '__main__':
    logger.info('Running get_plot_spread_bb.py from module telegram_api/handlers')
