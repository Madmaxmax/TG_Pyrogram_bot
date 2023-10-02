from aiogram import types
from aiogram_bot.database.DB import Database as set_db


class Keyboard:
    def __init__(self):
        self.keyboard = types.InlineKeyboardMarkup()
        self.button = types.InlineKeyboardButton

    def welcome(self):
        containers = set_db().get_containers()
        buttons = []
        for container in containers:
            print(container)
            buttons.append(self.button(text=f'Группа {container[1]}', callback_data=f'container_{container[0]}'))
        self.keyboard.add(*buttons)
        self.keyboard.add(self.button(text='Добавить', callback_data='add_container'))
        return self.keyboard

    def my_container(self, accounts, container_id):
        is_ready = set_db().get_container(container_id)
        if int(is_ready[3]) == 1:
            buttons = [
                self.button(text='Аккаунты', callback_data='my_accounts'),
                self.button(text='Настройки', callback_data='my_settings'),
                self.button(text='Остановить', callback_data='my_revers'),
                self.button(text='Назад', callback_data='welcome_call'),
            ]
        else:
            buttons = [
                self.button(text='Аккаунты', callback_data='my_accounts'),
                self.button(text='Настройки', callback_data='my_settings'),
                self.button(text='Запустить', callback_data='my_revers'),
                self.button(text='Назад', callback_data='welcome_call'),
            ]
        self.keyboard.add(buttons[0], buttons[1])
        self.keyboard.add(buttons[2])
        self.keyboard.add(buttons[3])
        return self.keyboard

    def container_setting(self):
        buttons = [
            self.button(text='Промпт', callback_data='my_prompt'),
            self.button(text='Прокси', callback_data='my_proxy'),
            self.button(text='Задержка комментирования', callback_data='my_delays'),
            self.button(text='Назад', callback_data='my_container'),
        ]
        self.keyboard.add(buttons[0], buttons[1], buttons[2])
        self.keyboard.add(buttons[3])
        return self.keyboard

    def proxy_setting(self):
        buttons = [
            self.button(text='Промпт', callback_data='my_prompt')
        ]
        self.keyboard.add(buttons[0], buttons[1], buttons[2])
        self.keyboard.add(buttons[3])
        self.keyboard.add(buttons[4])
        return self.keyboard

    def get_accounts(self, accounts):
        buttons = []
        if accounts:
            for account in accounts:
                buttons.append(self.button(text=f'Аккаунт {account[4]}', callback_data=f'my_account_{account[4]}'))
            self.keyboard.add(*buttons)
        if len(accounts) < 25:
            self.keyboard.add(self.button(text='Добавить', callback_data='add_account'))
        self.keyboard.add(self.button(text='Назад', callback_data='my_container'))
        return self.keyboard

    def go_home(self):
        self.keyboard.add(self.button(text='Вернуться в начало', callback_data='my_accounts'))
        return self.keyboard
