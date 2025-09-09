from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from moex_api.get_data_moex import get_stock_data, get_all_stocks_data
from telegram_api.essence.keyboards import correlation_menu, correlation_all_menu, correlation_months, \
    correlation_database
from telegram_api.essence.state_machine import CorrelationStates
from utils.correlation_calculator import calculate_correlation


async def cmd_correlation(callback: types.CallbackQuery):
    await callback.message.answer("Выберите тип анализа корреляции:", reply_markup=correlation_menu())


async def cmd_correlation_custom(callback: types.CallbackQuery):
    await callback.message.answer("Введите тикеры инструментов через запятую (например: SBER, GAZP, LKOH):")
    await CorrelationStates.waiting_for_tickers.set()


async def cmd_correlation_all(callback: types.CallbackQuery):
    await callback.message.answer("Выберите период для анализа всех акций:", reply_markup=correlation_all_menu())
    await CorrelationStates.waiting_for_all_period.set()


async def process_tickers(message: types.Message, state: FSMContext):
    tickers = [ticker.strip().upper() for ticker in message.text.split(',')]
    if len(tickers) < 2:
        await message.answer("❌ Нужно ввести хотя бы 2 тикера!")
        return
    await state.update_data(tickers=tickers)
    await message.answer("Выберите период для анализа:", reply_markup=correlation_months())
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


async def process_all_period(callback: types.CallbackQuery, state: FSMContext):
    period_map = {
        "all_1_month": 30,
        "all_3_month": 90,
        "all_6_month": 180,
        "all_1_year": 365
    }
    days = period_map[callback.data]
    await callback.message.answer("Загружаю данные по всем акциям... Это может занять несколько минут.")
    data = await get_all_stocks_data(days)
    if data is None or data.empty:
        await callback.message.answer("❌ Не удалось получить данные по акциям")
        await state.finish()
        return
    await callback.message.answer(f"Получено данных по {len(data.columns)} акциям. Рассчитываю корреляцию...")
    correlation_matrix = calculate_correlation(data)
    if correlation_matrix is None:
        await callback.message.answer("❌ Не удалось рассчитать корреляцию")
        await state.finish()
        return
    strong_correlations = []
    tickers = correlation_matrix.columns.tolist()
    for i, ticker1 in enumerate(tickers):
        for j, ticker2 in enumerate(tickers):
            if i < j:
                corr = correlation_matrix.loc[ticker1, ticker2]
                if abs(corr) >= 0.75:
                    strong_correlations.append({
                        'ticker1': ticker1,
                        'ticker2': ticker2,
                        'correlation': corr,
                        'type': 'positive' if corr > 0 else 'negative'
                    })
    if not strong_correlations:
        await callback.message.answer("🤷‍♂️ Не найдено пар акций с корреляцией ≥ 0.75 или ≤ -0.75")
        await state.finish()
        return
    if strong_correlations:
        success = await db.save_correlations(days, strong_correlations)
        if not success:
            logger.warning("Не удалось сохранить корреляции в базу данных")
    strong_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    header = f"<b>Сильные корреляции ({days} дней):</b>\n\n"
    header += f"Найдено {len(strong_correlations)} сильных корреляций\n"
    header += "🟢 ПРЯМ - прямая корреляция (≥ 0.75)\n"
    header += "🔴 ОБР - обратная корреляция (≤ -0.75)\n\n"
    table_parts = []
    current_part = "<code>"
    current_part += "АКЦИЯ 1    АКЦИЯ 2    КОРР.     ТИП\n"
    current_part += "-------------------------------------\n"
    for pair in strong_correlations:
        ticker1 = pair['ticker1'].ljust(8)
        ticker2 = pair['ticker2'].ljust(8)
        corr = f"{pair['correlation']:.3f}".ljust(8)
        corr_type = "🟢 ПРЯМ" if pair['type'] == 'positive' else "🔴 ОБР"
        line = f"{ticker1} {ticker2} {corr} {corr_type}\n"
        if len(current_part) + len(line) > 3500:
            current_part += "</code>"
            table_parts.append(current_part)
            current_part = "<code>"
            current_part += "АКЦИЯ 1    АКЦИЯ 2    КОРР.     ТИП\n"
            current_part += "-------------------------------------\n"
            current_part += line
        else:
            current_part += line
    if current_part != "<code>":
        current_part += "</code>"
        table_parts.append(current_part)
    await callback.message.answer(header, parse_mode="HTML")
    for i, part in enumerate(table_parts, 1):
        if i == 1:
            message_text = f"<b>Часть {i}/{len(table_parts)}:</b>\n{part}"
        else:
            message_text = f"<b>Часть {i}/{len(table_parts)}:</b>\n{part}"
        await callback.message.answer(message_text, parse_mode="HTML")
    await state.finish()


async def show_saved_correlations(callback: types.CallbackQuery):
    await callback.message.answer("Выберите период для просмотра сохраненных корреляций:",
                                  reply_markup=correlation_database())


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
        await callback.message.answer(f"Нет сохраненных корреляций для периода {days} дней")
        return
    response = f"<b>Сохраненные корреляции ({days} дней):</b>\n\n"
    response += f"Дата расчета: {correlations[0]['calculation_date']}\n"
    response += f"Найдено пар: {len(correlations)}\n\n"
    response += "<code>"
    response += "АКЦИЯ 1    АКЦИЯ 2    КОРР.     ТИП\n"
    response += "-------------------------------------\n"
    for pair in correlations:
        ticker1 = pair['ticker1'].ljust(8)
        ticker2 = pair['ticker2'].ljust(8)
        corr = f"{pair['correlation']:.3f}".ljust(8)
        corr_type = "🟢 ПРЯМ" if pair['type'] == 'positive' else "🔴 ОБР"
        response += f"{ticker1} {ticker2} {corr} {corr_type}\n"
    response += "</code>"
    await callback.message.answer(response, parse_mode="HTML")


async def register_correlation_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_correlation, lambda callback: callback.data == "correlation")
    dp.register_callback_query_handler(cmd_correlation_custom, lambda callback: callback.data == "correlation_custom")
    dp.register_callback_query_handler(cmd_correlation_all, lambda callback: callback.data == "correlation_all")
    dp.register_message_handler(process_tickers, state=CorrelationStates.waiting_for_tickers)
    dp.register_callback_query_handler(process_period, lambda callback: callback.data in
                                       ["1_month", "3_month", "6_month", "1_year"],
                                       state=CorrelationStates.waiting_for_period)
    dp.register_callback_query_handler(process_all_period, lambda callback: callback.data in
                                       ["all_1_month", "all_3_month", "all_6_month", "all_1_year"],
                                       state=CorrelationStates.waiting_for_all_period)
    dp.register_callback_query_handler(show_saved_correlations, lambda callback: callback.data == "correlation_history")
    dp.register_callback_query_handler(process_saved_correlations, lambda callback: callback.data.startswith("saved_"))


if __name__ == '__main__':
    logger.info('Running correlation.py from module telegram_api/handlers')
