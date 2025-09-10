import re
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import db
from settings import TECHNICAL_SETTINGS, EXPIRATION_MONTHS, VALID_TIMEFRAMES
from telegram_api.essence.answers_bot import bot_answers
from telegram_api.essence.keyboards import (main_menu, admin_menu, access_bot_menu, confirm_menu, settings_menu,
                                            settings_edit_menu)
from telegram_api.essence.state_machine import AdminPanel
from utils.decorators import check_int
from utils.formating_parameters import format_available_timeframes, format_expiration_months
from utils.settings_manager import settings_manager


async def admin_panel(message: types.Message):
    logger.info("Получена команда на администрирование бота.")
    admins = await db.get_admin()
    if message.from_user.username in admins:
        await AdminPanel.what_edit.set()
        await message.answer(bot_answers.what_edit(), reply_markup=admin_menu())
    else:
        await message.answer(bot_answers.not_admin(), reply_markup=main_menu())


async def stop_admin_panel(callback: types.CallbackQuery, state: FSMContext):
    logger.info("Получена команда на завершение администрирования бота.")
    await callback.message.delete()
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await callback.message.answer(bot_answers.stop_admin_panel())


async def get_history_signals_admin(callback: types.CallbackQuery):
    user_db = await db.get_user('user_name', 'allowed_ids')
    if not user_db:
        return await callback.message.answer(bot_answers.not_users_database())
    for user in user_db:
        history_line = await db.db_read('bot_lines_signals', user)
        history_bollinger = await db.db_read('bot_bb_signals', user)
        if not history_line and not history_bollinger:
            return await callback.message.answer(bot_answers.not_info_database())
        if history_line:
            for elem in history_line:
                await callback.message.answer(bot_answers.info_signal_database(elem[0], elem[3], elem[1], elem[2]))
        if history_bollinger:
            for elem in history_bollinger:
                await callback.message.answer(bot_answers.info_signal_database(elem[0], elem[3], elem[1], elem[2]))
        await back_admin_menu(callback)
    return None


async def get_all_ids_db(callback: types.CallbackQuery):
    allowed_users = await db.get_user('user_name', 'allowed_ids')
    if allowed_users:
        await callback.message.answer(bot_answers.allowed_users())
        for user in allowed_users:
            history_users = await db.db_read('allowed_ids', user)
            if history_users:
                for elem in history_users:
                    await callback.message.answer(bot_answers.user_database(elem[0], elem[1], elem[2]))
    incoming_users = await db.get_user('user_name', 'incoming_ids')
    if incoming_users:
        await callback.message.answer(bot_answers.unauthorized_users())
        for user in incoming_users:
            if user in allowed_users:
                continue
            history_users = await db.db_read('incoming_ids', user)
            for elem in history_users:
                await callback.message.answer(bot_answers.user_database(elem[0], elem[1], elem[2]))
    else:
        await callback.message.answer(bot_answers.not_users_database())
    await back_admin_menu(callback)


async def access_bot(callback: types.CallbackQuery):
    await AdminPanel.access_bot.set()
    await callback.message.answer(bot_answers.access_bot(), reply_markup=access_bot_menu())


async def access_bot_get_incoming_ids(callback: types.CallbackQuery):
    await AdminPanel.add_user.set()
    incoming_users = await db.get_user('user_name', 'incoming_ids')
    await callback.message.answer(bot_answers.unauthorized_users())
    if incoming_users:
        for user in incoming_users:
            history_users = await db.db_read('incoming_ids', user)
            for elem in history_users:
                await callback.message.answer(bot_answers.user_database(elem[0], elem[1], elem[2]))
        await callback.message.answer(bot_answers.get_user_id())
    else:
        await callback.message.answer(bot_answers.not_users_database())


async def access_bot_get_allowed_ids(callback: types.CallbackQuery):
    await AdminPanel.del_user.set()
    allowed_ids = await db.get_user('user_name', 'allowed_ids')
    await callback.message.answer(bot_answers.allowed_users())
    if allowed_ids:
        for user in allowed_ids:
            history_users = await db.db_read('allowed_ids', user)
            for elem in history_users:
                await callback.message.answer(bot_answers.user_database(elem[0], elem[1], elem[2]))
        await callback.message.answer(bot_answers.get_user_id())
    else:
        await callback.message.answer(bot_answers.not_users_database())


@check_int
async def set_user_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = int(message.text)
    current_state = await state.get_state()
    if current_state == AdminPanel.add_user.state:
        await AdminPanel.set_user_nik.set()
        await message.answer(bot_answers.get_user_nik())
    else:
        await message.answer(bot_answers.confirm_deletion(message.text), reply_markup=confirm_menu())


async def adding_user(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await db.db_write(
            date_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            table_name='allowed_ids',
            user_name=message.text,
            user_id=data['id'],
            info='add_user'
        )
    await message.answer(bot_answers.success_add_user_db(data['id'], message.text))
    await message.answer(bot_answers.choice_action_access(), reply_markup=admin_menu())
    await AdminPanel.what_edit.set()


async def deleting_user(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'yes':
        async with state.proxy() as data:
            await db.deleting_user_db(table_name='allowed_ids', user_id=data['id'])
        await callback.message.answer(bot_answers.confirm_deletion(data['id']))
    await back_admin_menu(callback)


async def get_parameters_bot(callback: types.CallbackQuery):
    await AdminPanel.view_settings.set()
    settings = await settings_manager.get_all_settings()
    await callback.message.answer(bot_answers.response_parts_answer(settings), parse_mode='HTML')
    await callback.message.answer(bot_answers.change_action_settings(), reply_markup=settings_menu())


async def edit_settings_start(callback: types.CallbackQuery):
    await AdminPanel.edit_settings_select.set()
    await callback.message.answer(bot_answers.change_category_settings(), reply_markup=settings_edit_menu())


async def select_setting_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split('-')[-1]
    await state.update_data(category=category)
    all_settings = await settings_manager.get_all_settings()
    settings = all_settings.get(category, {})
    await callback.message.answer(bot_answers.actual_settings_category(category, settings), parse_mode='HTML')
    await callback.message.answer(bot_answers.category_instruction(category), parse_mode='HTML')
    await AdminPanel.edit_settings_value.set()


async def edit_setting_value(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    category = state_data['category']
    logger.info(f"Editing category: {category}")
    parts = [p.strip() for p in message.text.split('=', 1)]
    if len(parts) != 2:
        await message.answer(bot_answers.error_message_parameter())
    param, value_str = parts
    param, value_str = param.strip(), value_str.strip()
    logger.info(f"Parameter: {param}, Value: {value_str}")
    if await _handle_special_commands(message, category, param, value_str):
        return
    result = await _process_setting(message, category, value_str)
    if not result:
        await message.answer(bot_answers.unknown_category_settings(), reply_markup=settings_menu())
        return
    full_key, value = result
    if await settings_manager.update_setting(full_key, value):
        await message.answer(bot_answers.parameter_updated(full_key, value), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.parameter_update_error(), reply_markup=settings_menu())
    await AdminPanel.what_edit.set()


async def _handle_special_commands(message: types.Message, category: str, param: str, value_str: str):
    if category == 'pairs' and param.startswith(('add_pair', 'del_pair', 'edit_pair')):
        await handle_pairs_commands_db(message, param, value_str)
        return True
    elif category == 'commands' and param.startswith(('add_command', 'del_command', 'edit_command')):
        await handle_commands_commands_db(message, param, value_str)
        return True
    elif category == 'expiration' and param == 'delete':
        await _handle_expiration_delete(message, value_str)
        return True
    return False


async def _handle_expiration_delete(message: types.Message, value_str: str):
    month_symbol = value_str.upper()
    if month_symbol not in EXPIRATION_MONTHS:
        expiration_list = format_expiration_months()
        await message.answer(bot_answers.error_parameter_expiration(expiration_list), reply_markup=settings_menu())
        return
    if await settings_manager.delete_setting(f"expiration.{month_symbol}"):
        await message.answer(bot_answers.success_del_parameter_expiration(month_symbol), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.error_del_parameter_expiration(), reply_markup=settings_menu())


async def _process_setting(message: types.Message, category: str, value_str: str) -> str or None:
    if category == 'time_frame_minutes':
        if value_str not in VALID_TIMEFRAMES:
            await message.answer(bot_answers.error_parameter_time_frame(format_available_timeframes()))
        return "technical.time_frame_minutes", value_str
    elif category in TECHNICAL_SETTINGS:
        try:
            value = int(value_str)
            if value <= 0:
                await message.answer(bot_answers.error_positive_number())
            return f"technical.{category}", value
        except ValueError:
            await message.answer(bot_answers.check_int_answer(value_str))
    elif category == 'expiration':
        month_symbol = value_str.upper()
        if month_symbol not in EXPIRATION_MONTHS:
            expiration_list = format_expiration_months()
            await message.answer(bot_answers.error_parameter_expiration(expiration_list))
        return f"expiration.{month_symbol}", EXPIRATION_MONTHS[month_symbol]
    return None


async def handle_pairs_commands_db(message: types.Message, command: str, data: str):
    pattern = r'\(([^)]+)\)'
    if command == 'add_pair':
        await add_pair(message, data, pattern)
    elif command == 'del_pair':
        await del_pair(message, data)
    elif command == 'edit_pair':
        await edit_pair(message, data, pattern)


async def handle_commands_commands_db(message: types.Message, command: str, data: str):
    if command == 'add_command':
        await add_command(message, data)
    elif command == 'del_command':
        await del_command(message, data)
    elif command == 'edit_command':
        await edit_command(message, data)


async def back_admin_menu(callback: types.CallbackQuery):
    await callback.message.answer(bot_answers.choice_action_access(), reply_markup=admin_menu())
    await AdminPanel.what_edit.set()


async def register_handlers_admin_panel_commands(dp: Dispatcher):
    handlers = [
        (admin_panel, {'commands': ['admin'], 'state': '*'}),
        (get_all_ids_db, {'lambda': lambda c: c.data == 'get_users', 'state': AdminPanel.what_edit}),
        (get_history_signals_admin, {'lambda': lambda c: c.data == 'get_signals', 'state': AdminPanel.what_edit}),
        (access_bot, {'lambda': lambda c: c.data == 'access', 'state': AdminPanel.what_edit}),
        (access_bot_get_incoming_ids, {'lambda': lambda c: c.data == 'add_user', 'state': AdminPanel.access_bot}),
        (access_bot_get_allowed_ids, {'lambda': lambda c: c.data == 'del_user', 'state': AdminPanel.access_bot}),
        (set_user_id, {'state': (AdminPanel.add_user, AdminPanel.del_user)}),
        (adding_user, {'state': AdminPanel.set_user_nik}),
        (deleting_user, {'state': AdminPanel.del_user}),
        (stop_admin_panel, {'lambda': lambda c: c.data == 'stop_admin', 'state': '*'}),
        (get_parameters_bot, {'lambda': lambda c: c.data == 'params', 'state': AdminPanel.what_edit}),
        (edit_settings_start, {'lambda': lambda c: c.data == 'edit_settings', 'state': '*'}),
        (select_setting_category,
         {'lambda': lambda c: c.data.startswith('edit_'), 'state': AdminPanel.edit_settings_select}),
        (edit_setting_value, {'state': AdminPanel.edit_settings_value}),
        (back_admin_menu, {'lambda': lambda c: c.data == 'back_to_admin', 'state': '*'})
    ]
    for handler, params in handlers:
        if 'lambda' in params:
            dp.register_callback_query_handler(handler, params['lambda'], state=params['state'])
        else:
            dp.register_message_handler(handler, **params)


async def add_pair(message: types.Message, data: str, pattern: str):
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
        await message.answer(bot_answers.success_add_pair(), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.error_add_pair(), reply_markup=settings_menu())


async def del_pair(message: types.Message, data: str):
    group_name, index_str = data.split(';', 1)
    group_name = group_name.strip()
    index = int(index_str.strip())
    if await db.delete_pair(group_name, index):
        await message.answer(bot_answers.success_del_pair(), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.error_del_pair(), reply_markup=settings_menu())


async def edit_pair(message: types.Message, data: str, pattern: str):
    group_name, index, pairs, coeffs = data.split(';')
    pairs_match = re.search(pattern, pairs)
    coeffs_match = re.search(pattern, coeffs)
    content_pairs = pairs_match.group(1)
    content_coeffs = coeffs_match.group(1)
    symbols = [s.strip() for s in content_pairs.split(',')]
    coefficients = [int(s) for s in content_coeffs.split(',')]
    if await db.save_pair(group_name, index, symbols, coefficients):
        await message.answer(bot_answers.success_update_pair(), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.error_update_pair(), reply_markup=settings_menu())


async def add_command(message: types.Message, data: str):
    parts = data.split(';', 1)
    if len(parts) != 2:
        await message.answer(bot_answers.error_format_add_command())
    name = parts[0].strip()
    description = parts[1].strip()
    if await settings_manager.update_setting(f"commands.{name}", description):
        await message.answer(bot_answers.success_add_command(name), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.error_add_command(), reply_markup=settings_menu())


async def del_command(message: types.Message, data: str):
    name = data.strip()
    all_settings = await settings_manager.get_all_settings()
    current_commands = all_settings.get('commands', {})
    if name in current_commands:
        if await settings_manager.delete_setting(f"commands.{name}"):
            await message.answer(bot_answers.success_del_command(name), reply_markup=settings_menu())
        else:
            await message.answer(bot_answers.error_del_command(), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.error_searching_command(name), reply_markup=settings_menu())


async def edit_command(message: types.Message, data: str):
    parts = data.split(';', 2)
    if len(parts) != 3:
        await message.answer(bot_answers.error_format_update_command())
    old_name = parts[0].strip()
    new_name = parts[1].strip()
    new_description = parts[2].strip()
    all_settings = await settings_manager.get_all_settings()
    current_commands = all_settings.get('commands', {})
    if old_name in current_commands:
        if (await settings_manager.update_setting(f"commands.{old_name}", None) and
                await settings_manager.update_setting(f"commands.{new_name}", new_description)):
            await message.answer(bot_answers.success_update_command(old_name, new_name),
                                 reply_markup=settings_menu())
        else:
            await message.answer(bot_answers.error_update_command(), reply_markup=settings_menu())
    else:
        await message.answer(bot_answers.error_searching_command(old_name), reply_markup=settings_menu())


if __name__ == '__main__':
    logger.info('Running admin_panel.py from module telegram_api/handlers')
