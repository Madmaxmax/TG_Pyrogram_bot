import logging
from functools import partial

from aiogram import Dispatcher, types
from aiogram_bot.functions.functions import *


def reg_admin_handler(dp: Dispatcher, queue):
    dp.register_message_handler(welcome, commands=['start'], state='*')
    dp.register_message_handler(partial(all_states_handler, queue), content_types=types.ContentType.ANY, state='*')
    dp.register_callback_query_handler(partial(test_callback, queue), state='*')


async def all_states_handler(queue: Queue, message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    print(state_name)
    queue.put('is_alive')
    try:
        if 'get_phone' in state_name:
            await get_phone(message=message, state=state, queue=queue)
        if 'get_2fa_code' in state_name:
            await get_2fa_code(message=message, state=state, queue=queue)
        if 'get_password' in state_name:
            await eval(f'{state_name}(message=message, state=state, queue=queue)')
        else:
            await eval(f'{state_name}(message=message, state=state)')
    except Exception as e:
        logging.error('State_handler has Exception - %s' % e)
