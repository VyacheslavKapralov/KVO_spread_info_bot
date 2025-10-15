import asyncio
from datetime import datetime

import pandas as pd
from aiogram import types
from loguru import logger

from database.database_bot import db
from telegram_api.essence.answers_bot import bot_answers
from telegram_api.essence.keyboards import back_main_menu
from tinkoff_investments.exceptions import FigiRetrievalError, DataRetrievalError
from utils.calculate_spread import calculate_spread
from utils.data_frame_pandas import add_dataframe_spread_bb
from utils.fair_price_futures import get_fair_spread_futures_currency
from utils.spread_chart import add_plot_spread
from utils.waiting_time import get_waiting_time


async def signal_line(data: dict, message: types.Message, monitor_id: str, spread_monitor) -> None:
    tickers = data['tickers']
    coefficients = data['coefficients']
    spread_type = data['spread_type']
    max_spread = float(data['max_line'])
    min_spread = float(data['min_line'])
    count = 3
    in_alert_zone = False
    while True:
        if not await spread_monitor.is_monitor_active(message.from_user.id, monitor_id):
            logger.info(f"Мониторинг {monitor_id} остановлен")
            return
        if count == 0:
            await message.answer(bot_answers.no_exchange_data())
            await asyncio.sleep(60)
            count = 3
        try:
            spread = await calculate_spread(coefficients, spread_type, tickers)
            if not in_alert_zone and (max_spread <= spread or spread <= min_spread):
                in_alert_zone = True
                await send_signal_line(message, tickers, spread, spread_type, min_line=min_spread, max_line=max_spread)
            if in_alert_zone and min_spread < spread < max_spread:
                in_alert_zone = False
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(15)
        except (FigiRetrievalError, DataRetrievalError) as error:
            logger.error(f"Error: {error}. {error.message}")
            count -= 1
        except asyncio.exceptions.TimeoutError as error:
            logger.error(f"Error: {error}")


async def signal_bb(data: dict, callback: types.CallbackQuery, monitor_id: str, spread_monitor) -> None:
    if data.get('time_frame'):
        time_frame = data['time_frame']
    else:
        time_frame = await db.get_setting('technical', 'time_frame_minutes')
    bollinger_deviation = await db.get_setting('technical', 'bollinger_deviation')
    if data.get('period'):
        bollinger_period = data['period']
    else:
        bollinger_period = await db.get_setting('technical', 'bollinger_period')
    tickers = data['tickers']
    coefficients = data['coefficients']
    spread_type = data['spread_type']
    count = 3
    first_condition = False
    while True:
        if not await spread_monitor.is_monitor_active(callback.from_user.id, monitor_id):
            logger.info(f"Мониторинг {monitor_id} остановлен")
            return
        if count == 0:
            await callback.message.answer(bot_answers.no_exchange_data())
            count = 3
        wait_time = await get_waiting_time(time_frame)
        await asyncio.sleep(wait_time)
        try:
            data_frame = await add_dataframe_spread_bb(
                time_frame, coefficients, bollinger_deviation, bollinger_period, tickers, spread_type
            )
            spread = await calculate_spread(coefficients, spread_type, tickers)
            if not first_condition and (spread <= data_frame['BBL'].iloc[-1] or spread >= data_frame['BBU'].iloc[-1]):
                first_condition = True
                plot = await add_plot_spread(data_frame, f"{' '.join(tickers)}")
                await send_signal_bb(callback, data_frame, tickers, spread, spread_type, plot)
                continue
            if first_condition and (spread > data_frame['BBL'].iloc[-1] or spread < data_frame['BBU'].iloc[-1]):
                first_condition = False
                await callback.message.answer(bot_answers.return_range_bb(data_frame, spread, spread_type, tickers))
        except (FigiRetrievalError, DataRetrievalError) as error:
            logger.error(f"Error: {error}. {error.message}")
            count -= 1
        except asyncio.exceptions.TimeoutError as error:
            logger.error(f"Error: {error}")


async def signal_deviation_fair_spread(data: dict, message: types.Message, monitor_id: str, spread_monitor) -> None:
    tickers = data['tickers']
    coefficients = data['coefficients']
    spread_type = data['spread_type']
    deviation_fair_spread = float(data['deviation_fair_spread'])
    count = 3
    in_alert_zone = False
    while True:
        if not await spread_monitor.is_monitor_active(message.from_user.id, monitor_id):
            logger.info(f"Мониторинг {monitor_id} остановлен")
            return
        if count == 0:
            await message.answer(bot_answers.no_exchange_data())
            await asyncio.sleep(60)
            count = 3
        try:
            spread = await calculate_spread(coefficients, spread_type, tickers)
            fair_spread = await get_fair_spread_futures_currency(tickers, spread_type)
            if abs(fair_spread - spread) >= deviation_fair_spread and not in_alert_zone:
                await send_signal_deviation_fair_spread(message, tickers, spread, spread_type, fair_spread)
                in_alert_zone = True
            elif in_alert_zone and abs(fair_spread - spread) < deviation_fair_spread:
                in_alert_zone = False
            await asyncio.sleep(60)
        except (FigiRetrievalError, DataRetrievalError) as error:
            logger.error(f"Error: {error}. {error.message}")
            count -= 1
        except asyncio.exceptions.TimeoutError as error:
            logger.error(f"Error: {error}")


async def send_signal_line(message: types.Message, tickers: list, spread: float, spread_type: str, min_line=0.0,
                           max_line=0.0):
    info = bot_answers.lines_signal_answer(min_line, max_line, spread, spread_type, tickers)
    table_name = 'bot_lines_signals'
    await message.answer(info, reply_markup=back_main_menu())
    await db.db_write(
        date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        table_name=table_name,
        user_name=message.from_user.username,
        user_id=message.from_user.id,
        info=info
    )


async def send_signal_bb(callback: types.CallbackQuery, data_frame: pd.DataFrame, tickers: list, spread: float,
                         spread_type: str, plot):
    info = bot_answers.bollinger_bands_signal_answer(data_frame, spread, spread_type, tickers)
    table_name = 'bot_bb_signals'
    await callback.message.answer_photo(
        photo=plot,
        caption=info,
        reply_markup=back_main_menu()
    )
    await db.db_write(
        date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        table_name=table_name,
        user_name=callback.from_user.username,
        user_id=callback.from_user.id,
        info=info
    )


async def send_signal_deviation_fair_spread(message: types.Message, tickers: list, spread: float, spread_type: str,
                                            fair_spread: float):
    info = bot_answers.deviation_fair_spread_signal_answer(fair_spread, spread, spread_type, tickers)
    table_name = 'bot_deviation_fair_spread_signals'
    await message.answer(bot_answers.deviation_fair_spread_signal_answer(info), reply_markup=back_main_menu())
    await db.db_write(
        date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        table_name=table_name,
        user_name=message.from_user.username,
        user_id=message.from_user.id,
        info=info
    )


if __name__ == '__main__':
    logger.info('Running spread_rules.py from module utils')
