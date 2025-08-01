from loguru import logger
from datetime import datetime


def log_telegram_bot():
    """Настройки логирования."""

    now_datetime = datetime.now().strftime('%Y-%m-%d')
    logger.add(
        f'logs/files_logs/{now_datetime}.log',
        rotation='1 day',
        retention='7 days',
        encoding='utf-8',
        level='DEBUG',
        format='<green>{time}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{'
               'function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> '
    )


if __name__ == '__main__':
    logger.info('Running start_log.py from module logs')
