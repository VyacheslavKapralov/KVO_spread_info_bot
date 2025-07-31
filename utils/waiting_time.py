import datetime
from loguru import logger


@logger.catch()
async def get_waiting_time(time_frame_minutes: str) -> int or None:
    try:
        time = int(time_frame_minutes[:-1])
        now = datetime.datetime.now()
        start_minute = int(now.minute) // time * time
        start_time = now.replace(minute=start_minute, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(minutes=time)
        result = round((end_time - now).total_seconds())
        return result
    except KeyError:
        logger.error("Ключ 'time_frame_minutes' отсутствует в параметрах.")
    except IndexError:
        logger.error("Строка 'time_frame_minutes' пуста.")
    except ValueError:
        logger.error("Ошибка преобразования: значение не является целым числом.")
    except TypeError:
        logger.error("Неправильный тип данных для 'time_frame_minutes'.")
    return 15

if __name__ == '__main__':
    logger.info('Running waiting_time.py from module utils')
