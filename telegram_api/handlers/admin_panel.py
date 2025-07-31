from aiogram import Dispatcher, types

from loguru import logger

from database.database_bot import BotDatabase
from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import AdminPanel
from telegram_api.essence.keyboards import main_menu, admin_menu


@logger.catch()
async def admin_panel(message: types.Message):
    logger.info("Получена команда на администрирование бота.")
    admins = await BotDatabase().get_admin('allowed_ids')
    if message.from_user.username in admins:
        await AdminPanel.what_edit.set()
        await message.answer(BotAnswers.what_edit(), reply_markup=admin_menu())
    else:
        await message.answer(BotAnswers.not_admin(), reply_markup=main_menu())


@logger.catch()
async def get_history_signals_admin(callback: types.CallbackQuery):
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
                await callback.message.answer(BotAnswers.info_signal_database(elem))
        if history_bollinger:
            for elem in history_bollinger:
                await callback.message.answer(BotAnswers.info_signal_database(elem))
    return None


@logger.catch()
async def get_allowed_ids(callback: types.CallbackQuery):
    allowed_users = await BotDatabase().get_user('user_name', 'allowed_ids')
    if allowed_users:
        await callback.message.answer(BotAnswers.allowed_users())
        for user in allowed_users:
            history = await BotDatabase().db_read('allowed_ids', user)
            if history:
                for elem in history:
                    await callback.message.answer(BotAnswers.user_database(elem))
    incoming_users = await BotDatabase().get_user('user_name', 'incoming_ids')
    if incoming_users:
        await callback.message.answer(BotAnswers.unauthorized_users())
        for user in incoming_users:
            if user in allowed_users:
                continue
            history = await BotDatabase().db_read('allowed_ids', user)
            for elem in history:
                await callback.message.answer(BotAnswers.user_database(elem))
    else:
        await callback.message.answer(BotAnswers.not_users_database())


@logger.catch()
async def register_handlers_admin_panel_commands(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'], state='*')
    dp.register_callback_query_handler(get_allowed_ids, lambda callback: callback.data == 'get_users',
                                       state=AdminPanel.what_edit)
    dp.register_callback_query_handler(get_history_signals_admin,
                                       lambda callback: callback.data == 'get_signals',
                                       state=AdminPanel.what_edit)


if __name__ == '__main__':
    logger.info('Running admin_panel.py from module telegram_api/handlers')
