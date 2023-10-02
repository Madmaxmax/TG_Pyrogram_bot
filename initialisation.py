import asyncio
import multiprocessing
import os
import time
from multiprocessing import Queue

from aiogram_bot.Bot import main as bot_main
from log import logger, start_log


async def run_aiogram_bot(queue):
    try:
        start_log()
        await bot_main(queue)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Aigoram stopped!")
    except Exception as e:
        logger.critical("Aigoram crashed! | %s" % e)


def run_aiogram(queue):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_aiogram_bot(queue))


def start(run_containers):
    queue = Queue()
    processes = []
    process1 = multiprocessing.Process(target=run_aiogram, args=(queue,))
    processes.append(process1)
    process1.start()
    # process2 = multiprocessing.Process(target=run_containers, args=(queue,))
    # processes.append(process2)
    # process2.start()

