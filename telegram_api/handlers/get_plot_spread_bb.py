from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loguru import logger

from telegram_api.essence.answers_bot import BotAnswers
from telegram_api.essence.state_machine import MainInfo
from telegram_api.essence.keyboards import menu_spread_type, menu_futures_tool, menu_spot_tool
from settings import PARAMETERS
from utils.calculate_spread import calculate_spread
from utils.data_frame_pandas import add_dataframe_spread_bb
from utils.spread_chart import add_plot_spread


@logger.catch()
async def bollinger_bands(callback: types.CallbackQuery):
    logger.info('Получена команда на получение графика спреда с полосами Боллинджера')
    await MainInfo.spread_type_bb.set()
    await callback.message.answer(BotAnswers.spread_type(), reply_markup=menu_spread_type())


@logger.catch()
async def set_spread_type_bb(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spread_type'] = callback.data
        data['tool_1'] = PARAMETERS['tool_1']
        data['tool_2'] = PARAMETERS['tool_2']
    await get_spread_bb(callback, state)


@logger.catch()
async def get_spread_bb(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await callback.message.answer(BotAnswers.spread_bb_moex(data['tool_1'], data['tool_2'], data['spread_type']))
        await callback.message.answer(BotAnswers.expectation_answer())
        data['spread'] = await calculate_spread(data)
    df = await add_dataframe_spread_bb(data['tool_1'], data['tool_2'])
    plot = await add_plot_spread(df, data['tool_2'])
    await sending_signal_bb(callback, data, df, plot)
    await MainInfo.type_info.set()


@logger.catch()
async def sending_signal_bb(callback: types.CallbackQuery, data: dict, plot):
    logger.info(f'sending_signal_bb: {callback.data}\n{data}\n{PARAMETERS}')

    await callback.message.answer(f"Текущий спред {data['tool_1']} к {data['tool_2']}: {data['spread']}")
    if PARAMETERS['type_tool'] == 'futures' or PARAMETERS['type_tool'] == 'stocks_futures':
        await callback.message.answer_photo(photo=plot,
                                            caption=f"График с полосами Боллинджера для {data['tool_1']} к {data['tool_2']}",
                                            reply_markup=menu_futures_tool())
    else:
        await callback.message.answer_photo(photo=plot,
                                            caption=f"График с полосами Боллинджера для {data['tool_1']} к {data['tool_2']}",
                                            reply_markup=menu_spot_tool())


@logger.catch()
def register_handlers_command_bollinger_bands(dp: Dispatcher):
    dp.register_callback_query_handler(bollinger_bands, lambda callback: callback.data == 'bollinger_bands',
                                       state=MainInfo.type_info)
    dp.register_callback_query_handler(set_spread_type_bb, lambda callback: callback.data in ['money', 'percent'],
                                       state=MainInfo.spread_type_bb)


if __name__ == '__main__':
    logger.info('Running get_plot_spread_bb.py from module telegram_api/handlers')
