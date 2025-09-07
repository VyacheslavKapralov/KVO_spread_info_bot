import pandas as pd
import pandas_ta as ta
from loguru import logger

from tinkoff_investments.candles_tinkoff import get_candles
from tinkoff_investments.figi_for_ticker import searching_ticker_figi


async def create_dataframe_spread(candle_interval: str, coefficients_list: list, tickers_list: list,
                                  spread_type: str) -> pd.DataFrame:
    data_frames = []
    for num, ticker in enumerate(tickers_list):
        candles = await add_candles_ticker(ticker, candle_interval)
        data_frame = await add_dataframe_pandas(candles)
        data_frames.append(await get_dataframe_with_coefficient(data_frame, float(coefficients_list[num])))
    result_data_frame = data_frames[0]
    for df in data_frames[1:]:
        result_data_frame = await get_dataframe_spread(result_data_frame, df, spread_type)
    if spread_type == 'percent':
        result_data_frame = await get_dataframe_with_coefficient(result_data_frame, 100, 1)
    return result_data_frame


async def get_dataframe_spread(data_frame_1: pd.DataFrame, data_frame_2: pd.DataFrame,
                               spread_type: str) -> pd.DataFrame:
    merged_df = pd.merge(data_frame_1, data_frame_2, on='Date', suffixes=('_1', '_2'))
    data_frame_3 = pd.DataFrame({'Date': merged_df['Date']})
    if spread_type == 'money':
        data_frame_3['Open'] = round(merged_df['Open_1'] - merged_df['Open_2'], 3)
        data_frame_3['High'] = round(merged_df['High_1'] - merged_df['High_2'], 3)
        data_frame_3['Low'] = round(merged_df['Low_1'] - merged_df['Low_2'], 3)
        data_frame_3['Close'] = round(merged_df['Close_1'] - merged_df['Close_2'], 3)
    elif spread_type == 'percent':
        data_frame_3['Open'] = round(merged_df['Open_1'] / merged_df['Open_2'], 4)
        data_frame_3['High'] = round(merged_df['High_1'] / merged_df['High_2'], 4)
        data_frame_3['Low'] = round(merged_df['Low_1'] / merged_df['Low_2'], 4)
        data_frame_3['Close'] = round(merged_df['Close_1'] / merged_df['Close_2'], 4)
    return data_frame_3


async def add_candles_ticker(ticker: str, candle_interval: str) -> list:
    figi = await searching_ticker_figi(ticker)
    return await get_candles(figi=figi, candle_interval=candle_interval)


async def add_dataframe_pandas(data: list) -> pd.DataFrame:
    data_frame = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data_frame['Date'] = pd.to_datetime(data_frame['Date'], format='%Y-%m-%d %H:%M:%S')
    data_frame['Date'] = data_frame['Date'] + pd.Timedelta(hours=3)
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    data_frame[numeric_columns] = data_frame[numeric_columns].apply(pd.to_numeric, errors='coerce')
    return data_frame


async def get_dataframe_with_coefficient(data_frame: pd.DataFrame, coefficient_1: float,
                                         coefficient_2: int = 0) -> pd.DataFrame:
    data_frame['Open'] = (data_frame['Open'] - coefficient_2) * coefficient_1
    data_frame['High'] = (data_frame['High'] - coefficient_2) * coefficient_1
    data_frame['Low'] = (data_frame['Low'] - coefficient_2) * coefficient_1
    data_frame['Close'] = (data_frame['Close'] - coefficient_2) * coefficient_1
    return data_frame


async def calculate_sma(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data['sma'] = data['Close'].rolling(window=period).mean()
    return data


async def calculate_ema(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data['ema'] = data['Close'].ewm(span=period, adjust=False).mean()
    return data


async def calculate_atr(data: pd.DataFrame, period: int) -> pd.DataFrame:
    data['atr'] = ta.atr(high=data['High'], low=data['Low'], close=data['Close'], length=period)
    return data


async def calculate_bollinger_bands_ta(data_frame: pd.DataFrame, deviation: int, period: int) -> pd.DataFrame:
    data_frame_bb = ta.bbands(close=data_frame['Close'], length=period, std=deviation)
    data_frame = pd.concat([data_frame, data_frame_bb], axis=1)
    return data_frame


async def calculate_bollinger_bands_ema(data_frame: pd.DataFrame, deviation: int, period: int) -> pd.DataFrame:
    ema = data_frame['Close'].ewm(span=period, adjust=False).mean()
    std = data_frame['Close'].rolling(window=period).std()
    data_frame["BBL"] = ema - (deviation * std)
    data_frame["BBM"] = ema
    data_frame["BBU"] = ema + (deviation * std)
    return data_frame


async def add_dataframe_spread_bb(candle_interval: str, coefficients_list: list, deviation: int, period: int,
                                  tickers_list: list, spread_type: str) -> pd.DataFrame:
    data_frame = await create_dataframe_spread(candle_interval, coefficients_list, tickers_list, spread_type)
    data_frame = await calculate_bollinger_bands_ema(data_frame, deviation, period)
    data_frame.dropna(inplace=True)
    start_time = data_frame['Date'].iloc[-1] - pd.Timedelta(days=3)
    data_frame = data_frame.loc[data_frame['Date'] >= start_time]
    data_frame = data_frame.set_index('Date')
    return data_frame


if __name__ == '__main__':
    logger.info('Running data_frame_pandas.py from module utils')
