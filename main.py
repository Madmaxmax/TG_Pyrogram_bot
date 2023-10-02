import asyncio
import os
import multiprocessing
import time

from env import load_env
from initialisation import start
from log import start_log, logger
from pyrogram_bot.Accounts import main as account_main
from pyrogram_bot.database.DB import Database
from aiogram_bot.database.DB import Database as set_db


def find_db_files(directory):
    db_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".db"):
                db_files.append(os.path.join(root, file))

    return db_files


async def run_pyrogram_bot(container_id, queue):
    try:
        Database(container_id).create_table()
        start_log()
        await account_main(container_id, queue)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Pyrogram stopped!")
    except Exception as e:
        logger.critical("Pyrogram crashed! | %s" % e)


async def my_func():
    print('ready1')
    await asyncio.sleep(10)
    print('ready2')


def run_pyrogram(container_id, queue):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_pyrogram_bot(container_id, queue))


def run_containers(queue):
    containers = set_db().get_containers()
    start_log()
    processes = {}
    for item in containers:
        if int(item[3]) != 1:
            continue
        thread = multiprocessing.Process(target=run_pyrogram, args=(item[0], queue))
        processes[item[0]] = thread
        thread.start()
    while True:
        message = queue.get()
        logger.info('Get Message - %s' % message)
        if 'restart_container' in str(message):
            try:
                container_id = int(message[18:])
                try:
                    process = processes[container_id]
                except:
                    new_thread = multiprocessing.Process(target=run_pyrogram, args=(container_id, queue))
                    processes[container_id] = new_thread
                    new_thread.start()
                    continue

                process.terminate()  # Завершаем текущий процесс

                # Запускаем новый процесс
                new_thread = multiprocessing.Process(target=run_pyrogram, args=(container_id, queue))
                processes[container_id] = new_thread
                new_thread.start()
            except Exception as e:
                logger.info('Except %s' % e)
        if 'stop_container' in str(message):
            try:
                container_id = int(message[15:])
                container = set_db().get_container(int(container_id))
                if int(container[3]) == 1:
                    set_db().update_container(container[1], 'Is_ready', '0')
                process = processes[container_id]
                process.terminate()  # Завершаем текущий процесс
            except Exception as e:
                logger.info('Except %s' % e)


def main():
    load_env()  # Загружаем перменные окружения

    # Запускаем Aiogram и Pyrogram
    start(run_containers=run_containers)


if __name__ == "__main__":
    main()
    # run_containers()
