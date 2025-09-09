import pandas as pd
from loguru import logger


def calculate_correlation(data: pd.DataFrame):
    returns = data.pct_change().dropna()
    correlation_matrix = returns.corr()
    return correlation_matrix


def calculate_rolling_correlation(data: pd.DataFrame, window: int = 30):
    returns = data.pct_change().dropna()
    rolling_corr = returns.rolling(window=window).corr(returns)
    return rolling_corr


if __name__ == '__main__':
    logger.info('Running correlation_calculator.py from module utils')
