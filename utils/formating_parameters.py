from loguru import logger
from settings import EXPIRATION_MONTHS, VALID_TIMEFRAMES


def format_settings_display(settings: dict, category: str) -> str:
    if category == 'pairs':
        response = ""
        pairs = settings
        for group_name, group_pairs in pairs.items():
            response += f"  {group_name}:\n"
            for num, (symbols, coefficients) in enumerate(group_pairs):
                response += f"    [{num}] {symbols} × {coefficients}\n"
            response += "\n"
        return response
    elif isinstance(settings, dict):
        return '\n'.join([f"{key}: {val}" for key, val in settings.items()])
    else:
        return str(settings)


def format_expiration_months() -> str:
    return '\n'.join([f"{key}: {value}" for key, value in EXPIRATION_MONTHS.items()])


def format_available_timeframes() -> str:
    return ', '.join(VALID_TIMEFRAMES)


if __name__ == '__main__':
    logger.info('Running formating_parameters.py from module utils')
