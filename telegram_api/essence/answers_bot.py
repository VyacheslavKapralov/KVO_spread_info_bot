import pandas as pd
from loguru import logger

from settings import TECHNICAL_SETTINGS, VALID_TIMEFRAMES
from utils.formating_parameters import format_settings_display, format_expiration_months


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
    def bollinger_bands_signal_answer(text: str) -> str:
        return text

    @staticmethod
    def lines_signal_answer(text: str) -> str:
        return text

    @staticmethod
    def deviation_fair_spread_signal_answer(text: str) -> str:
        return text

    @staticmethod
    def result_calculation_funding(number: float, ticker: str) -> str:
        return f"Фандинг инструмента {ticker} = {number} руб."

    @staticmethod
    def result_fair_price_futures(number: float, ticker: str) -> str:
        return f"Справедливая цена фьючерса {ticker}: {number}"

    @staticmethod
    def result_fair_spread_futures(fair_spread: float, spread: float, tickers: list, spread_type: str) -> str:
        if spread_type == 'money':
            return (f"Справедливый спред фьючерсов:\n{' - '.join(tickers)} = {fair_spread} руб.\n"
                    f"Текущий спред: {spread} руб. Разница {round(fair_spread - spread, 3)} руб.")
        return (f"Справедливый спред фьючерсов:\n{' / '.join(tickers)} = {fair_spread}%\n"
                f"Текущий спред: {spread}%. Разница {round(fair_spread - spread, 3)}%")

    @staticmethod
    def spread_type() -> str:
        return 'Выберите в каком виде отображать спред:'

    @staticmethod
    def count_lots(count: str):
        return f"Количество лотов в первой ноге: {count}"

    @staticmethod
    def position() -> str:
        return 'Введите какой размер позиции в лотах:'

    @staticmethod
    def set_direction_position(direction: str, tickers: list):
        return f"Позиция '{direction}' спреда для {' '.join(tickers)}"

    @staticmethod
    def direction_position():
        return 'Выберите в каком направлении взят спред:'

    @staticmethod
    def funding(tickers: list) -> str:
        return f"Фандинг спреда для {' '.join(tickers)}"

    @staticmethod
    def what_needs_sent(tickers: list) -> str:
        return f"Выберите какую информацию нужно прислать для {' '.join(tickers)}:"

    @staticmethod
    def set_alert():
        return 'Установка оповещения по спреду'

    @staticmethod
    def get_info_spread():
        return 'Получение информации по спреду'

    @staticmethod
    def line_alert():
        return 'Пересечение горизонтальной линии'

    @staticmethod
    def bb_alert():
        return 'Пересечение линий Боллинджера'

    @staticmethod
    def fair_price_alert():
        return 'Отклонение от справедливого спреда'

    @staticmethod
    def money_spread():
        return 'Значение спреда в валюте'

    @staticmethod
    def percent_spread():
        return 'Значение спреда в процентах'

    @staticmethod
    def what_alert_set() -> str:
        return f"Выберите какое оповещение установить:"

    @staticmethod
    def spread_tickers(tickers: list):
        return f"Спред для {' '.join(tickers)}"

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
    def deviation_fair_spread_answer() -> str:
        return 'Укажите границу отклонения справедливого спреда:'

    @staticmethod
    def check_float_answer(text) -> str:
        return f'Неверное число: {text}\nДолжно быть целым или вещественным числом, а также записано через точку'

    @staticmethod
    def check_int_answer(text) -> str:
        return f'Неверное число: {text}\nЧисло должно быть целым'

    @staticmethod
    def command_chancel_answer() -> str:
        return 'Остановка отслеживания оповещений'

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
        return 'Напишите ID пользователя:'

    @staticmethod
    def get_user_nik():
        return 'Напишите никнейм пользователя:'

    @staticmethod
    def success_add_user_db(user_id: int, user_nik: str):
        return f"Пользователь {user_nik} с номером ID: {user_id} успешно добавлен."

    @staticmethod
    def choice_action_access():
        return 'Выберите дальнейшее действие:'

    @staticmethod
    def confirm_deletion(user_id: str):
        return f"Подтвердите удаление пользователя ID: {user_id}"

    @staticmethod
    def stop_admin_panel():
        return 'Панель администратора закрыта.'

    @staticmethod
    def monitoring():
        return "Управление мониторингами:"

    @staticmethod
    def active_monitoring():
        return "Активные мониторинги:"

    @staticmethod
    def get_active_monitoring(monitor_id: str, data: dict):
        tickers = data['data']['tickers']
        alert_type = "Линии" if data['data']['type_alert'] == 'line_alert' else "Боллинджер"
        spread_type = "Валюта" if data['data']['spread_type'] == 'money' else "Проценты"
        return (
            f"ID: {monitor_id}\n"
            f"Тикеры: {' '.join(tickers)}\n"
            f"Тип оповещения: {alert_type}\n"
            f"Тип спреда: {spread_type}\n\n"
        )

    @staticmethod
    def start_monitoring(monitor_id: str):
        return f"Мониторинг запущен.\nID: {monitor_id}"

    @staticmethod
    def stop_monitoring(monitor_id: str):
        return f"Мониторинг остановлен.\nID: {monitor_id}"

    @staticmethod
    def not_monitoring():
        return "Не удалось найти указанный мониторинг"

    @staticmethod
    def stop_all_monitoring(count: int):
        return f"Остановлено {count} мониторингов"

    @staticmethod
    def not_active_monitoring():
        return "У вас нет активных мониторингов"

    @staticmethod
    def select_action_monitoring():
        return "Что нужно сделать с мониторингами?"

    @staticmethod
    def stop_one_monitor():
        return 'Введите ID мониторинга, который нужно остановить:'

    @staticmethod
    def change_action_settings():
        return "Выберите действие с настройками:"

    @staticmethod
    def change_category_settings():
        return "Выберите категорию настроек для редактирования:"

    @staticmethod
    def error_message_parameter():
        return "Неверный формат ввода. Используйте: параметр=значение"

    @staticmethod
    def unknown_category_settings():
        return "❌ Неизвестная категория настроек"

    @staticmethod
    def parameter_updated(key: str, value: str) -> str:
        return f"✅ Параметр успешно обновлен:\n{key}= {value}"

    @staticmethod
    def parameter_update_error() -> str:
        return "❌ Ошибка при обновлении параметра"

    @staticmethod
    def response_parts_answer(settings: dict):
        response_parts = [
            "<b>TECHNICAL SETTINGS</b>:",
            *[f"  {key}: {settings.get(key, 'N/A')}" for key in TECHNICAL_SETTINGS],
            "",
            "<b>EXPIRATION MONTHS</b>:",
            *[f"  {key}: {value}" for key, value in settings.get('expiration', {}).items()],
            "",
            "<b>COMMANDS</b>:",
            *[f"  {key}: {value}" for key, value in settings.get('commands', {}).items()],
            "",
            "<b>PAIRS</b>:",
            format_settings_display(settings.get('pairs', {}), 'pairs')
        ]
        return "\n".join(response_parts)

    @staticmethod
    def actual_settings_category(category: str, settings: dict):
        response = f"Текущие настройки категории <b>{category}</b>:\n"
        response += format_settings_display(settings, category)
        return response

    @staticmethod
    def category_instruction(category: str):
        category_instructions = {
            'pairs': (
                "Для редактирования пар используйте команды:\n"
                "• Добавить пару: <code>add_pair=группа; (символ1, символ2, ...); (коэф1, коэф2, ...)</code>\n"
                "• Удалить пару: <code>del_pair=группа; индекс</code>\n"
                "• Изменить пару: <code>edit_pair=группа; индекс; (новые_символы); (новые_коэффициенты)</code>"
            ),
            'commands': (
                "Для редактирования команд используйте:\n"
                "• Добавить команду: <code>add_command=название; описание</code>\n"
                "• Удалить команду: <code>del_command=название</code>\n"
                "• Изменить команду: <code>edit_command=старое_название; новое_название; новое_описание</code>"
            ),
            'expiration_months': (
                "Для работы с месяцами экспирации используйте:\n"
                "• Добавить месяц: <code>expiration_months=символ</code> (например: expiration_months=V)\n"
                "• Удалить месяц: <code>delete=символ</code> (например: delete=V)\n"
                f"Доступные символы:\n{format_expiration_months()}"
            )
        }
        instruction = category_instructions.get(category,
                                                "Введите название параметра и новое значение в формате:\n"
                                                "<code>параметр=значение</code>"
                                                )
        return instruction

    @staticmethod
    def error_parameter_expiration(expiration: str):
        return f"❌ Ошибка: неверный символ месяца. Допустимые значения:\n{expiration}"

    @staticmethod
    def success_add_pair():
        return "✅ Пара успешно добавлена"

    @staticmethod
    def error_add_pair():
        return "❌ Ошибка при добавлении пары"

    @staticmethod
    def success_del_pair():
        return "✅ Пара успешно удалена"

    @staticmethod
    def error_del_pair():
        return "❌ Ошибка при удалении пары"

    @staticmethod
    def success_update_pair():
        return "✅ Пара успешно обновлена"

    @staticmethod
    def error_update_pair():
        return "❌ Ошибка при обновлении пары"

    @staticmethod
    def success_del_parameter_expiration(month_symbol: str):
        return f"✅ Месяц экспирации успешно удален: {month_symbol}"

    @staticmethod
    def error_del_parameter_expiration():
        return "❌ Ошибка при удалении месяца экспирации"

    @staticmethod
    def error_parameter_time_frame(timeframes: str):
        return f"Неверный тайм фрейм. Допустимые значения: {timeframes}"

    @staticmethod
    def error_positive_number():
        return "Должно быть положительным числом."

    @staticmethod
    def error_format_add_command():
        return "Неверный формат. Используйте: название; описание"

    @staticmethod
    def success_add_command(name: str):
        return f"✅ Команда '{name}' успешно добавлена"

    @staticmethod
    def error_add_command():
        return "❌ Ошибка при добавлении команды"

    @staticmethod
    def success_del_command(name: str):
        return f"✅ Команда '{name}' успешно удалена"

    @staticmethod
    def error_del_command():
        return "❌ Ошибка при удалении команды"

    @staticmethod
    def error_searching_command(name: str):
        return f"❌ Команда '{name}' не найдена"

    @staticmethod
    def error_format_update_command():
        return "Неверный формат. Используйте: старое_название; новое_название; новое_описание"

    @staticmethod
    def success_update_command(old_name: str, new_name: str):
        return f"✅ Команда '{old_name}' успешно изменена на '{new_name}'"

    @staticmethod
    def error_update_command():
        return "❌ Ошибка при изменении команды"

    @staticmethod
    def setting_update() -> str:
        return "Желаете установить индивидуальные настройки для оповещения?"

    @staticmethod
    def set_time_frame() -> str:
        return f"Выберите желаемый тайм фрейм для индикатора:\n{VALID_TIMEFRAMES}"

    @staticmethod
    def check_timeframe(timeframes: list) -> str:
        return f"Неверный тайм фрейм.\nДопустимые тайм фреймы:\n{timeframes}"

    @staticmethod
    def set_period() -> str:
        return "Введите желаемый период для индикатора. Допускается только целое число."

    @staticmethod
    def type_correlation():
        return "Выберите тип анализа корреляции:"

    @staticmethod
    def enter_tickers():
        return "Введите тикеры инструментов через запятую (например: SBER, GAZP, LKOH):"

    @staticmethod
    def choose_period():
        return "Выберите период для анализа:"

    @staticmethod
    def choose_period_all_stocks():
        return "Выберите период для анализа всех акций:"

    @staticmethod
    def error_entry_stocks():
        return "❌ Нужно ввести хотя бы 2 тикера!"

    @staticmethod
    def error_get_data_tickers():
        return "❌ Не удалось получить данные по акциям"

    @staticmethod
    def wait_get_data_tickers():
        return "Загружаю данные по всем акциям... Это может занять несколько минут."

    @staticmethod
    def success_get_data_tickers(length_data: int):
        return f"Получено данных по {length_data} акциям. Рассчитываю корреляцию..."

    @staticmethod
    def failed_calculate_correlation():
        return "❌ Не удалось рассчитать корреляцию"

    @staticmethod
    def no_pair_correlation():
        return "Не найдено пар акций с корреляцией ≥ 0.75 или ≤ -0.75"

    @staticmethod
    def choose_period_history():
        return "Выберите период для просмотра сохраненных корреляций:"

    @staticmethod
    def no_saved_correlation(days: int):
        return f"Нет сохраненных корреляций для периода {days} дней"

    @staticmethod
    def correlation_answer(days: int, tickers: list, correlation_matrix: pd.DataFrame):
        response = f"Корреляция за {days} дней:\n"
        for i, ticker1 in enumerate(tickers):
            for j, ticker2 in enumerate(tickers):
                if i < j:
                    corr = correlation_matrix.loc[ticker1, ticker2]
                    response += f"{ticker1} - {ticker2}: {corr:.2f}\n"
        return response

    @staticmethod
    def header_correlation_answer(days: int, count: int):
        header = f"<b>Сильные корреляции ({days} дней):</b>\n\n"
        header += f"Найдено {count} сильных корреляций\n"
        header += "🟢 ПРЯМ - прямая корреляция (≥ 0.75)\n"
        header += "🔴 ОБР - обратная корреляция (≤ -0.75)\n\n"
        return header

    @staticmethod
    def correlation_pair_answer(num: int, count: int, part: str):
        return f"<b>Часть {num}/{count}:</b>\n{part}"

    @staticmethod
    def correlation_history_answer(days: int, correlations: list):
        response = f"<b>Сохраненные корреляции ({days} дней):</b>\n\n"
        response += f"Дата расчета: {correlations[0]['calculation_date']}\n"
        response += f"Найдено пар: {len(correlations)}\n\n"
        response += "<code>"
        response += "АКЦИЯ 1    АКЦИЯ 2    КОРР.     ТИП\n"
        response += "-------------------------------------\n"
        for pair in correlations:
            ticker1 = pair['ticker1'].ljust(8)
            ticker2 = pair['ticker2'].ljust(8)
            corr = f"{pair['correlation']:.3f}".ljust(8)
            corr_type = "🟢 ПРЯМ" if pair['type'] == 'positive' else "🔴 ОБР"
            response += f"{ticker1} {ticker2} {corr} {corr_type}\n"
        response += "</code>"
        return response


bot_answers = BotAnswers()


if __name__ == '__main__':
    logger.info('Running answers.py from module telegram_api/essence')
