from loguru import logger

from tinkoff_investments.get_figi_for_ticker import searching_ticker_figi
from tinkoff_investments.get_last_price import get_last_price


@logger.catch()
async def calculate_spread_money(tool_1: str, tool_2: str, coefficient_tool_1: int, coefficient_tool_2: int,
                                 accuracy: int = 3) -> float or None:
    try:
        return round(await get_price_for_figi(tool_1) * coefficient_tool_1 -
                     await get_price_for_figi(tool_2) * coefficient_tool_2, accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def calculate_spread_percent(tool_1: str, tool_2: str, coefficient_tool_1: int, coefficient_tool_2: int,
                                   accuracy: int = 2) -> float or None:
    try:
        return round((await get_price_for_figi(tool_1) * coefficient_tool_1 /
                      await get_price_for_figi(tool_2) * coefficient_tool_2 - 1) * 100, accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def calculate_spread_tool_3_money(tool_1: str, tool_2: str, tool_3: str, coefficient_tool_1: int,
                                        coefficient_tool_2: int, coefficient_tool_3: int,
                                        accuracy: int = 3) -> float or None:
    try:
        return round(await get_price_for_figi(tool_1) * coefficient_tool_1 *
                     await get_price_for_figi(tool_2) * coefficient_tool_2 -
                     await get_price_for_figi(tool_3) * coefficient_tool_3, accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def calculate_spread_tool_3_percent(tool_1: str, tool_2: str, tool_3: str, coefficient_tool_1: int,
                                        coefficient_tool_2: int, coefficient_tool_3: int,
                                        accuracy: int = 2) -> float or None:
    try:
        return round((await get_price_for_figi(tool_1) * coefficient_tool_1 *
                      await get_price_for_figi(tool_2) * coefficient_tool_2 /
                      await get_price_for_figi(tool_3) * coefficient_tool_3 - 1) * 100, accuracy)
    except ValueError and TypeError:
        return


@logger.catch()
async def get_price_for_figi(tool: str) -> float or None:
    ticker = await searching_ticker_figi(tool)
    if not ticker:
        return
    last_price = await get_last_price(ticker)
    if not last_price:
        return
    return float(last_price)


@logger.catch()
async def calculate_spread(data: dict) -> str or None:
    if data.get('tool_3') == 'GLDRUBF':
        if data['spread_type'] == 'percent':
            spread = await calculate_spread_tool_3_percent(
                data['tool_1'],
                data['tool_2'],
                data['tool_3'],
                data['coefficient_tool_1'],
                data['coefficient_tool_2'],
                data['coefficient_tool_3']
            )
            return spread
        spread = await calculate_spread_tool_3_money(
            data['tool_1'],
            data['tool_2'],
            data['tool_3'],
            data['coefficient_tool_1'],
            data['coefficient_tool_2'],
            data['coefficient_tool_3']
        )
        return spread
    if data['spread_type'] == 'percent':
        spread = await calculate_spread_percent(data['tool_1'], data['tool_2'], data['coefficient_tool_1'],
                                              data['coefficient_tool_2'])
        return spread
    elif data['spread_type'] == 'money':
        spread = await calculate_spread_money(data['tool_1'], data['tool_2'], data['coefficient_tool_1'],
                                              data['coefficient_tool_2'])
        return spread


if __name__ == '__main__':
    logger.info('Running calculate_spread.py from module utils')
