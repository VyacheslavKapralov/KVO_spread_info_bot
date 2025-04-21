from loguru import logger


class BotAnswers:

    @staticmethod
    def start_message(first_name: str) -> str:
        return (f"Добро пожаловать, {first_name}.\n"
                f"Я бот для взаимодействии с биржей для расчета информации по спреду различных пар.")

    @staticmethod
    def to_developing() -> str:
        return 'В разработке...'

    @staticmethod
    def not_get_ticker() -> str:
        return ('При попытке получить актуальный тикер фьючерсного контракта не удалось связаться с биржей. '
                'Повторите попытку позже.')

    @staticmethod
    def result_calculation_indicator(number: float, indicator_type: str, tickers: list, spread_type: str) -> str:
        if spread_type == 'money':
            return f"{indicator_type}: {' - '.join(tickers)} = {number} руб."
        return f"{indicator_type}: {' / '.join(tickers)} = {number} %"

    @staticmethod
    def result_calculation_funding(number: float, ticker: str) -> str:
        return f"Фандинг инструмента {ticker} = {number} руб."

    @staticmethod
    def result_fair_price_futures(number: float, ticker: str) -> str:
        return f"Справедливая цена фьючерса {ticker}: {number}"

    @staticmethod
    def spread_type() -> str:
        return 'Выберите в каком виде отображать спред'

    @staticmethod
    def position() -> str:
        return 'Напишите какой размер позиции в лотах'

    @staticmethod
    def funding() -> str:
        return 'Фандинг для инструмента'

    @staticmethod
    def spread_moex(ticker_1: str, ticker_2: str, spread_type: str) -> str:
        if spread_type == 'percent':
            return f"Спред {ticker_1}/{ticker_2}%"
        elif spread_type == 'money':
            return f"Спред {ticker_1}-{ticker_2} руб."

    @staticmethod
    def what_needs_sent(text) -> str:
        return f'Выберите какую информацию нужно прислать для {text}'

    @staticmethod
    def pare_need_info() -> str:
        return 'Выберите пару для которой нужна информация'

    @staticmethod
    def result_bb(ticker_1: str, ticker_2: str, ticker_3: str = None) -> str:
        if ticker_3:
            return f"График с полосами Боллинджера для {ticker_1} * {ticker_2} к {ticker_3}"
        return f"График с полосами Боллинджера для {ticker_1} к {ticker_2}"

    @staticmethod
    def grid_max_price_answer() -> str:
        return 'Укажите верхнюю границу спреда'

    @staticmethod
    def grid_min_price_answer() -> str:
        return 'Укажите нижнюю границу спреда'

    @staticmethod
    def check_float_answer(text) -> str:
        return f'Неверное число: {text}\nДолжно быть целым или вещественным числом, а также записано через точку'

    @staticmethod
    def check_int_answer(text) -> str:
        return f'Неверное число: {text}\nЧисло должно быть целым'

    @staticmethod
    def command_chancel_answer() -> str:
        return 'Остановка бота'

    @staticmethod
    def command_back_main_menu() -> str:
        return 'Возвращаюсь в главное меню'

    @staticmethod
    def expectation_answer() -> str:
        return 'Это займет некоторое время. Ожидайте'


if __name__ == '__main__':
    logger.info('Running answers.py from module telegram_api/essence')
