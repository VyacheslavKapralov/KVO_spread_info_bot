import pandas as pd
from loguru import logger


async def calculate_correlation(data: pd.DataFrame) -> pd.DataFrame:
    returns = data.pct_change().dropna()
    correlation_matrix = returns.corr()
    return correlation_matrix


async def calculate_rolling_correlation(data: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    returns = data.pct_change().dropna()
    rolling_corr = returns.rolling(window=window).corr(returns)
    return rolling_corr


async def get_strong_correlation(correlation_matrix: pd.DataFrame, min_correlation: float = 0.75) -> list:
    strong_correlations = []
    tickers = correlation_matrix.columns.tolist()
    for i, ticker1 in enumerate(tickers):
        for j, ticker2 in enumerate(tickers):
            if i < j:
                corr = correlation_matrix.loc[ticker1, ticker2]
                if abs(corr) >= min_correlation:
                    strong_correlations.append({
                        'ticker1': ticker1,
                        'ticker2': ticker2,
                        'correlation': corr,
                        'type': 'positive' if corr > 0 else 'negative'
                    })
    return strong_correlations


async def get_table_parts_correlation(strong_correlations: list) -> list:
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
    return table_parts


if __name__ == '__main__':
    logger.info('Running correlation_calculator.py from module utils')
