from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from moex_api.get_data_moex import get_stock_data, get_all_stocks_data
from telegram_api.essence.answers_bot import bot_answers
from telegram_api.essence.keyboards import correlation_menu, correlation_all_menu, correlation_months, \
    correlation_database
from telegram_api.essence.state_machine import CorrelationStates
from utils.correlation_calculator import calculate_correlation, get_strong_correlation, get_table_parts_correlation


async def cmd_correlation(callback: types.CallbackQuery):
    await callback.message.answer(bot_answers.type_correlation(), reply_markup=correlation_menu())


async def cmd_correlation_custom(callback: types.CallbackQuery):
    await callback.message.answer(bot_answers.enter_tickers())
    await CorrelationStates.waiting_for_tickers.set()


async def cmd_correlation_all(callback: types.CallbackQuery):
    await callback.message.answer(bot_answers.choose_period_all_stocks(), reply_markup=correlation_all_menu())
    await CorrelationStates.waiting_for_all_period.set()


async def process_tickers(message: types.Message, state: FSMContext):
    tickers = [ticker.strip().upper() for ticker in message.text.split(',')]
    if len(tickers) < 2:
        await message.answer(bot_answers.error_entry_stocks())
        return
    await state.update_data(tickers=tickers)
    await message.answer(bot_answers.choose_period(), reply_markup=correlation_months())
    await CorrelationStates.waiting_for_period.set()


async def process_period(callback: types.CallbackQuery, state: FSMContext):
    period_map = {
        "1_month": 30,
        "3_month": 90,
        "6_month": 180,
        "1_year": 365
    }
    days = period_map[callback.data]
    user_data = await state.get_data()
    tickers = user_data['tickers']
    data = await get_stock_data(tickers, days)
    if data is None:
        await callback.message.answer(bot_answers.error_get_data_tickers())
        return
    correlation_matrix = await calculate_correlation(data)
    await callback.message.answer(bot_answers.correlation_answer(days, tickers, correlation_matrix))
    await state.finish()


async def process_all_period(callback: types.CallbackQuery, state: FSMContext):
    period_map = {
        "all_1_month": 30,
        "all_3_month": 90,
        "all_6_month": 180,
        "all_1_year": 365
    }
    days = period_map[callback.data]
    await callback.message.answer(bot_answers.wait_get_data_tickers())
    data = await get_all_stocks_data(days)
    if data is None or data.empty:
        await callback.message.answer(bot_answers.error_get_data_tickers())
        await state.finish()
        return
    await callback.message.answer(bot_answers.success_get_data_tickers(len(data.columns)))
    correlation_matrix = await calculate_correlation(data)
    if correlation_matrix is None:
        await callback.message.answer(bot_answers.failed_calculate_correlation())
        await state.finish()
        return
    strong_correlations = await get_strong_correlation(correlation_matrix)
    if not strong_correlations:
        await callback.message.answer(bot_answers.no_pair_correlation())
        await state.finish()
        return
    if strong_correlations:
        await db.save_correlations(days, strong_correlations)
    strong_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    table_parts = await get_table_parts_correlation(strong_correlations)
    await callback.message.answer(bot_answers.header_correlation_answer(days, len(strong_correlations)),
                                  parse_mode="HTML")
    for num, part in enumerate(table_parts, 1):
        await callback.message.answer(bot_answers.correlation_pair_answer(num, len(table_parts), part),
                                      parse_mode="HTML")
    await state.finish()


async def show_saved_correlations(callback: types.CallbackQuery):
    await callback.message.answer(bot_answers.choose_period_history(), reply_markup=correlation_database())


async def process_saved_correlations(callback: types.CallbackQuery):
    period_map = {
        "saved_30": 30,
        "saved_90": 90,
        "saved_180": 180,
        "saved_365": 365
    }
    days = period_map[callback.data]
    correlations = await db.get_latest_correlations(days)
    if not correlations:
        await callback.message.answer(bot_answers.no_saved_correlation(days))
        return
    await callback.message.answer(bot_answers.correlation_history_answer(days, correlations), parse_mode="HTML")


async def register_correlation_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_correlation, lambda callback: callback.data == "correlation")
    dp.register_callback_query_handler(cmd_correlation_custom, lambda callback: callback.data == "correlation_custom")
    dp.register_callback_query_handler(cmd_correlation_all, lambda callback: callback.data == "correlation_all")
    dp.register_message_handler(process_tickers, state=CorrelationStates.waiting_for_tickers)
    dp.register_callback_query_handler(process_period, lambda callback: callback.data in
                                                                        ["1_month", "3_month", "6_month", "1_year"],
                                       state=CorrelationStates.waiting_for_period)
    dp.register_callback_query_handler(process_all_period, lambda callback: callback.data in
                                                                            ["all_1_month", "all_3_month",
                                                                             "all_6_month", "all_1_year"],
                                       state=CorrelationStates.waiting_for_all_period)
    dp.register_callback_query_handler(show_saved_correlations, lambda callback: callback.data == "correlation_history")
    dp.register_callback_query_handler(process_saved_correlations, lambda callback: callback.data.startswith("saved_"))


if __name__ == '__main__':
    logger.info('Running correlation.py from module telegram_api/handlers')
