from datetime import timedelta

import pandas as pd
import pandas_ta as ta
from loguru import logger

from tinkoff_investments.get_candles import get_candles
from tinkoff_investments.get_figi_for_ticker import searching_ticker_figi


@logger.catch()
async def add_dataframe_pandas(data: list) -> pd.DataFrame:
    data_frame = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data_frame['Date'] = pd.to_datetime(data_frame['Date'], format='%Y-%m-%d %H:%M:%S')
    data_frame['Date'] = data_frame['Date'] + pd.Timedelta(hours=3)
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    data_frame[numeric_columns] = data_frame[numeric_columns].apply(pd.to_numeric, errors='coerce')
    return data_frame


# @logger.catch()
# async def filling_time_gaps(data_frame: pd.DataFrame, period: str = '5m') -> pd.DataFrame:
#     period_mapping = {
#         'm': 'minutes',
#         'h': 'hours',
#         'd': 'days',
#         'w': 'weeks',
#         'M': 'months'
#     }
#     period_value = int(period[:-1])
#     period_unit = period_mapping[period[-1]]
#     time_delta = timedelta(**{period_unit: period_value})
#     all_dates = pd.date_range(start=data_frame['Date'].min(), end=data_frame['Date'].max(), freq=time_delta)
#     complete_data_frame = pd.DataFrame(all_dates, columns=['Date'])
#     data_frame = complete_data_frame.merge(data_frame, on='Date', how='left')
#     data_frame = data_frame[~((data_frame['Date'].dt.time > pd.to_datetime('23:45').time()) |
#                               (data_frame['Date'].dt.time < pd.to_datetime('07:00').time()))]
#     data_frame.reset_index(drop=True, inplace=True)
#     for i in range(1, len(data_frame)):
#         if pd.isna(data_frame.at[i, 'Open']):
#             for col in ['Open', 'High', 'Low', 'Close']:
#                 data_frame.at[i, col] = data_frame.at[i - 1, 'Close']
#     return data_frame


@logger.catch()
async def calculate_sma(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data['sma'] = data['Close'].rolling(window=period).mean()
    return data


@logger.catch()
async def calculate_ema(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data['ema'] = data['Close'].ewm(span=period, adjust=False).mean()
    return data


@logger.catch()
async def calculate_atr(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data['atr'] = ta.atr(high=data['High'], low=data['Low'], close=data['Close'], length=period)
    return data


@logger.catch()
async def calculate_bollinger_bands_ta(data_frame: pd.DataFrame, deviation: int, period: int) -> pd.DataFrame:
    data_frame_bb = ta.bbands(close=data_frame['Close'], length=period, std=deviation)
    data_frame = pd.concat([data_frame, data_frame_bb], axis=1)
    return data_frame


@logger.catch()
async def calculate_bollinger_bands_ema(data_frame: pd.DataFrame, deviation: int, period: int) -> pd.DataFrame:
    ema = data_frame['Close'].ewm(span=period, adjust=False).mean()
    std = data_frame['Close'].rolling(window=period).std()
    data_frame["BBL"] = ema - (deviation * std)
    data_frame["BBM"] = ema
    data_frame["BBU"] = ema + (deviation * std)
    return data_frame


@logger.catch()
async def get_dataframe_spread(data: dict, data_frame_1: pd.DataFrame, data_frame_2: pd.DataFrame,
                               coefficient_tool_1: int, coefficient_tool_2: int) -> pd.DataFrame:
    merged_df = pd.merge(data_frame_1, data_frame_2, on='Date', suffixes=('_1', '_2'))
    data_frame_3 = pd.DataFrame({'Date': merged_df['Date']})
    if data['spread_type'] == 'money':
        data_frame_3['Open'] = round(
            merged_df['Open_1'] * coefficient_tool_1 - merged_df['Open_2'] * coefficient_tool_2, 3)
        data_frame_3['High'] = round(
            merged_df['High_1'] * coefficient_tool_1 - merged_df['High_2'] * coefficient_tool_2, 3)
        data_frame_3['Low'] = round(
            merged_df['Low_1'] * coefficient_tool_1 - merged_df['Low_2'] * coefficient_tool_2, 3)
        data_frame_3['Close'] = round(
            merged_df['Close_1'] * coefficient_tool_1 - merged_df['Close_2'] * coefficient_tool_2, 3)
    elif data['spread_type'] == 'percent':
        data_frame_3['Open'] = round((merged_df['Open_1'] * coefficient_tool_1 /
                                      merged_df['Open_2'] * coefficient_tool_2 - 1) * 100, 3)
        data_frame_3['High'] = round((merged_df['High_1'] * coefficient_tool_1 /
                                      merged_df['High_2'] * coefficient_tool_2 - 1) * 100, 3)
        data_frame_3['Low'] = round((merged_df['Low_1'] * coefficient_tool_1 /
                                     merged_df['Low_2'] * coefficient_tool_2 - 1) * 100, 3)
        data_frame_3['Close'] = round((merged_df['Close_1'] * coefficient_tool_1 /
                                       merged_df['Close_2'] * coefficient_tool_2 - 1) * 100, 3)
    return data_frame_3


@logger.catch()
async def add_candles_tool(ticker: str, candle_interval: str) -> list:
    figi = await searching_ticker_figi(ticker)
    return await get_candles(figi=figi, candle_interval=candle_interval)


@logger.catch()
async def add_dataframe_spread_bb(data: dict, candle_interval: str, coefficient_tool_1: int, coefficient_tool_2: int,
                                  deviation: int, period: int) -> pd.DataFrame:
    data_frame = await create_dataframe_spread(data, candle_interval, coefficient_tool_1, coefficient_tool_2)
    data_frame = await calculate_bollinger_bands_ta(data_frame, deviation, period)
    data_frame = data_frame.set_index('Date')
    data_frame.dropna(inplace=True)
    return data_frame


@logger.catch()
async def create_dataframe_spread(data: dict, candle_interval: str, coefficient_tool_1: int,
                                  coefficient_tool_2: int) -> pd.DataFrame:
    candles_1 = await add_candles_tool(data['tool_1'], candle_interval)
    candles_2 = await add_candles_tool(data['tool_2'], candle_interval)
    data_frame_1 = await add_dataframe_pandas(candles_1)
    data_frame_2 = await add_dataframe_pandas(candles_2)
    return await get_dataframe_spread(data, data_frame_1, data_frame_2, coefficient_tool_1, coefficient_tool_2)


if __name__ == '__main__':
    logger.info('Running data_frame_pandas.py from module utils')
