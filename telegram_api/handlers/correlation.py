from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from moex_api.get_data_moex import get_stock_data
from telegram_api.essence.keyboards import correlation_menu
from telegram_api.essence.state_machine import CorrelationStates
from utils.correlation_calculator import calculate_correlation


async def cmd_correlation(callback: types.CallbackQuery):
    await callback.message.answer("Введите тикеры инструментов через запятую (например: SBER, GAZP, LKOH):")
    await CorrelationStates.waiting_for_tickers.set()


async def process_tickers(message: types.Message, state: FSMContext):
    tickers = [ticker.strip().upper() for ticker in message.text.split(',')]
    if len(tickers) < 2:
        await message.answer("❌ Нужно ввести хотя бы 2 тикера!")
        return
    await state.update_data(tickers=tickers)
    await message.answer("📅 Выберите период для анализа:", reply_markup=correlation_menu())
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
        await callback.message.answer("Не удалось получить данные для указанных тикеров")
        return
    correlation_matrix = calculate_correlation(data)
    response = f"Корреляция за {period_map[callback.data]} дней:\n"
    for i, ticker1 in enumerate(tickers):
        for j, ticker2 in enumerate(tickers):
            if i < j:
                corr = correlation_matrix.loc[ticker1, ticker2]
                response += f"{ticker1} - {ticker2}: {corr:.2f}\n"
    await callback.message.answer(response)
    await state.finish()


async def register_correlation_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_correlation, lambda callback: callback.data == "correlation")
    dp.register_message_handler(process_tickers, state=CorrelationStates.waiting_for_tickers)
    dp.register_callback_query_handler(process_period, lambda callback: callback.data in
                                       ["1_month", "3_month", "6_month", "1_year"],
                                       state=CorrelationStates.waiting_for_period)


if __name__ == '__main__':
    logger.info('Running correlation.py from module telegram_api/handlers')
