import asyncio
import logging
from functools import partial

import openai
import os
from pyrogram.enums import ChatType

from log import logger
from pyrogram_bot.database.DB import Database as db


async def answer_from_chatgpt(user_message, process_name, chat_id: int, post: bool = None, mailing_text: bool = None):
    try:
        user_message = user_message.replace('\n', '')
        setting_text = await db(process_name).get_prompt_text()
        await db(process_name).close()
        # Создаем путь к файлу с диалогами и проверяем, существует ли он
        filename = f"pyrogram_bot/dialogs/{chat_id}.txt"
        if not os.path.isfile(filename):
            open(filename, "w", encoding="UTF-8").close()

        # Читаем и обрабатываем предыдущие сообщения
        with open(filename, "r+", encoding="UTF-8") as f:
            # Читаем все строки из файла и удаляем первые две
            lines = f.readlines()
            if len(lines) >= 12:
                del lines[:2]
                # Перемещаем указатель в начало файла и записываем новые строки
                f.seek(0)
                f.writelines(lines)
                f.truncate()

            # Читаем содержимое файла для использования в промпте
            f.seek(0)
            txt = f.readlines()
            messages = [{"role": "system",
                         "content": 'AI соответствует этим параметрам: '+setting_text}]
            # добавляем инструкции в промпт
            if mailing_text and len(str(messages)) < 2000:
                messages.append({"role": "system",
                                 "content": "Тебе нужно поддержать диалог"})
            if post and len(str(messages)) < 2000:
                messages.append({"role": "system",
                                 "content": "Нужно прокомментировать данный пост,ты не являешься автором поста, "
                                            "но ты должна рассказать что то интересное. Нужно информация чтобы людям "
                                            "стало интересно. Нужно отвечать ярко красочно и добавлять смайлики.  "
                                            "Быть максимально на позитиве и красочно"
                                            "описывать. Повторять или цитировать текст категорически нельзя "})
            elif len(str(messages)) < 2000:
                messages.append({"role": "system",
                                 "content": "Я хочу, чтобы ты выступил как асистент. Тебе будут писать разные "
                                            "вопросы, а твоя задача грамотно, вежливо и кратко на них отвечать. "})
            # # добавляем В промпт историю общения
            # if txt:
            #     for i in range(len(lines)):
            #         if len(str(messages)) < 2000:
            #             messages.append(
            #                 {"role": f"{lines[i][:lines[i].find(':')]}", "content": lines[i][lines[i].find(':') + 2:]})
            #         else:
            #             break
            # проверяем не вышли ли из границ промпта
            new_messages = messages
            if len(str(new_messages.append({"role": 'user', "content": user_message}))) > 4000:
                messages = [{"role": "system",
                             "content": 'AI соответствует этим параметрам: ' + setting_text}]
                if post:
                    messages.append({"role": "system",
                                     "content": "Нужно прокомментировать данный пост,ты не являешься автором поста, "
                                                "но ты должна рассказать что то интересное. Нужно информация чтобы людям "
                                                "стало интересно. Нужно отвечать ярко красочно и добавлять смайлики.  "
                                                "Быть максимально на позитиве и красочно"
                                                "описывать. Повторять или цитировать текст категорически нельзя "})
                if mailing_text:
                    messages.append({"role": "system",
                                     "content": "Я хочу, чтобы ты выступил как асистент. Тебе будут писать разные "
                                                "вопросы, а твоя задача грамотно, вежливо и кратко на них отвечать. "})
            else:
                messages.append({"role": 'user', "content": user_message})

            # Подключаемся к Chat GPT API и получаем ответ от AI
            openai.api_key = await db(process_name).get_api_key()
            await db(process_name).close()
            print(messages)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            # Получаем текст ответа AI и записываем диалог в файл
            text = response.choices[0].message.content
            print(response)
            out = text
            text = text.replace('\n', ' ')
            text = "\n".join(filter(lambda x: x.strip(), text.splitlines()))
            with open(filename, 'a+', encoding="UTF-8") as a:
                a.write(f"user: {user_message.strip()}\n")
                a.write(f"assistant: {text}\n")
            # Возвращаем переведенный на русский язык текст ответа AI
            return out
    except Exception as e:
        logger.error('Ошибка с генерацией ответа - %s' % e)


async def get_answer(message_text, message, bot_id, bot_name, username, process_name):
    # Пост с канала
    try:
        if message.forward_from_chat.type == ChatType.CHANNEL:
            # text = 'ответ на пост'
            # loop = asyncio.get_event_loop()
            text = await answer_from_chatgpt(message_text, process_name, message.chat.id, post=True)
            await message.reply(text=text)
            return
    except Exception as e:
        logger.error('Ошибка с генерацией ответа - %s' % e)
    try:
        if message.reply_to_message.from_user.id == bot_id:
            # loop = asyncio.get_event_loop()
            text = await answer_from_chatgpt(message_text, process_name, message.chat.id, mailing_text=True)
            await message.reply(text=text)
            return
    except Exception as e:
        logger.error('Ошибка с генерацией ответа - %s' % e)
    try:
        if bot_name in message_text.lower() or username in message_text.lower():
            # text = 'ответ на тег'
            # loop = asyncio.get_event_loop()
            text = await answer_from_chatgpt(message_text, process_name, message.chat.id, mailing_text=True)
            await message.reply(text=text)
            return
    except Exception as e:
        logger.error('Ошибка с генерацией ответа - %s' % e)


def delete_files_with_extension(directory):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".session"):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                logging.info(f"Deleted file: {file_path}")
    except Exception as e:
        logging.error(f"Error deleting files: {str(e)}")
