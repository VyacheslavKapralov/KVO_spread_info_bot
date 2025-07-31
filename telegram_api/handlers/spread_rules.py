import asyncio
from datetime import datetime

import pandas as pd
from aiogram import types
from loguru import logger

from database.database_bot import BotDatabase
from settings import PARAMETERS
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import menu_chancel
from tinkoff_investments.exceptions import FigiRetrievalError, DataRetrievalError
from utils.calculate_spread import calculate_spread
from utils.data_frame_pandas import add_dataframe_spread_bb
from utils.spread_chart import add_plot_spread
from utils.waiting_time import get_waiting_time


@logger.catch()
async def signal_line(data: dict, message: types.Message) -> float or None:
    tickers = data['tickers']
    coefficients = data['coefficients']
    spread_type = data['spread_type']
    type_alert = data['type_alert']
    max_spread = float(data['max_line'])
    min_spread = float(data['min_line'])
    signals = PARAMETERS['signals']
    non_stop = PARAMETERS['non_stop']
    count = 3
    while non_stop:
        if count == 0:
            await message.answer(BotAnswers.no_exchange_data())
            await asyncio.sleep(60)
            count = 3
        if signals == 0:
            await asyncio.sleep(600)
            signals = 3
        try:
            spread = await calculate_spread(coefficients, spread_type, tickers)
            if max_spread <= spread or spread <= min_spread:
                signals -= 1
                await send_signal(message, tickers, type_alert, spread, spread_type, min_line=min_spread,
                                  max_line=max_spread)
                await asyncio.sleep(15)
        except (FigiRetrievalError, DataRetrievalError) as error:
            logger.error(f"Error: {error}. {error.message}")
            count -= 1
        except asyncio.exceptions.TimeoutError as error:
            logger.error(f"Error: {error}")
        finally:
            await asyncio.sleep(1.5)


@logger.catch()
async def signal_bb(data: dict, message: types.Message) -> (pd.DataFrame, float) or None:
    time_frame = PARAMETERS['time_frame_minutes']
    bollinger_deviation = PARAMETERS['bollinger_deviation']
    bollinger_period = PARAMETERS['bollinger_period']
    none_stop = PARAMETERS['non_stop']
    tickers = data['tickers']
    coefficients = data['coefficients']
    spread_type = data['spread_type']
    type_alert = data['type_alert']
    count = 3
    first_condition = False
    while none_stop:
        if count == 0:
            await message.answer(BotAnswers.no_exchange_data())
            await asyncio.sleep(60)
            count = 3
        try:
            data_frame = await add_dataframe_spread_bb(time_frame, coefficients, bollinger_deviation, bollinger_period,
                                                       tickers, spread_type)
            spread = await calculate_spread(coefficients, spread_type, tickers)
            if first_condition or spread < data_frame['BBL'].iloc[-1]:
                first_condition = True
                wait_time = await get_waiting_time(time_frame)
                await asyncio.sleep(wait_time)
                data_frame = await add_dataframe_spread_bb(time_frame, coefficients, bollinger_deviation,
                                                           bollinger_period, tickers, spread_type)
                spread = await calculate_spread(coefficients, spread_type, tickers)
                if spread > data_frame['BBL'].iloc[-1]:
                    first_condition = False
                    plot = await add_plot_spread(data_frame, f"{' '.join(tickers)}")
                    await send_signal(message, tickers, type_alert, spread, spread_type, plot=plot)
            elif first_condition or spread > data_frame['BBU'].iloc[-1]:
                first_condition = True
                wait_time = await get_waiting_time(time_frame)
                await asyncio.sleep(wait_time)
                data_frame = await add_dataframe_spread_bb(time_frame, coefficients, bollinger_deviation,
                                                           bollinger_period, tickers, spread_type)
                spread = await calculate_spread(coefficients, spread_type, tickers)
                if spread < data_frame['BBU'].iloc[-1]:
                    first_condition = False
                    plot = await add_plot_spread(data_frame, f"{' '.join(tickers)}")
                    await send_signal(message, tickers, type_alert, spread, spread_type, plot=plot)
        except (FigiRetrievalError, DataRetrievalError) as error:
            logger.error(f"Error: {error}. {error.message}")
            count -= 1
        except asyncio.exceptions.TimeoutError as error:
            logger.error(f"Error: {error}")
        finally:
            wait_time = await get_waiting_time(time_frame)
            await asyncio.sleep(wait_time)


@logger.catch()
async def send_signal(message: types.Message, tickers: list, type_alert: str, spread: float, spread_type: str,
                      data_frame=None, min_line=0.0, max_line=0.0, plot=None):
    info = "Спред: "
    if spread_type == 'money':
        spread_formula = f"{' - '.join(tickers)}"
        ending_string = f' = {spread} руб.'
    else:
        spread_formula = f"{' / '.join(tickers)}"
        ending_string = f' = {spread}%'
    if type_alert == 'line_alert':
        info = spread_formula + ending_string + f" пересек одну из линий: [{min_line} --- {max_line}]"
        table_name = 'bot_lines_signals'
        await message.answer(BotAnswers.result_calculation_indicator(spread, 'Спред', tickers, spread_type),
                             reply_markup=menu_chancel())
    else:
        info += (f" пересек и вернулся за одну из линий Боллинджера: "
                 f"[{round(data_frame['BBL'].iloc[-1], 2)} --- {round(data_frame['BBU'].iloc[-1], 2)}]")
        table_name = 'bot_bb_signals'
        await message.answer(BotAnswers.bollinger_bands_answer(tickers, spread, spread_type))
        await message.answer_photo(photo=plot, caption=f"График для {spread_formula}", reply_markup=menu_chancel())
    await BotDatabase().db_write(
        date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        table_name=table_name,
        user_name=message.from_user.username,
        user_id=message.from_user.id,
        info=info
    )


if __name__ == '__main__':
    logger.info('Running spread_rules.py from module utils')
