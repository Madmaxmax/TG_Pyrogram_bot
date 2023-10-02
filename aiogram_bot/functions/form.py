from aiogram.types import Message


async def get_form(message: Message):
    await message.answer(message.text)
