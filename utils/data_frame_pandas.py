import pandas as pd
import pandas_ta as ta
from loguru import logger

from settings import PARAMETERS
from tinkoff_investments.get_candles import get_candles
from tinkoff_investments.get_figi_for_ticker import searching_ticker_figi


@logger.catch()
async def add_dataframe_pandas(data: list) -> pd.DataFrame:
    data_frame = pd.DataFrame(data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data_frame['Date'] = pd.to_datetime(data_frame['Date'], format='%Y-%m-%d %H:%M:%S')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    data_frame[numeric_columns] = data_frame[numeric_columns].apply(pd.to_numeric, errors='coerce')
    return data_frame


@logger.catch()
async def calculate_sma(data: pd.DataFrame, period: int = PARAMETERS['sma_period']):
    # data['sma'] = ta.sma(data['Close'], length=period)
    data['sma'] = data['Close'].rolling(window=period).mean()
    return data


@logger.catch()
async def calculate_ema(data: pd.DataFrame, period: int = PARAMETERS['ema_period']):
    # data['ema'] = ta.ema(data['Close'], length=period)
    data['ema'] = data['Close'].ewm(span=period, adjust=False).mean()
    return data

@logger.catch()
async def calculate_atr(data: pd.DataFrame, period: int = PARAMETERS['atr_period']):
    data['atr'] = ta.atr(high=data['High'], low=data['Low'], close=data['Close'], length=period)
    return data


@logger.catch()
async def calculate_bollinger_bands(data: pd.DataFrame):
    # data_frame = (ta.bbands(close=data['Close'], length=PARAMETERS['bollinger_period'], std=PARAMETERS['bollinger_deviation']))
    # (
    #     data[f"BBL_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"],
    #     data[f"BBM_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"],
    #     data[f"BBU_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"]
    # ) = (
    #     data_frame[f"BBL_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"],
    #     data_frame[f"BBM_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"],
    #     data_frame[f"BBU_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"]
    # )
    sma = data['Close'].rolling(window=PARAMETERS['bollinger_period']).mean()
    std = data['Close'].rolling(window=PARAMETERS['bollinger_period']).std()
    data[f"BBL_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"] = sma - (PARAMETERS['bollinger_deviation'] * std)
    data[f"BBM_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"] = sma
    data[f"BBU_{PARAMETERS['bollinger_period']}_{PARAMETERS['bollinger_deviation']}"] = sma + (PARAMETERS['bollinger_deviation'] * std)
    return data


@logger.catch()
async def get_dataframe_spread(data_1: pd.DataFrame, data_2: pd.DataFrame):
    data_frame_1 = await add_dataframe_pandas(data_1)
    data_frame_2 = await add_dataframe_pandas(data_2)
    data_frame_3 = pd.DataFrame({
        'Date': data_frame_1['Date'],
        'Open': data_frame_1['Open'] - data_frame_2['Open'],
        'High': data_frame_1['High'] - data_frame_2['High'],
        'Low': data_frame_1['Low'] - data_frame_2['Low'],
        'Close': data_frame_1['Close'] - data_frame_2['Close']
    })
    data_frame_3['Date'] = pd.to_datetime(data_frame_3['Date'], format='%Y-%m-%d %H:%M:%S')
    data_frame_3.dropna(inplace=True)
    data_frame_3 = data_frame_3.set_index('Date')
    return data_frame_3


@logger.catch()
async def add_dataframe_tools(ticker_1: str, ticker_2: str):
    figi_1: str = await searching_ticker_figi(ticker_1)
    figi_2: str = await searching_ticker_figi(ticker_2)
    candles_1: list = await get_candles(figi=figi_1, candle_interval=PARAMETERS['time_frame_minutes'])
    candles_2: list = await get_candles(figi=figi_2, candle_interval=PARAMETERS['time_frame_minutes'])
    return candles_1, candles_2


@logger.catch()
async def add_dataframe_spread_bb(ticker_1: str, ticker_2: str):
    candles_1, candles_2 = await add_dataframe_tools(ticker_1, ticker_2)
    data_frame: pd.DataFrame = await get_dataframe_spread(candles_1, candles_2)
    data_frame: pd.DataFrame = await calculate_bollinger_bands(data_frame)
    data_frame.dropna(inplace=True)
    return data_frame


@logger.catch()
async def create_dataframe_spread(ticker_1, ticker_2):
    candles_1, candles_2 = await add_dataframe_tools(ticker_1, ticker_2)
    data_frame = await get_dataframe_spread(candles_1, candles_2)
    return data_frame


if __name__ == '__main__':
    logger.info('Running data_frame_pandas.py from module utils')
