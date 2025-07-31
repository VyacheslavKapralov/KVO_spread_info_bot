from loguru import logger

class ExchangeError(Exception):
    pass

class DataRetrievalError(ExchangeError):
    def __init__(self, message="Не удалось получить данные от сервера биржи."):
        self.message = message
        super().__init__(self.message)

class FigiRetrievalError(ExchangeError):
    def __init__(self, message="Не удалось получить figi инструмента."):
        self.message = message
        super().__init__(self.message)


if __name__ == "__main__":
    logger.info('Running exceptions.py from module tinkoff_investments')
