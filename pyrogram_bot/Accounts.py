import json
import logging
import multiprocessing
import os
from functools import partial
import time as tm
from pyrogram.enums import ChatType
from aiogram import Bot
from pyrogram import Client, idle
from pyrogram.errors import BadRequest, SessionPasswordNeeded
from pyrogram.handlers import MessageHandler
from pyrogram_bot.database.DB import Database as db
from log import logger
import asyncio
from pyrogram_bot.AccountFunctions import get_answer, delete_files_with_extension


# db.insert_new_record_to_Accounts("29840382", "6ba30f6856f127b74c77b83b1435f20b", "7 901 570 3336", 'asdasd',
# "https://t.me/+QH8bHtAqUzFjNTYy" ) print(db.get_all_accounts())

proxy = {
    "scheme": "http",  # "socks4", "socks5" and "http" are supported
    "hostname": "35.236.207.242",
    "port": 33333
}


async def message_handler(client: Client, message, container_id):
    me = await client.get_me()
    username = f"@{me.username}".lower()
    bot_name = f"{me.first_name}".lower()
    bot_id = me.id

    chat_links = await db(container_id).get_chat_links_by_account_id(bot_id)
    if chat_links is not None:
        for chat_link in chat_links.split(","):
            print(chat_link)
            try:
                await client.join_chat(chat_link)
                await asyncio.sleep(100)
            except Exception as e:
                logging.error(f"Error while joining chat: {str(e)}")

    if message.text == "привет":
        await message.reply("Привет!")
    if message.text is None:
        message.text = message.caption
    if message.chat.type == ChatType.SUPERGROUP or message.chat.type == ChatType.GROUP:
        if message.text == '':
            return
        await client.read_chat_history(message.chat.id)
        # loop = asyncio.get_event_loop()
        # msg = await loop.run_in_executor(None, answer_from_chatgpt, message.text, False, message.from_user.id)
        # await message.answer(text=msg['text'])
        await get_answer(message.text, message, bot_id=bot_id, bot_name=bot_name, username=username,
                         process_name=container_id)

    print(f"Received message on: {message.text}")


async def send_alert(msg):
    bot_token = os.getenv('BOT_TOKEN')
    bot = Bot(bot_token)
    admins = []
    for admin in admins:
        try:
            await bot.send_message(admin.chat_id, text='Alert!\n' + msg)
        except Exception as e:
            logger.error("Exception | %s" % e)


async def add_account(api_id, api_hash, phone, password, chat_links, apps, container_id):
    app = Client(str(phone), api_id, api_hash, proxy=proxy)
    print(phone)
    phone = str(phone)

    is_authorized = await app.connect()
    while not is_authorized:
        sent_code = await app.send_code(phone)

        # ждём код
        code = '0'
        while code == '0':
            temp = await db(container_id).get_code_for_account(api_id, api_hash, phone)
            print(temp[0])
            if temp[0] == '0':
                await asyncio.sleep(2)
            else:
                code = temp[0]
                break
        print('code:' + code)
        print(code)
        try:
            await app.sign_in(phone, sent_code.phone_code_hash, code)
        except BadRequest as e:
            print(e.MESSAGE)
            await db(container_id).update_code(api_id=api_id, api_hash=api_hash,
                                               phone_number=phone, new_code=0)
            continue
        except SessionPasswordNeeded as e:
            print(e.MESSAGE)

            try:
                passwd_hint = await app.get_password_hint()
                print(passwd_hint)
                await app.check_password(password)
            except Exception as e:
                print(e)
        me = await app.get_me()
        print(me)

        await db(container_id).update_account_id(api_id, api_hash, phone, me.id)
    await app.disconnect()

    await app.start()

    apps.append(app)

    app.add_handler(MessageHandler(message_handler))
    # for chat_link in chat_links.split(","):
    #     print(chat_link)
    #     try:
    #         await app.join_chat(chat_link)
    #         await asyncio.sleep(100)
    #     except Exception as e:
    #         logging.error(f"Error while joining chat: {str(e)}")


async def remove_account(container_id, phone):
    db(container_id).delete_account(phone)
    delete_files_with_extension(container_id)
    # написать код для удаления сессии


async def main(container_id, queue):
    apps = []
    logger.info('OK')

    all_accounts = await db(container_id).get_all_accounts()
    logger.info('All accounts - %s' % all_accounts)

    if all_accounts is not None:
        tasks = []
        for account in all_accounts:
            api_id, api_hash, phone, password, chat_links = account[2:7]
            task = asyncio.create_task(add_account(api_id, api_hash, phone, password, chat_links, apps, container_id))
            tasks.append(task)

        await asyncio.gather(*tasks)  # Ожидаем завершения всех задач

        await idle()

        for app in apps.copy():
            await remove_account(app, apps)

    # start
    # try:
    #     await dp.start_polling()
    # finally:
    #     # Остановили бота и закрываем сессию
    #     await dp.storage.close()
    #     await dp.storage.wait_closed()
    #     await bot.session.close()
