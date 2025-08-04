from loguru import logger


class BotAnswers:

    @staticmethod
    def start_message(first_name: str) -> str:
        return (f"Добро пожаловать, {first_name}.\n"
                f"Я бот для взаимодействии с биржей для расчета информации по спреду различных пар инструментов.")

    @staticmethod
    def main_menu():
        return 'Выберите пункт:'

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
        return f"{indicator_type}: {' / '.join(tickers)} = {number}%"

    @staticmethod
    def bollinger_bands_answer(tickers: list, spread: float, spread_type: str) -> str:
        if spread_type == 'money':
            return f"Возврат спреда в канал линий Боллинджера.\nСпред: {' - '.join(tickers)} = {spread} руб."
        return f"Возврат спреда в канал линий Боллинджера.\nСпред: {' / '.join(tickers)} = {spread}%"

    @staticmethod
    def result_calculation_funding(number: float, ticker: str) -> str:
        return f"Фандинг инструмента {ticker} = {number} руб."

    @staticmethod
    def result_fair_price_futures(number: float, ticker: str) -> str:
        return f"Справедливая цена фьючерса {ticker}: {number}"

    @staticmethod
    def spread_type() -> str:
        return 'Выберите в каком виде отображать спред:'

    @staticmethod
    def position() -> str:
        return 'Напишите какой размер позиции в лотах:'

    @staticmethod
    def direction_position():
        return 'Выберите в каком направлении взят спред:'

    @staticmethod
    def funding() -> str:
        return 'Фандинг для инструмента'

    @staticmethod
    def what_needs_sent(text) -> str:
        return f'Выберите какую информацию нужно прислать для {text}:'

    @staticmethod
    def what_alert_set(text) -> str:
        return f'Выберите какое оповещение установить для {text}:'

    @staticmethod
    def pare_need_info() -> str:
        return 'Выберите пару для которой нужна информация:'

    @staticmethod
    def result_bb(tickers: list, spread_type: str) -> str:
        if spread_type == 'money':
            return f"График с полосами Боллинджера для {' - '.join(tickers)}"
        return f"График с полосами Боллинджера для {' / '.join(tickers)}"

    @staticmethod
    def grid_max_price_answer() -> str:
        return 'Укажите верхнюю границу спреда:'

    @staticmethod
    def grid_min_price_answer() -> str:
        return 'Укажите нижнюю границу спреда:'

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
        return 'Меню инструментов:'

    @staticmethod
    def command_alerts() -> str:
        return 'Выберите инструмент, на который нужно поставить оповещение:'

    @staticmethod
    def expectation_answer() -> str:
        return 'Это займет некоторое время. Ожидайте'

    @staticmethod
    def no_exchange_data() -> str:
        return 'Не удается получить от биржи данные по инструментам. Повторная попытка через 60 секунд.'

    @staticmethod
    def not_admin() -> str:
        return 'Вы не являетесь администратором'

    @staticmethod
    def what_edit() -> str:
        return 'Что нужно отредактировать?'

    @staticmethod
    def not_users_database() -> str:
        return 'В базе данных нет информации о пользователях.'

    @staticmethod
    def allowed_users() -> str:
        return 'Допущенные пользователи:'

    @staticmethod
    def unauthorized_users() -> str:
        return 'Недопущенные пользователи:'

    @staticmethod
    def user_database(date: str, user_name: str, user_id: int) -> str:
        return f"Date: {date}\nUser name: {user_name}\nUser ID: {user_id}"

    @staticmethod
    def not_info_database() -> str:
        return 'В базе данных нет информации о сигналах.'

    @staticmethod
    def info_signal_database(date: str, info: str, user_name: str, user_id: int) -> str:
        return f"Date: {date}\nUser name: {user_name}\nUser ID: {user_id}\nInfo: {info}\n"

    @staticmethod
    def access_bot():
        return 'Выберите, что нужно сделать с доступом к боту:'

    @staticmethod
    def get_user_id():
        return 'Напишите id пользователя:'

    @staticmethod
    def get_user_nik():
        return 'Напишите никнейм пользователя:'

    @staticmethod
    def success_add_user_db(user_id: int, user_nik: str):
        return f"Пользователь {user_nik} с номером id: {user_id} успешно добавлен."

    @staticmethod
    def choice_action_access():
        return 'Выберите дальнейшее действие:'

    @staticmethod
    def confirm_deletion(user_id: str):
        return f"Подтвердите удаление пользователя id: {user_id}"

    @staticmethod
    def stop_admin_panel():
        return 'Панель администратора закрыта.'


if __name__ == '__main__':
    logger.info('Running answers.py from module telegram_api/essence')
