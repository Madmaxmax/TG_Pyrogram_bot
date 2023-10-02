import logging
import sqlite3


class Database:
    def __init__(self, container_id):
        self.database_path = f'pyrogram_bot/database_storage/container_{container_id}.db'
        self.conn = sqlite3.connect(self.database_path)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Accounts'")
        table_exists = self.cursor.fetchone()

        if not table_exists:
            self.cursor.execute("""
                CREATE TABLE Accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INT,
                    api_id TEXT,
                    api_hash TEXT,
                    phone_number TEXT,
                    password TEXT,
                    Chat_links TEXT NOT NULL,
                    Code TEXT NOT NULL
                )
            """)
            self.conn.commit()

            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Prompt_and_API_Keys'")
            new_table_exists = self.cursor.fetchone()

            if not new_table_exists:
                self.cursor.execute("""
                       CREATE TABLE Prompt_and_API_Keys (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           TitlePrompt TEXT,
                           PromptText TEXT,
                           API_Key TEXT
                       )
                   """)

    async def get_all_accounts(self):
        self.cursor.execute("SELECT * FROM Accounts")
        return self.cursor.fetchall()

    async def get_selected_accounts(self):
        self.cursor.execute("SELECT api_id, api_hash, phone_number, password, Chat_links FROM Accounts")
        return self.cursor.fetchall()

    async def insert_new_record_to_Accounts(self, api_id, api_hash, phone_number, password, chat_links, account_id=0,
                                            code=0):
        print('add')
        try:
            self.cursor.execute("""
                INSERT INTO Accounts (account_id, api_id, api_hash, phone_number, password, Chat_links, Code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (account_id, api_id, api_hash, phone_number, password, chat_links, code))
            self.conn.commit()
        except Exception as e:
            logging.error('%s' % e)
        print('add_true')

    async def insert_new_record_to_Prompt(self, title, text):
        self.cursor.execute("""
            INSERT INTO Prompts (title, text)
            VALUES (?, ?)
        """, (title, text))
        self.conn.commit()

    async def get_chat_links_for_account(self, api_id, api_hash, phone_number):
        self.cursor.execute("""
            SELECT Chat_links FROM Accounts
            WHERE phone_number = ?
        """, (phone_number,))

        result = self.cursor.fetchone()

        if result:
            chat_links_str = result[0]  # Получаем строку с чат-ссылками
            chat_links_list = chat_links_str.split(",")  # Разделяем строку на список

            return chat_links_list

        return []

    async def get_passwd_for_account(self, api_id, api_hash, phone_number):
        self.cursor.execute("""
            SELECT password FROM Accounts
            WHERE api_id = ? AND api_hash = ? AND phone_number = ?
        """, (api_id, api_hash, phone_number))
        return self.cursor.fetchone()[0]

    async def update_passwd(self, api_id, api_hash, phone_number, passwd):
        self.cursor.execute(
            f"UPDATE Accounts SET password = '{passwd}' WHERE api_id = '{api_id}' AND api_hash = '{api_hash}' AND phone_number = '{phone_number}';")
        self.conn.commit()

    async def get_code_for_account(self, api_id, api_hash, phone_number):
        self.cursor.execute("""
            SELECT Code FROM Accounts
            WHERE api_id = ? AND api_hash = ? AND phone_number = ?
        """, (api_id, api_hash, phone_number))
        return self.cursor.fetchone()

    async def update_code(self, api_id, api_hash, phone_number, new_code):
        self.cursor.execute(
            f"UPDATE Accounts SET Code = '{new_code}' WHERE api_id = '{api_id}' AND api_hash = '{api_hash}' AND phone_number = '{phone_number}';")
        self.conn.commit()

    async def update_account_id(self, api_id, api_hash, phone_number, account_id):
        self.cursor.execute(
            f"UPDATE Accounts SET account_id = '{account_id}' WHERE api_id = '{api_id}' AND api_hash = '{api_hash}' AND phone_number = '{phone_number}';")
        self.conn.commit()

    async def add_prompt_and_key(self, title_prompt, prompt_text, api_key):
        self.cursor.execute("""
                        INSERT INTO Prompt_and_API_Keys (TitlePrompt, PromptText, API_Key)
                        VALUES (?, ?, ?)
                    """, (title_prompt, prompt_text, api_key))
        self.conn.commit()

    async def get_prompt_text(self):
        self.cursor.execute("SELECT PromptText FROM Prompt_and_API_Keys")
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    async def delete_prompt(self, id_):
        self.cursor.execute(f"DELETE FROM Prompt_and_API_Keys WHERE id = '{id_}'")
        self.conn.commit()

    async def get_prompt(self):
        self.cursor.execute("SELECT * FROM Prompt_and_API_Keys")
        result = self.cursor.fetchall()
        if result:
            return result
        else:
            return None

    async def get_api_key(self):
        self.cursor.execute("SELECT API_Key FROM Prompt_and_API_Keys")
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    async def get_chat_links_by_account_id(self, account_id):
        self.cursor.execute("SELECT Chat_links FROM Accounts WHERE account_id = ?", (account_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def delete_account(self, phone_number):
        self.cursor.execute("DELETE FROM Accounts WHERE phone_number = ?", (phone_number,))
        self.conn.commit()

    async def close(self):
        self.conn.close()
