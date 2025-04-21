from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_perpetual_futures, menu_quarterly_futures_and_stock
from settings import PARAMETERS
from utils.data_frame_pandas import add_dataframe_spread_bb
from utils.spread_chart import add_plot_spread


@logger.catch()
async def bollinger_bands(callback: types.CallbackQuery):
    await MainInfo.spread_type_bb.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


@logger.catch()
async def set_spread_type_bb(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await get_spread_bb(callback, state)


@logger.catch()
async def get_spread_bb(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.expectation_answer())
    df = await add_dataframe_spread_bb(
        PARAMETERS['time_frame_minutes'], data, PARAMETERS['bollinger_deviation'], PARAMETERS['bollinger_period']
    )
    plot = await add_plot_spread(df, ' '.join(data['tickers']))
    await sending_signal_bb(callback, data, plot)
    await MainInfo.type_info.set()


@logger.catch()
async def sending_signal_bb(callback: types.CallbackQuery, data, plot):
    if data['perpetual']:
        reply_markup = menu_perpetual_futures
    else:
        reply_markup = menu_quarterly_futures_and_stock
    await callback.message.answer_photo(photo=plot,
                                        caption=BotAnswers.result_bb(data['tickers'][0], data['tickers'][1]),
                                        reply_markup=reply_markup())


@logger.catch()
async def register_handlers_command_bollinger_bands(dp: Dispatcher):
    dp.register_callback_query_handler(bollinger_bands, lambda callback: callback.data == 'bollinger_bands',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_bb, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_bb)


if __name__ == '__main__':
    logger.info('Running get_plot_spread_bb.py from module telegram_api/handlers')
