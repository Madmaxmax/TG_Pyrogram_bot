import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram_bot.database.DB import Database as set_db
from aiogram_bot.keyboards.inline import Keyboard
from env import load_env
from pyrogram_bot.database.DB import Database as db
from initialisation import *
from dotenv import set_key, find_dotenv


# db = Database('pyrogram_bot/database_storage/Accounts_settings.db')
# db.create_table()


async def welcome(message: types.Message):
    containers = set_db().get_containers()
    accounts = 0
    for account in containers:
        accounts += len(await db(account[0]).get_all_accounts())
    count_cont = 0
    ready_cont = ''
    count_ready = 0
    containers = set_db().get_containers()
    for container in containers:
        if int(container[3]) == 1:
            print(count_ready, len(containers))
            count_ready += 1
            if count_ready == 1:
                ready_cont += f'╒<code>{container[1]}</code>\n'
            elif count_ready == len(containers):
                ready_cont += f'╘<code>{container[1]}</code>\n'
            else:
                ready_cont += f'╞<code>{container[1]}</code>\n'
        count_cont += 1
    msg = f'''
<b>Панель администратора</b>

<b>Инфо</b>
<b>╠Всего аккаунтов:</b> <code>{accounts}</code>
<b>╠Всего групп:</b> <code>{count_cont}</code>
<b>╙Группы в работе:</b> <code>{count_ready}</code>

{ready_cont}
'''
    await message.answer(msg, reply_markup=Keyboard().welcome())
    # id = message.from_user.id
    # bot = message.bot


async def welcome_call(call: types.CallbackQuery, state: FSMContext):
    containers = set_db().get_containers()
    accounts = 0
    for account in containers:
        accounts += len(await db(account[0]).get_all_accounts())
    count_cont = 0
    ready_cont = ''
    count_ready = 0
    containers = set_db().get_containers()
    for container in containers:
        if int(container[3]) == 1:
            count_ready += 1
            if count_ready == 1:
                ready_cont += f'╒<code>{container[1]}</code>\n'
            elif count_ready == len(containers):
                ready_cont += f'╘<code>{container[1]}</code>\n'
            else:
                ready_cont += f'╞<code>{container[1]}</code>\n'
        count_cont += 1
    msg = f'''
<b>Панель администратора</b>

<b>Инфо</b>
<b>╠Всего аккаунтов:</b> <code>{accounts}</code>
<b>╠Всего групп:</b> <code>{count_cont}</code>
<b>╙Группы в работе:</b> <code>{count_ready}</code>

{ready_cont}
'''
    await call.message.edit_text(msg, reply_markup=Keyboard().welcome())


async def test_callback(queue: Queue, call: types.CallbackQuery, state: FSMContext):
    if 'my_revers' in call.data:
        await my_revers(call, state, queue)
        return
    if 'my_account_' in call.data:
        await my_account(call, state)
        return
    if 'new_delay' in call.data:
        await new_delays(call, state)
        return
    if 'add_account' in call.data:
        await new_account(call, state)
        return
    if 'add_container' in call.data:
        await new_container(call, state)
        return
    if 'del_prompt' in call.data:
        await del_prompt(call, state)
        return
    if 'container_' in call.data:
        id_ = call.data[10:]
        await state.update_data(container_id=id_)
        await my_container(call, state)
        return
    else:
        await eval(f'{call.data}(call, state)')


async def my_revers(call: types.CallbackQuery, state: FSMContext, queue: Queue):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    is_ready = set_db().get_container(container_id)
    if int(is_ready[3]) == 1:
        set_db().update_container(container_name, 'Is_ready', '0')
        queue.put(f'stop_container_{container_id}')
    else:
        set_db().update_container(container_name, 'Is_ready', '1')
    await my_container(call, state)


async def my_account(call: types.CallbackQuery, state: FSMContext):
    account_id = call.data[11:]
    data = await state.get_data()
    await state.update_data(account_id=account_id)
    container_name = data['container_name']
    container_id = data['container_id']
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>
<b>Аккаунт:</b> <code>{account_id}</code>

<em>Выберите:</em>
'''
    keyboard.add(button(text='Чаты', callback_data='my_chats'),
                 button(text='Удалить', callback_data='add_links_with_pyrogram'))
    keyboard.add(button(text='Назад', callback_data='my_container'))
    await call.message.edit_text(msg, reply_markup=keyboard)


async def my_chats(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    account_id = data['account_id']
    container_name = data['container_name']
    container_id = data['container_id']
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton
    chats = await db(container_id).get_chat_links_for_account(0, 0, account_id)
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>
<b>Аккаунт:</b> <code>{account_id}</code>
<em>Чаты</em>

<em>Выберите:</em>
'''
    keyboard.add(button(text='Добавить', callback_data='add_links'))
    keyboard.add(button(text='Удалить', callback_data='add_links'))
    await call.message.edit_text(msg, reply_markup=Keyboard().container_setting())


async def my_proxy(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>
<em>Proxy</em>

<em>Выберите:</em>
'''
    await call.message.edit_text(msg, reply_markup=Keyboard().container_setting())


async def my_delays(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    delay = int(set_db().get_container(container_id)[2])
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    button = types.InlineKeyboardButton
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>
<em>Задержка комментирования</em>

Задержка: {delay} сек.
'''
    keyboard.add(button(text='⏪️', callback_data=f'new_delay_{delay - 5}'),
                 button(text='◀️', callback_data=f'new_delay_{delay - 1}'),
                 button(text='▶️', callback_data=f'new_delay_{delay + 1}'),
                 button(text='⏩️', callback_data=f'new_delay_{delay + 5}'))
    keyboard.add(button(text='Назад', callback_data=f'my_settings'))
    await call.message.edit_text(msg, reply_markup=keyboard)


async def new_delays(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    new_delay = call.data[10:]
    set_db().update_container(container_name, 'Delay', new_delay)
    await my_delays(call, state)


async def my_prompt(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    buttons = []
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>
<em>Промпт | Ключи OpenAI</em>

'''
    prompt_datas = await db(container_id).get_prompt()
    if prompt_datas != None:
        for prompt_data in prompt_datas:
            prompt_name = prompt_data[1]
            prompt = prompt_data[2]
            api_key = prompt_data[3]
            msg += f'''
Имя: {prompt_name}
Промпт: {prompt[:100]}
Ключ: {api_key}
'''
            buttons.append(button(text=f'Удалить ({prompt_name})', callback_data=f'del_prompt_{prompt_data[0]}'))
    keyboard.add(button(text='Добавить', callback_data='add_prompt'))
    keyboard.add(*buttons)
    keyboard.add(button(text='Назад', callback_data='my_settings'))
    await call.message.edit_text(msg, reply_markup=keyboard)


async def add_prompt(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    buttons = []
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>
<em>Промпт | Ключи OpenAI</em>

Формат сообщения:
<em><code>Имя: ...
Промпт: ...
api_key: ...</code></em>

Введите:
'''
    await state.set_state('add_new_prompt')
    keyboard.add(button(text='Назад', callback_data='my_prompt'))
    await call.message.edit_text(msg, reply_markup=keyboard)


async def add_new_prompt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    msg_data = message.text.strip()
    msg_prompt_i = msg_data.find('Промпт:')
    msg_api_i = msg_data.find('api_key:')
    msg_name = msg_data[4:msg_prompt_i].strip()
    msg_prompt = msg_data[msg_prompt_i + 6:msg_api_i].strip()
    msg_api = msg_data[msg_api_i + 7:].strip()
    await db(container_id).add_prompt_and_key(msg_name, msg_prompt, msg_api)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    buttons = []
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>
<em>Промпт | Ключи OpenAI</em>

    '''
    prompt_datas = await db(container_id).get_prompt()
    for prompt_data in prompt_datas:
        prompt_name = prompt_data[1]
        prompt = prompt_data[2]
        api_key = prompt_data[3]
        msg += f'''
Имя: {prompt_name}
Промпт: {prompt[:100]}
Ключ: {api_key}
'''
        buttons.append(button(text=f'Удалить ({prompt_name})', callback_data=f'del_prompt_{prompt_data[0]}'))
    keyboard.add(button(text='Добавить', callback_data='add_prompt'))
    keyboard.add(*buttons)
    keyboard.add(button(text='Назад', callback_data='my_settings'))
    msg_id = message.message_id
    await message.delete()
    await message.bot.edit_message_text(message.chat.id, msg - 1, reply_markup=keyboard)


async def del_prompt(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_id = data['container_id']
    prompt_id = call.data[11:]
    await db(container_id).delete_prompt(int(prompt_id))
    await my_prompt(call, state)


async def my_settings(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    container_id = data['container_id']
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>


<em>Выберите:</em>
'''
    await call.message.edit_text(msg, reply_markup=Keyboard().container_setting())


async def my_container(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = None
    for container in set_db().get_containers():
        print(data['container_id'])
        print(container[0])
        if int(container[0]) == int(data['container_id']):
            container_name = container[1]
    await state.update_data(container_name=container_name)
    accounts = await db(data['container_id']).get_all_accounts()
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>

<b>Инфо</b>
<b>Всего аккаунтов:</b> <code>{len(accounts)}</code>
'''
    await call.message.edit_text(msg, reply_markup=Keyboard().my_container(accounts, data['container_id']))


async def my_accounts(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    container_name = data['container_name']
    accounts = await db(data['container_id']).get_all_accounts()
    msg = f'''
<b>Панель администратора
Группа: {container_name}</b>

<b>Инфо</b>
Всего аккаунтов: {len(accounts)}

<em>Выберите аккаунт</em>
'''
    await call.message.edit_text(msg, reply_markup=Keyboard().get_accounts(accounts))


async def get_account_data(state: FSMContext):
    data = await state.get_data()

    api_id = data['api_id'] if data['api_id'] else '...'
    api_hash = data['api_hash'] if data['api_hash'] else '...'
    phone = data['phone'] if data['phone'] else '...'
    code = data['code'] if data['code'] else '...'
    password = data['password'] if data['password'] else '...'

    msg = f'''
<b>Панель администратора | Добавить аккаунт</b>

<b>Api_id:</b> <code>{api_id}</code>
<b>Api_hash:</b> <code>{api_hash}</code>
<b>Phone:</b> <code>{phone}</code>
<b>2FA Password:</b> <code>{password}</code>
<b>2FA Code:</b> <code>{code}</code>
'''
    return msg


async def new_container(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    msg = '<b>Введитe имя новой группы:</b>'
    await call.message.edit_text(msg)
    await state.set_state('add_new_container')


async def add_new_container(message: types.Message, state: FSMContext):
    await state.finish()
    container_id = set_db().add_container(message.text)
    await state.update_data(container_id=container_id)
    db(container_id).create_table()
    msg_id = message.message_id
    await message.delete()
    await message.bot.delete_message(message.chat.id, msg_id - 1)
    await welcome(message)


async def new_account(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(api_id=None, api_hash=None, phone=None, code=None, password=None, links=None, msg_id=None)
    msg = await get_account_data(state=state)
    msg += '<b>Введите: [Api_id]</b>'
    await call.message.edit_text(msg, reply_markup=Keyboard().go_home())
    await state.set_state('get_api_id')


async def get_api_id(message: types.Message, state: FSMContext):
    msg_id = message.message_id
    await message.bot.delete_message(message.chat.id, msg_id)

    api_id = message.text
    await state.update_data(api_id=api_id, msg_id=msg_id - 1)
    msg = await get_account_data(state=state)
    data = await state.get_data()
    msg += '<b>Введите: [Api_hash]</b>'
    await message.bot.edit_message_text(msg, message.chat.id, data['msg_id'], reply_markup=Keyboard().go_home())
    await state.set_state('get_api_hash')


async def get_api_hash(message: types.Message, state: FSMContext):
    msg_id = message.message_id
    await message.bot.delete_message(message.chat.id, msg_id)

    api_hash = message.text
    await state.update_data(api_hash=api_hash)
    msg = await get_account_data(state=state)
    data = await state.get_data()
    msg += '<b>Введите: [Phone]</b>'
    await message.bot.edit_message_text(msg, message.chat.id, data['msg_id'], reply_markup=Keyboard().go_home())
    await state.set_state('get_phone')


async def get_phone(message: types.Message, state: FSMContext, queue: Queue):
    msg_id = message.message_id
    await message.bot.delete_message(message.chat.id, msg_id)

    phone = message.text.strip().replace('+7', '8').replace(' ', '')
    await state.set_state('get_password')
    await state.update_data(phone=phone)
    msg = await get_account_data(state=state)
    data = await state.get_data()
    msg += '<b>Введите: [2FA Password]\n<em>None если пароля нет</em></b>'
    await message.bot.edit_message_text(msg, message.chat.id, data['msg_id'], reply_markup=Keyboard().go_home())


async def get_password(message: types.Message, state: FSMContext, queue: Queue):
    msg_id = message.message_id
    await message.bot.delete_message(message.chat.id, msg_id)

    password = message.text
    await state.update_data(password=password)
    data = await state.get_data()
    print(data)
    try:
        await db(data['container_id']).insert_new_record_to_Accounts(api_id=data['api_id'], api_hash=data['api_hash'],
                                                                     phone_number=data['phone'],
                                                                     password=data['password'],
                                                                     chat_links='')
        await db(data['container_id']).close()
    except Exception as e:
        db(data['container_id']).create_table()
        await db(data['container_id']).insert_new_record_to_Accounts(api_id=data['api_id'], api_hash=data['api_hash'],
                                                                     phone_number=data['phone'],
                                                                     password=data['password'],
                                                                     chat_links='')
        await db(data['container_id']).close()
    queue.put(f'restart_container_{data["container_id"]}')
    # Отправляем код (логинимся)
    msg = await get_account_data(state)
    msg += f'<b>Введите: [2FA Code]</b>'
    await state.set_state('get_2fa_code')
    await message.bot.edit_message_text(msg, message.chat.id, data['msg_id'], reply_markup=Keyboard().go_home())


async def get_2fa_code(message: types.Message, state: FSMContext, queue: Queue):
    msg_id = message.message_id
    await message.bot.delete_message(message.chat.id, msg_id)

    code = message.text
    print(code)
    await state.update_data(code=code)
    data = await state.get_data()
    await db(data['container_id']).update_code(api_id=data['api_id'], api_hash=data['api_hash'],
                                               phone_number=data['phone'], new_code=data['code'])
    # Подтверждаем код (заканчиваем авторизацию)
    await asyncio.sleep(7)
    temp = await db(data['container_id']).get_code_for_account(data['api_id'], data['api_hash'], data['phone'])
    print(temp[0])
    if temp[0] == '0':
        await asyncio.sleep(2)
        msg = await get_account_data(state=state)
        msg += '<b>Введён не верный [2FA Code]\nВведите: [2FA Code]</b>'
        await message.bot.edit_message_text(msg, message.chat.id, data['msg_id'], reply_markup=Keyboard().go_home())
        await state.set_state('get_2fa_code')
        return
    await message.bot.delete_message(message.chat.id, data['msg_id'])
    await welcome(message)

#
# async def get_links_(message: types.Message, state: FSMContext):
#     from main import run_pyrogram_bot
#     await message.answer("Введите код для входа")
#     await state.update_data(links=message.text)
#     await state.set_state('get_links')
#     data = await state.get_data()
#     await db().insert_new_record_to_Accounts(api_id=data['api_id'], api_hash=data['api_hash'],
#                                              phone_number=data['phone'], password=data['password'],
#                                              chat_links=data['links'])
#     await db().close()
#     # await restart_pyrogram_bot(run_pyrogram_bot)
#     await state.set_state('wait_password')
#
#
# async def wait_password(message: types.Message, state: FSMContext):
#     await state.update_data(code=message.text)
#     data = await state.get_data()
#     await db().update_code(api_id=data['api_id'], api_hash=data['api_hash'],
#                            phone_number=data['phone'], new_code=data['code'])
#     await state.finish()  # Очистить state (удаляем data)
#     await state.set_state('*')  # Очистить state (data дальше существует)
#     msg = f'''
# api_id: {data['api_id']}
# api_hash: {data['api_hash']}
# phone: {data['phone']}
# password: {data['password']}
# links: {data['links']}
# '''
#     await message.answer(msg)
