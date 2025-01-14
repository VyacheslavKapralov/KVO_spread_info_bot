import pandas as pd
import pandas_ta as ta
from loguru import logger

from tinkoff_investments.get_candles import get_candles
from tinkoff_investments.get_figi_for_ticker import searching_ticker_figi


@logger.catch()
async def add_dataframe_pandas(data: list) -> pd.DataFrame:
    data_frame = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data_frame['Date'] = pd.to_datetime(data_frame['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    data_frame = data_frame.dropna(subset=['Date'])
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    data_frame[numeric_columns] = data_frame[numeric_columns].apply(pd.to_numeric, errors='coerce')
    return data_frame


@logger.catch()
async def calculate_sma(data: pd.DataFrame, period: int):
    data['sma'] = data['Close'].rolling(window=period).mean()
    return data


@logger.catch()
async def calculate_ema(data: pd.DataFrame, period: int):
    data['ema'] = data['Close'].ewm(span=period, adjust=False).mean()
    return data


@logger.catch()
async def calculate_atr(data: pd.DataFrame, period: int):
    data['atr'] = ta.atr(high=data['High'], low=data['Low'], close=data['Close'], length=period)
    return data


@logger.catch()
async def calculate_bollinger_bands(data: pd.DataFrame, deviation: int, period: int):
    sma = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    data[f"BBL_{period}_{deviation}"] = sma - (deviation * std)
    data[f"BBM_{period}_{deviation}"] = sma
    data[f"BBU_{period}_{deviation}"] = sma + (deviation * std)
    return data


@logger.catch()
async def get_dataframe_spread(data: dict, data_1: pd.DataFrame, data_2: pd.DataFrame):
    data_frame_1 = await add_dataframe_pandas(data_1)
    data_frame_2 = await add_dataframe_pandas(data_2)
    data_frame_3 = await get_dataframe_3(data, data_frame_1, data_frame_2)
    return data_frame_3


@logger.catch()
async def get_dataframe_3(data: dict, data_frame_1: pd.DataFrame, data_frame_2: pd.DataFrame, coefficient_tool_1: int,
                          coefficient_tool_2: int):
    merged_df = pd.merge(data_frame_1, data_frame_2, on='Date', suffixes=('_1', '_2'))
    data_frame_3 = pd.DataFrame({'Date': merged_df['Date']})
    if data['spread_type'] == 'money':
        data_frame_3['Open'] = merged_df['Open_1'] * coefficient_tool_1 - merged_df['Open_2'] * coefficient_tool_2
        data_frame_3['High'] = merged_df['High_1'] * coefficient_tool_1 - merged_df['High_2'] * coefficient_tool_2
        data_frame_3['Low'] = merged_df['Low_1'] * coefficient_tool_1 - merged_df['Low_2'] * coefficient_tool_2
        data_frame_3['Close'] = merged_df['Close_1'] * coefficient_tool_1 - merged_df['Close_2'] * coefficient_tool_2
    elif data['spread_type'] == 'percent':
        data_frame_3['Open'] = (merged_df['Open_1'] * coefficient_tool_1 /
                                merged_df['Open_2'] * coefficient_tool_2 - 1) * 100
        data_frame_3['High'] = (merged_df['High_1'] * coefficient_tool_1 /
                                merged_df['High_2'] * coefficient_tool_2 - 1) * 100
        data_frame_3['Low'] = (merged_df['Low_1'] * coefficient_tool_1 /
                               merged_df['Low_2'] * coefficient_tool_2 - 1) * 100
        data_frame_3['Close'] = (merged_df['Close_1'] * coefficient_tool_1 /
                                 merged_df['Close_2'] * coefficient_tool_2 - 1) * 100
    return data_frame_3


@logger.catch()
async def add_candles_tool(ticker: str, candle_interval: str):
    figi = await searching_ticker_figi(ticker)
    return await get_candles(figi=figi, candle_interval=candle_interval)


@logger.catch()
async def add_dataframe_spread_bb(data: dict, candle_interval: str, coefficient_tool_1: int, coefficient_tool_2: int,
                                  deviation: int, period: int):
    data_frame = await create_dataframe_spread(data, candle_interval, coefficient_tool_1, coefficient_tool_2)
    data_frame = await calculate_bollinger_bands(data_frame, deviation, period)
    data_frame = data_frame.set_index('Date')
    data_frame.dropna(inplace=True)
    return data_frame


@logger.catch()
async def create_dataframe_spread(data: dict, candle_interval: str, coefficient_tool_1: int, coefficient_tool_2: int):
    candles_1 = await add_candles_tool(data['tool_1'], candle_interval)
    candles_2 = await add_candles_tool(data['tool_2'], candle_interval)
    data_frame_1 = await add_dataframe_pandas(candles_1)
    data_frame_2 = await add_dataframe_pandas(candles_2)
    data_frame_3 = await get_dataframe_3(data, data_frame_1, data_frame_2, coefficient_tool_1, coefficient_tool_2)
    return data_frame_3


if __name__ == '__main__':
    logger.info('Running data_frame_pandas.py from module utils')
