from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from database.database_bot import BotDatabase
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.keyboards import (main_menu, admin_menu, access_bot_menu, confirm_menu, settings_menu,
                                            settings_edit_menu)
from telegram_api.essence.state_machine import AdminPanel
from utils.decorators import check_int
from utils.settings_manager import settings_manager


async def admin_panel(message: types.Message):
    logger.info("Получена команда на администрирование бота.")
    admins = await BotDatabase().get_admin()
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
    await callback.message.delete()
    user_db = await BotDatabase().get_user('user_name', 'allowed_ids')
    if not user_db:
        return await callback.message.answer(BotAnswers.not_users_database())
    for user in user_db:
        history_line = await BotDatabase().db_read('bot_lines_signals', user)
        history_bollinger = await BotDatabase().db_read('bot_bb_signals', user)
        if not history_line and not history_bollinger:
            return await callback.message.answer(BotAnswers.not_info_database())
        if history_line:
            for elem in history_line:
                await callback.message.answer(BotAnswers.info_signal_database(elem[0], elem[4], elem[1], elem[2]))
        if history_bollinger:
            for elem in history_bollinger:
                await callback.message.answer(BotAnswers.info_signal_database(elem[0], elem[4], elem[1], elem[2]))
    return None


async def get_all_ids_db(callback: types.CallbackQuery):
    await callback.message.delete()
    allowed_users = await BotDatabase().get_user('user_name', 'allowed_ids')
    if allowed_users:
        await callback.message.answer(BotAnswers.allowed_users())
        for user in allowed_users:
            history_users = await BotDatabase().db_read('allowed_ids', user)
            if history_users:
                for elem in history_users:
                    await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
    incoming_users = await BotDatabase().get_user('user_name', 'incoming_ids')
    if incoming_users:
        await callback.message.answer(BotAnswers.unauthorized_users())
        for user in incoming_users:
            if user in allowed_users:
                continue
            history_users = await BotDatabase().db_read('allowed_ids', user)
            for elem in history_users:
                await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
    else:
        await callback.message.answer(BotAnswers.not_users_database())


async def access_bot(callback: types.CallbackQuery):
    await callback.message.delete()
    await AdminPanel.access_bot.set()
    await callback.message.answer(BotAnswers.access_bot(), reply_markup=access_bot_menu())


async def access_bot_get_incoming_ids(callback: types.CallbackQuery):
    await callback.message.delete()
    await AdminPanel.add_user.set()
    incoming_users = await BotDatabase().get_user('user_name', 'incoming_ids')
    await callback.message.answer(BotAnswers.unauthorized_users())
    if incoming_users:
        for user in incoming_users:
            history_users = await BotDatabase().db_read('incoming_ids', user)
            for elem in history_users:
                await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
        await callback.message.answer(BotAnswers.get_user_id())
    else:
        await callback.message.answer(BotAnswers.not_users_database())


async def access_bot_get_allowed_ids(callback: types.CallbackQuery):
    await callback.message.delete()
    await AdminPanel.del_user.set()
    allowed_ids = await BotDatabase().get_user('user_name', 'allowed_ids')
    await callback.message.answer(BotAnswers.allowed_users())
    if allowed_ids:
        for user in allowed_ids:
            history_users = await BotDatabase().db_read('allowed_ids', user)
            for elem in history_users:
                await callback.message.answer(BotAnswers.user_database(elem[0], elem[1], elem[2]))
        await callback.message.answer(BotAnswers.get_user_id())
    else:
        await callback.message.answer(BotAnswers.not_users_database())


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
        await BotDatabase().db_write(
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
            await BotDatabase().deleting_user_db(table_name='allowed_ids', user_id=data['id'])
        await callback.message.answer(BotAnswers.confirm_deletion(data['id']))
    await callback.message.answer(BotAnswers.choice_action_access(), reply_markup=admin_menu())
    await AdminPanel.what_edit.set()


async def get_parameters_bot(callback: types.CallbackQuery):
    await AdminPanel.view_settings.set()
    settings = settings_manager.get_all_settings()
    response = "Текущие настройки бота:\n\n"
    for category, values in settings.items():
        response += f"<b>{category.upper()}</b>:\n"
        if isinstance(values, dict):
            for key, val in values.items():
                response += f"  {key}: {val}\n"
        elif isinstance(values, (list, tuple)):
            for item in values:
                response += f"  - {item}\n"
        else:
            response += f"  {values}\n"
        response += "\n"
    await callback.message.answer(response, parse_mode='HTML')
    await callback.message.answer("Выберите действие с настройками:", reply_markup=settings_menu())


async def edit_settings_start(callback: types.CallbackQuery):
    await callback.message.delete()
    await AdminPanel.edit_settings_select.set()
    await callback.message.answer("Выберите категорию настроек для редактирования:",
                                  reply_markup=settings_edit_menu())


async def select_setting_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    category = callback.data.split('_')[-1]
    await state.update_data(category=category)
    settings = settings_manager.get_setting(category)
    if settings is None:
        await callback.message.answer("Ошибка: категория настроек не найдена", reply_markup=settings_menu())
        return
    response = f"Текущие настройки категории <b>{category}</b>:\n\n"
    if isinstance(settings, dict):
        for key, val in settings.items():
            response += f"{key}: {val}\n"
    else:
        response += str(settings)
    await callback.message.answer(response, parse_mode='HTML')
    await callback.message.answer(
        "Введите название параметра и новое значение в формате:\n"
        "<code>параметр = значение</code>\n\n"
        "Например: <code>bollinger_period = 100</code>",
        parse_mode='HTML'
    )
    await AdminPanel.edit_settings_value.set()


async def edit_setting_value(message: types.Message, state: FSMContext):
    try:
        parts = [p.strip() for p in message.text.split('=')]
        if len(parts) != 2:
            raise ValueError("Неверный формат ввода")
        param, value = parts
        state_data = await state.get_data()
        category = state_data['category']
        try:
            value = eval(value.strip())
        except:
            value = value.strip()
        full_key = f"{category}.{param}"
        if not settings_manager.update_setting(full_key, value):
            await message.answer("Ошибка: не удалось обновить параметр", reply_markup=settings_menu())
            return
        if settings_manager.save_settings():
            await message.answer(f"Параметр успешно обновлен:\n{full_key} = {value}", reply_markup=settings_menu())
        else:
            await message.answer("Ошибка при сохранении настроек в файл", reply_markup=settings_menu())
        await AdminPanel.what_edit.set()
        await message.answer(BotAnswers.what_edit(), reply_markup=admin_menu())
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}", reply_markup=settings_menu())


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
                                       state=AdminPanel.view_settings)
    dp.register_callback_query_handler(select_setting_category, lambda callback: callback.data.startswith('edit_'),
                                       state=AdminPanel.edit_settings_select)
    dp.register_message_handler(edit_setting_value, state=AdminPanel.edit_settings_value)


if __name__ == '__main__':
    logger.info('Running admin_panel.py from module telegram_api/handlers')
