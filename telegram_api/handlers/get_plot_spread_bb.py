from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import menu_spread_type, menu_expiring_futures, menu_futures_and_stock
from telegram_api.essence.state_machine import MainInfo
from utils.data_frame_pandas import add_dataframe_spread_bb
from utils.spread_chart import add_plot_spread


async def get_spread_bollinger_bands(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await MainInfo.spread_type_bb.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


async def set_spread_type_bb(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        data['spread_type'] = callback.data
    await set_spread_bb(callback, state)


async def set_spread_bb(callback: types.CallbackQuery, state: FSMContext):
    time_frame_minutes = await db.get_setting('technical', 'time_frame_minutes')
    bollinger_deviation = await db.get_setting('technical', 'bollinger_deviation')
    bollinger_period = await db.get_setting('technical', 'bollinger_period')
    async with state.proxy() as data:
        df = await add_dataframe_spread_bb(
            time_frame_minutes,
            data['coefficients'],
            bollinger_deviation,
            bollinger_period,
            data['tickers'],
            data['spread_type']
        )
        if data['spread_type'] == 'money':
            spread_formula = f"{' - '.join(data['tickers'])}"
        else:
            spread_formula = f"{' / '.join(data['tickers'])}"
        plot = await add_plot_spread(df, spread_formula)
        await sending_bb(callback, data, plot)
    await MainInfo.type_info.set()


async def sending_bb(callback: types.CallbackQuery, data, plot):
    if data['expiring_futures']:
        reply_markup = menu_expiring_futures
    else:
        reply_markup = menu_futures_and_stock
    await callback.message.answer_photo(photo=plot,
                                        caption=BotAnswers.result_bb(data['tickers'], data['spread_type']),
                                        reply_markup=reply_markup())


async def register_handlers_command_bollinger_bands(dp: Dispatcher):
    dp.register_callback_query_handler(get_spread_bollinger_bands, lambda callback: callback.data == 'bollinger_bands',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_bb, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_bb)


if __name__ == '__main__':
    logger.info('Running get_plot_spread_bb.py from module telegram_api/handlers')
