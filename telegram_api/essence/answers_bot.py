from aiogram import types
from loguru import logger


class BotAnswers:

    def __init__(self, user: types.user.User):
        self.user = user

    def start_message(self) -> str:
        return (f"Добро пожаловать, {self.user.first_name}.\n"
                f"Я бот для взаимодействии с биржей для расчета информации по спреду различных пар."
                )

    @staticmethod
    def to_developing() -> str:
        return 'В разработке...'

    # @staticmethod
    # def tool_1():
    #     return 'Введите тикер первого инструмента'
    #
    # @staticmethod
    # def tool_2():
    #     return 'Введите тикер второго инструмента'

    @staticmethod
    def spread_type():
        return 'Выберите в каком виде отображать спред'

    @staticmethod
    def position():
        return 'Напишите какой размер позиции в лотах'

    @staticmethod
    def funding():
        return 'Фандинг для инструмента'

    @staticmethod
    def spread_moex(tool_1, tool_2, spread_type):
        if spread_type == 'percent':
            return f"Спред {tool_1}/{tool_2}%"
        elif spread_type == 'money':
            return f"Спред {tool_1}-{tool_2} руб."


    @staticmethod
    def spread_bb_moex(tool_1, tool_2, spread_type):
        if spread_type == 'percent':
            return f"График спреда с линиями Боллинджера {tool_1}/{tool_2}%"
        elif spread_type == 'money':
            return f"График спреда с линиями Боллинджера {tool_1}-{tool_2} руб."

    @staticmethod
    def spread_sma_moex(tool_1, tool_2, spread_type):
        if spread_type == 'percent':
            return f"Простая скользящая средняя спреда {tool_1}/{tool_2}%"
        elif spread_type == 'money':
            return f"Простая скользящая средняя спреда {tool_1}-{tool_2} руб."

    @staticmethod
    def spread_ema_moex(tool_1, tool_2, spread_type):
        if spread_type == 'percent':
            return f"Экспоненциальная скользящая средняя спреда {tool_1}/{tool_2}%"
        elif spread_type == 'money':
            return f"Экспоненциальная скользящая средняя спреда {tool_1}-{tool_2} руб."

    @staticmethod
    def spread_atr_moex(tool_1, tool_2, spread_type) -> str:
        if spread_type == 'percent':
            return f"Среднее отклонение спреда {tool_1}/{tool_2}%"
        elif spread_type == 'money':
            return f"Среднее отклонение спреда {tool_1}-{tool_2} руб."

    @staticmethod
    def what_needs_sent() -> str:
        return 'Выберите какую информацию нужно прислать'

    @staticmethod
    def pare_need_info() -> str:
        return 'Выберите пару для которой нужна информация'

    # @staticmethod
    # def percentage_deposit_answer() -> str:
    #     return 'Какой процент от свободного депозита использовать?'
    #
    # @staticmethod
    # def strategy_answer() -> str:
    #     return 'Выберите стратегию'
    #
    # @staticmethod
    # def time_frame_answer() -> str:
    #     return 'Выберите тайм-фрейм'
    #
    # @staticmethod
    # def stop_ema_answer() -> str:
    #     return 'Введите период стоп линии основанной на экспоненциальной скользящей средней'
    #
    # @staticmethod
    # def period_fractal_answer() -> str:
    #     return 'Задайте период фракталов'
    #
    @staticmethod
    def grid_max_price_answer() -> str:
        return 'Укажите верхнюю границу спреда'

    @staticmethod
    def grid_min_price_answer() -> str:
        return 'Укажите нижнюю границу спреда'
    #
    # @staticmethod
    # def grid_mesh_threads_answer() -> str:
    #     return 'Укажите шаг сетки'
    #
    # @staticmethod
    # def grid_starting_price_answer() -> str:
    #     return 'Укажите цену при достижении которой бот начнет свою работу'
    #
    @staticmethod
    def check_float_answer(text) -> str:
        return f'Неверное число: {text}\nДолжно быть целым или вещественным числом, а также записано через точку'

    @staticmethod
    def check_int_answer(text) -> str:
        return f'Неверное число: {text}\nЧисло должно быть целым'

    # @staticmethod
    # def deposit_verification_answer(data: dict) -> str:
    #     return f"На бирже {data['exchange']} нет свободных средств: {data['client_depo']} USDT"
    #
    # @staticmethod
    # def client_depo_answer(client_depo: float) -> str:
    #     return f"Не удалось получить баланс клиента: {client_depo}"
    #
    # @staticmethod
    # def price_verification_answer(data: dict) -> str:
    #     return f"Неверно указана цена. Шаг цены равен: {data['accuracy_tick_size']} USDT"
    #
    # @staticmethod
    # def validation_price_range_answer(data: dict) -> str:
    #     return (f"Проверьте корректность введенных параметров сетки.\n"
    #             f"Верхняя цена сетки: {data['upper_price']}\n"
    #             f"Нижняя цена сетки: {data['lower_price']}\n"
    #             f"Цена запуска бота: {data['start_price']}\n")
    #
    # @staticmethod
    # def check_coin_name_answer(text) -> str:
    #     return f"Проверьте корректность введенного названия тикера - {text}"
    #
    # @staticmethod
    # def checking_feasibility_strategy_answer(data: dict) -> str:
    #     return f"Не хватает выделенного депозита для сетки.\nПересмотрите параметры сетки:\n{data}"

    @staticmethod
    def command_chancel_answer() -> str:
        return 'Остановка бота'

    @staticmethod
    def command_back() -> str:
        return 'Возвращаюсь в главное меню'

    # @staticmethod
    # def get_ema_stop_period_answer() -> str:
    #     return 'Введите период быстрой экспоненциальной скользящей средней'
    #
    # @staticmethod
    # def get_ema_period_answer() -> str:
    #     return 'Введите период медленной простой скользящей средней'
    #
    # @staticmethod
    # def get_period_fractal_answer() -> str:
    #     return 'Нужно применять откат цены от цены последнего фрактала?'
    #
    # @staticmethod
    # def get_rollback_usd_fractal_answer() -> str:
    #     return 'Введите на сколько USDT планируется откат'
    #
    # @staticmethod
    # def get_rollback_percent_fractal_answer() -> str:
    #     return 'Введите на сколько процентов планируется откат'
    #
    # @staticmethod
    # def measure_stop_loss_fractal_answer() -> str:
    #     return 'В чем измерять размер stop-loss?'
    #
    # @staticmethod
    # def stop_loss_selection_fractal_answer() -> str:
    #     return 'Введите размер stop-loss'
    #
    # @staticmethod
    # def measure_take_profit_fractal_answer() -> str:
    #     return 'В чем измерять размер take-profit?'
    #
    # @staticmethod
    # def take_profit_selection_fractal_answer() -> str:
    #     return 'Введите размер take-profit'
    #
    # @staticmethod
    # def get_multiplicity_atr_fractal() -> str:
    #     return 'Введите множитель (целое число) значения ATR для установки take-profit'
    #
    # @staticmethod
    # def open_order_answer(order) -> str:
    #     return f"Открыт ордер:\n{order}"

    # @staticmethod
    # def signal_search_stopped_answer() -> str:
    #     return 'Поиск сигналов остановлен'

    # @staticmethod
    # def how_match_results_answer() -> str:
    #     return 'Сколько вывести инструментов?'
    #
    # @staticmethod
    # def how_sort_coins_answer() -> str:
    #     return 'Как сортировать монеты?'
    #
    # @staticmethod
    # def time_interval_answer() -> str:
    #     return 'За какой промежуток времени искать?'

    @staticmethod
    def expectation_answer() -> str:
        return 'Это займет некоторое время. Ожидайте'

    # @staticmethod
    # def results_volatile_answer() -> str:
    #     return 'Получены следующие результаты по волатильности'
    #
    # @staticmethod
    # def start_strategy_message_answer(data: dict) -> str:
    #     return (
    #         f"Начинаю поиск сигналов на бирже {data['exchange']}\n"
    #         f"По стратегии {data['strategy']}\n"
    #         f"Параметры поиска:\n"
    #         f"Секция биржи: {data['exchange_type']}\n"
    #         f"Тикер инструмента: {data['coin_name']}\n"
    #         f"Тайм-фрейм: {data['time_frame']}\n"
    #         f"Используемый депозит: {data['percentage_deposit']}% от общей суммы\n"
    #     )
    #
    # @staticmethod
    # def strategy_signal_message_answer(data: dict, signal: str) -> str:
    #     return (
    #         f"Получен сигнал '{signal}' на инструменте {data['coin_name']},\n"
    #         f"По стратегии: {data['strategy']}\n"
    #         f"На бирже: {data['exchange']}\n"
    #     )
    #
    # @staticmethod
    # def start_ema_strategy_answer(data: dict) -> str:
    #     return (
    #         f"Stop_EMA: {data['stop_line']}\n"
    #         f"EMA: {data['ema']}\n"
    #         f"MA: {data['ma']}"
    #     )
    #
    # @staticmethod
    # def start_fractal_strategy_answer(data: dict) -> str:
    #     return (
    #         f"Period: {data['period']}\n"
    #         f"Stop_loss: {data['stop_loss']}\n"
    #         f"Take_profit: {data['take_profit']}"
    #     )
    #
    # @staticmethod
    # def start_grid_message_answer(data: dict) -> str:
    #     return (
    #         f"Расставляю сетку ордеров\n"
    #         f"Секция биржи: {data['exchange_type']}\n"
    #         f"Тикер инструмента: {data['coin_name']}\n"
    #         f"Верхняя граница: {data['upper_price']}\n"
    #         f"Нижняя граница: {data['lower_price']}\n"
    #         f"Шаг сетки: {data['mesh_threads']}\n"
    #         f"Цена старта бота: {data['start_price']}\n"
    #         f"Используемый депозит: {data['percentage_deposit']}% от свободной суммы\n"
    #     )


if __name__ == '__main__':
    logger.info('Running answers.py from module telegram_api/essence')
