from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from moex_api.get_data_moex import get_stock_data
from telegram_api.essence.keyboards import correlation_menu
from telegram_api.essence.state_machine import CorrelationStates
from utils.correlation_calculator import calculate_correlation



async def cmd_correlation(message: types.Message):
    await message.answer(
        "📊 <b>Калькулятор корреляции MOEX</b>\n\n"
        "Введите тикеры инструментов через запятую (например: SBER, GAZP, LKOH):",
        parse_mode="HTML"
    )
    await CorrelationStates.waiting_for_tickers.set()


async def process_tickers(message: types.Message, state: FSMContext):
    tickers = [ticker.strip().upper() for ticker in message.text.split(',')]
    if len(tickers) < 2:
        await message.answer("❌ Нужно ввести хотя бы 2 тикера!")
        return
    await state.update_data(tickers=tickers)
    await message.answer("📅 Выберите период для анализа:", reply_markup=correlation_menu(), parse_mode="HTML")
    await CorrelationStates.waiting_for_period.set()


async def process_period(message: types.Message, state: FSMContext):
    period_map = {
        "1 месяц": 30,
        "3 месяца": 90,
        "6 месяцев": 180,
        "1 год": 365
    }
    if message.text not in period_map:
        await message.answer("❌ Пожалуйста, выберите период из предложенных вариантов")
        return
    days = period_map[message.text]
    user_data = await state.get_data()
    tickers = user_data['tickers']
    await message.answer("⏳ Загружаю данные и рассчитываю корреляцию...")
    try:
        data = await get_stock_data(tickers, days)
        if not data:
            await message.answer("❌ Не удалось получить данные для указанных тикеров")
            return
        correlation_matrix = calculate_correlation(data)
        response = f"📊 <b>Корреляция за {message.text}:</b>\n\n"
        for i, ticker1 in enumerate(tickers):
            for j, ticker2 in enumerate(tickers):
                if i < j:
                    corr = correlation_matrix.loc[ticker1, ticker2]
                    response += f"🔗 {ticker1} - {ticker2}: {corr:.3f}\n"
        response += "\n📈 <b>Интерпретация:</b>\n"
        response += "1.0 - полная положительная корреляция\n"
        response += "0.0 - отсутствие корреляции\n"
        response += "-1.0 - полная отрицательная корреляция\n\n"
        response += "💡 <i>Значения выше 0.7 считаются сильной корреляцией</i>"
        await message.answer(response, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    finally:
        await state.finish()


def register_correlation_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_correlation, lambda callback: callback.data == "correlation")
    dp.register_message_handler(process_tickers, state=CorrelationStates.waiting_for_tickers)
    dp.register_message_handler(process_period, state=CorrelationStates.waiting_for_period)


if __name__ == '__main__':
    logger.info('Running correlation.py from module telegram_api/handlers')
