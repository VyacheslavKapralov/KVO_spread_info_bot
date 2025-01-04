import datetime
from loguru import logger


@logger.catch()
def get_waiting_time(time: int) -> int:
    now = datetime.datetime.now()
    start_minute = int(now.minute) // time * time
    start_time = now.replace(minute=start_minute, second=0, microsecond=0)
    end_time = start_time + datetime.timedelta(minutes=time)
    result = round((end_time - now).total_seconds())
    # logger.info(f"Ожидание: {result}")
    return result


if __name__ == '__main__':
    logger.info('Running waiting_time.py from module utils')