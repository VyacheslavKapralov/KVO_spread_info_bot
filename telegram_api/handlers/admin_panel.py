import re
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import (main_menu, admin_menu, access_bot_menu, confirm_menu, settings_menu,
                                            settings_edit_menu)
from telegram_api.essence.state_machine import AdminPanel
from utils.decorators import check_int
from utils.settings_manager import settings_manager


async def admin_panel(message: types.Message):
    logger.info("Получена команда на администрирование бота.")
    admins = await db.get_admin()
    if message.from_user.username in admins:
        await AdminPanel.what_edit.set()
        await message.answer(BotAnswers.what_edit(), reply_markup=admin_menu())
    else:
        await message.answer(BotAnswers.not_admin(), reply_markup=main_menu())


async def stop_admin_panel(callback: types.CallbackQuery, state: FSMContext):
    logger.info("Получена команда на завершение администрирования бота.")
    await callback.message.delete()
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await callback.message.answer(BotAnswers.stop_admin_panel())


async def get_history_signals_admin(callback: types.CallbackQuery):
    user_db = await db.get_user('user_name', 'allowed_ids')
    if not user_db:
        return await callback.message.answer(BotAnswers.not_users_database())
    for user in user_db:
        history_line = await db.db_read('bot_lines_signals', user)
        history_bollinger = await db.db_read('bot_bb_signals', user)
        if not history_line and not history_bollinger:
            return await callback.message.answer(BotAnswers.not_info_database())
        if history_line:
            for elem in history_line:
                await callback.message.answer(BotAnswers.info_signal_database(elem[0], elem[4], elem[1], elem[2]))
        if history_bollinger:
            for elem in history_bollinger:
                await callback.message.answer(BotAnswers.info_signal_database(elem[0], elem[4], elem[1], elem[2]))
        await back_admin_menu(callback)
    return None


async def get_all_ids_db(callback: types.CallbackQuery):
    allowed_users = await db.get_user('user_name', 'allowed_ids')
    if allowed_users:
        await callback.message.answer(BotAnswers.allowed_users())
        for user in allowed_users:
            history_users = await db.db_read('allowed_ids', user)
            if history_users:
                for elem in history_users:
                    await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
    incoming_users = await db.get_user('user_name', 'incoming_ids')
    if incoming_users:
        await callback.message.answer(BotAnswers.unauthorized_users())
        for user in incoming_users:
            if user in allowed_users:
                continue
            history_users = await db.db_read('allowed_ids', user)
            for elem in history_users:
                await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
    else:
        await callback.message.answer(BotAnswers.not_users_database())
    await back_admin_menu(callback)


async def access_bot(callback: types.CallbackQuery):
    await AdminPanel.access_bot.set()
    await callback.message.answer(BotAnswers.access_bot(), reply_markup=access_bot_menu())


async def access_bot_get_incoming_ids(callback: types.CallbackQuery):
    await AdminPanel.add_user.set()
    incoming_users = await db.get_user('user_name', 'incoming_ids')
    await callback.message.answer(BotAnswers.unauthorized_users())
    if incoming_users:
        for user in incoming_users:
            history_users = await db.db_read('incoming_ids', user)
            for elem in history_users:
                await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
        await callback.message.answer(BotAnswers.get_user_id())
    else:
        await callback.message.answer(BotAnswers.not_users_database())
    await back_admin_menu(callback)


async def access_bot_get_allowed_ids(callback: types.CallbackQuery):
    await AdminPanel.del_user.set()
    allowed_ids = await db.get_user('user_name', 'allowed_ids')
    await callback.message.answer(BotAnswers.allowed_users())
    if allowed_ids:
        for user in allowed_ids:
            history_users = await db.db_read('allowed_ids', user)
            for elem in history_users:
                await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
        await callback.message.answer(BotAnswers.get_user_id())
    else:
        await callback.message.answer(BotAnswers.not_users_database())
    await back_admin_menu(callback)


@check_int
async def set_user_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = int(message.text)
    current_state = await state.get_state()
    if current_state == AdminPanel.add_user.state:
        await AdminPanel.set_user_nik.set()
        await message.answer(BotAnswers.get_user_nik())
    else:
        await message.answer(BotAnswers.confirm_deletion(message.text), reply_markup=confirm_menu())


async def adding_user(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await db.db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='allowed_ids',
            user_name=message.text,
            user_id=data['id'],
            info='add_user'
        )
    await message.answer(BotAnswers.success_add_user_db(data['id'], message.text))
    await message.answer(BotAnswers.choice_action_access(), reply_markup=admin_menu())
    await AdminPanel.what_edit.set()


async def deleting_user(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'yes':
        async with state.proxy() as data:
            await db.deleting_user_db(table_name='allowed_ids', user_id=data['id'])
        await callback.message.answer(BotAnswers.confirm_deletion(data['id']))
    await back_admin_menu(callback)


async def get_parameters_bot(callback: types.CallbackQuery):
    await AdminPanel.view_settings.set()
    settings = await settings_manager.get_all_settings()
    response = "Текущие настройки бота:\n\n"
    response += "<b>TECHNICAL SETTINGS</b>:\n"
    tech_settings = [
        'time_frame_minutes', 'bollinger_period', 'bollinger_deviation',
        'sma_period', 'ema_period', 'atr_period', 'signals'
    ]
    for key in tech_settings:
        value = settings.get(key, 'N/A')
        response += f"  {key}: {value}\n"
    response += "\n"
    response += "<b>EXPIRATION MONTHS</b>:\n"
    for key, value in settings.get('expiration_months', {}).items():
        response += f"  {key}: {value}\n"
    response += "\n"
    response += "<b>COMMANDS</b>:\n"
    for key, value in settings.get('commands', {}).items():
        response += f"  {key}: {value}\n"
    response += "\n"
    response += "<b>PAIRS</b>:\n"
    pairs = settings.get('pairs', {})
    for group_name, group_pairs in pairs.items():
        response += f"  {group_name}:\n"
        for num, (symbols, coefficients) in enumerate(group_pairs):
            response += f"    [{num}] {symbols} × {coefficients}\n"
        response += "\n"
    await callback.message.answer(response, parse_mode='HTML')
    await callback.message.answer("Выберите действие с настройками:", reply_markup=settings_menu())


async def edit_settings_start(callback: types.CallbackQuery):
    await AdminPanel.edit_settings_select.set()
    await callback.message.answer("Выберите категорию настроек для редактирования:",
                                  reply_markup=settings_edit_menu())


async def select_setting_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split('-')[-1]
    await state.update_data(category=category)
    all_settings = await settings_manager.get_all_settings()
    settings = all_settings.get(category)
    response = f"Текущие настройки категории <b>{category}</b>:\n"
    if isinstance(settings, dict):
        for key, val in settings.items():
            response += f"{key}: {val}\n"
    else:
        response += str(settings)
    await callback.message.answer(response, parse_mode='HTML')
    if category == 'pairs':
        await callback.message.answer(
            "Для редактирования пар используйте команды:\n"
            "• Добавить пару\n: <code>add_pair=группа; (символ1, символ2, ...); (коэф1, коэф2, ...)</code>\n"
            "• Удалить пару\n: <code>del_pair=группа; индекс</code>\n"
            "• Изменить пару\n: <code>edit_pair=группа; индекс; (новые_символы); (новые_коэффициенты)</code>",
            parse_mode='HTML'
        )
    elif category == 'commands':
        await callback.message.answer(
            "Для редактирования команд используйте:\n"
            "• Добавить команду: <code>add_command=название; описание</code>\n"
            "• Удалить команду: <code>del_command=название</code>\n"
            "• Изменить команду: <code>edit_command=старое_название; новое_название; новое_описание</code>",
            parse_mode='HTML'
        )
    else:
        await callback.message.answer(
            "Введите название параметра и новое значение в формате:\n"
            "<code>параметр=значение</code>\n",
            parse_mode='HTML'
        )
    await AdminPanel.edit_settings_value.set()


async def edit_setting_value(message: types.Message, state: FSMContext):
    expiration_months = {
        'F': '01',
        'G': '02',
        'H': '03',
        'J': '04',
        'K': '05',
        'M': '06',
        'N': '07',
        'Q': '08',
        'U': '09',
        'V': '10',
        'X': '11',
        'Z': '12'
    }
    valid_timeframes = [
        '1m',
        '2m',
        '3m',
        '5m',
        '10m',
        '15m',
        '30m',
        '1h',
        '2h',
        '4h',
        '1d',
        '1w',
        '1M']
    value = None
    try:
        state_data = await state.get_data()
        category = state_data['category']
        logger.info(f"Editing category: {category}")
        parts = [p.strip() for p in message.text.split('=', 1)]
        if len(parts) != 2:
            raise ValueError("Неверный формат ввода. Используйте: параметр=значение")
        param, value_str = parts
        param = param.strip()
        value_str = value_str.strip()
        logger.info(f"Parameter: {param}, Value: {value_str}")
        if category == 'pairs' and param.startswith(('add_pair', 'del_pair', 'edit_pair')):
            await handle_pairs_commands_db(message, param, value_str)
            return
        elif category == 'commands' and param.startswith(('add_command', 'del_command', 'edit_command')):
            await handle_commands_commands_db(message, param, value_str)
            return
        elif category in ('signals', 'bollinger_period', 'bollinger_deviation', 'sma_period', 'ema_period',
                          'atr_period'):
            try:
                value = int(value_str)
                if value <= 0:
                    raise ValueError("Должно быть положительным числом.")
            except ValueError:
                await message.answer("❌ Ошибка: должно быть целым числом", reply_markup=settings_menu())
                return
        elif category == 'time_frame_minutes':
            if value_str not in valid_timeframes:
                await message.answer(
                    f"❌ Ошибка: неверный таймфрейм. Допустимые значения: {', '.join(valid_timeframes)}",
                    reply_markup=settings_menu())
                return
            value = value_str

        elif category == 'expiration_months':
            value_str = value_str.capitalize()
            if value_str.capitalize() not in expiration_months.keys():
                await message.answer(
                    f"❌ Ошибка: неверный символ месяца экспирации. Допустимые значения: {expiration_months}",
                    reply_markup=settings_menu())
                return
            value = f"{value_str}: {expiration_months[value_str]}"

        else:
            await message.answer("❌ Неизвестная категория настроек", reply_markup=settings_menu())
            return
        if category in ('expiration_months', 'pairs', 'commands'):
            full_key = f"{category}.{param}"
        else:
            full_key = f"technical.{param}"
        if await settings_manager.update_setting(full_key, value):
            await message.answer(f"✅ Параметр успешно обновлен:\n{full_key} = {value}", reply_markup=settings_menu())
        else:
            await message.answer("❌ Ошибка при обновлении параметра", reply_markup=settings_menu())
        await AdminPanel.what_edit.set()
    except Exception as error:
        await message.answer(f"❌ Ошибка: {str(error)}", reply_markup=settings_menu())


async def handle_pairs_commands_db(message: types.Message, command: str, data: str):
    try:
        pattern = r'\(([^)]+)\)'
        if command == 'add_pair':
            group_name, pairs, coeffs = data.split(';')
            group_name = group_name.strip()
            pairs_match = re.search(pattern, pairs)
            coeffs_match = re.search(pattern, coeffs)
            content_pairs = pairs_match.group(1)
            content_coeffs = coeffs_match.group(1)
            pairs = await db.get_pairs(group_name)
            symbols = [s.strip() for s in content_pairs.split(',')]
            coefficients = [int(s) for s in content_coeffs.split(',')]
            current_count = len(pairs.get(group_name, []))
            if await db.save_pair(group_name, current_count, symbols, coefficients):
                await message.answer("✅ Пара успешно добавлена", reply_markup=settings_menu())
            else:
                await message.answer("❌ Ошибка при добавлении пары", reply_markup=settings_menu())
        elif command == 'del_pair':
            group_name, index_str = data.split(';', 1)
            group_name = group_name.strip()
            index = int(index_str.strip())
            if await db.delete_pair(group_name, index):
                await message.answer("✅ Пара успешно удалена", reply_markup=settings_menu())
            else:
                await message.answer("❌ Ошибка при удалении пары", reply_markup=settings_menu())
        elif command == 'edit_pair':
            group_name, index, pairs, coeffs = data.split(';')
            pairs_match = re.search(pattern, pairs)
            coeffs_match = re.search(pattern, coeffs)
            content_pairs = pairs_match.group(1)
            content_coeffs = coeffs_match.group(1)
            symbols = [s.strip() for s in content_pairs.split(',')]
            coefficients = [int(s) for s in content_coeffs.split(',')]
            if await db.save_pair(group_name, index, symbols, coefficients):
                await message.answer("✅ Пара успешно обновлена", reply_markup=settings_menu())
            else:
                await message.answer("❌ Ошибка при обновлении пары", reply_markup=settings_menu())
    except Exception as error:
        await message.answer(f"❌ Ошибка при обработке команды пар: {str(error)}", reply_markup=settings_menu())


async def handle_commands_commands_db(message: types.Message, command: str, data: str):
    try:
        if command == 'add_command':
            parts = data.split(';', 1)
            if len(parts) != 2:
                raise ValueError("Неверный формат. Используйте: название; описание")
            name = parts[0].strip()
            description = parts[1].strip()
            if await settings_manager.update_setting(f"commands.{name}", description):
                await message.answer(f"✅ Команда '{name}' успешно добавлена", reply_markup=settings_menu())
            else:
                await message.answer("❌ Ошибка при добавлении команды", reply_markup=settings_menu())
        elif command == 'del_command':
            name = data.strip()
            all_settings = await settings_manager.get_all_settings()
            current_commands = all_settings.get('commands', {})
            if name in current_commands:
                if await settings_manager.delete_setting(f"commands.{name}"):
                    await message.answer(f"✅ Команда '{name}' успешно удалена", reply_markup=settings_menu())
                else:
                    await message.answer("❌ Ошибка при удалении команды", reply_markup=settings_menu())
            else:
                await message.answer(f"❌ Команда '{name}' не найдена", reply_markup=settings_menu())
        elif command == 'edit_command':
            parts = data.split(';', 2)
            if len(parts) != 3:
                raise ValueError("Неверный формат. Используйте: старое_название; новое_название; новое_описание")
            old_name = parts[0].strip()
            new_name = parts[1].strip()
            new_description = parts[2].strip()
            all_settings = await settings_manager.get_all_settings()
            current_commands = all_settings.get('commands', {})
            if old_name in current_commands:
                if (await settings_manager.update_setting(f"commands.{old_name}", None) and
                        await settings_manager.update_setting(f"commands.{new_name}", new_description)):
                    await message.answer(f"✅ Команда '{old_name}' успешно изменена на '{new_name}'",
                                         reply_markup=settings_menu())
                else:
                    await message.answer("❌ Ошибка при изменении команды", reply_markup=settings_menu())
            else:
                await message.answer(f"❌ Команда '{old_name}' не найдена", reply_markup=settings_menu())
    except Exception as error:
        await message.answer(f"❌ Ошибка при обработке команды commands: {str(error)}", reply_markup=settings_menu())


async def back_admin_menu(callback: types.CallbackQuery):
    await callback.message.answer(BotAnswers.choice_action_access(), reply_markup=admin_menu())
    await AdminPanel.what_edit.set()


async def register_handlers_admin_panel_commands(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'], state='*')
    dp.register_callback_query_handler(get_all_ids_db, lambda callback: callback.data == 'get_users',
                                       state=AdminPanel.what_edit)
    dp.register_callback_query_handler(get_history_signals_admin, lambda callback: callback.data == 'get_signals',
                                       state=AdminPanel.what_edit)
    dp.register_callback_query_handler(access_bot, lambda callback: callback.data == 'access',
                                       state=AdminPanel.what_edit)
    dp.register_callback_query_handler(access_bot_get_incoming_ids, lambda callback: callback.data == 'add_user',
                                       state=AdminPanel.access_bot)
    dp.register_callback_query_handler(access_bot_get_allowed_ids, lambda callback: callback.data == 'del_user',
                                       state=AdminPanel.access_bot)
    dp.register_message_handler(set_user_id, state=(AdminPanel.add_user, AdminPanel.del_user))
    dp.register_message_handler(adding_user, state=AdminPanel.set_user_nik)
    dp.register_callback_query_handler(deleting_user, state=AdminPanel.del_user)
    dp.register_callback_query_handler(stop_admin_panel, lambda callback: callback.data == 'stop_admin', state='*')
    dp.register_callback_query_handler(get_parameters_bot, lambda callback: callback.data == 'params',
                                       state=AdminPanel.what_edit)
    dp.register_callback_query_handler(edit_settings_start, lambda callback: callback.data == 'edit_settings',
                                       state='*')
    dp.register_callback_query_handler(select_setting_category, lambda callback: callback.data.startswith('edit_'),
                                       state=AdminPanel.edit_settings_select)
    dp.register_message_handler(edit_setting_value, state=AdminPanel.edit_settings_value)
    dp.register_callback_query_handler(back_admin_menu, lambda callback: callback.data == 'back_to_admin',
                                       state='*')


if __name__ == '__main__':
    logger.info('Running admin_panel.py from module telegram_api/handlers')
