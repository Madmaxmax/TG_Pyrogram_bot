import sqlite3
from pathlib import Path


class Database:
    def __init__(self):
        cwd_path = Path.cwd()
        setting_path = Path(cwd_path, "aiogram_bot", "database_storage", "Settings.db")
        self.conn = sqlite3.connect(setting_path)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS logging(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Time TEXT,
        Phone TEXT,
        Account_id TEXT,
        Message TEXT
        );""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Containers(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Delay INT NOT NULL,
        Is_ready TEXT NOT NULL
        );""")
        self.conn.commit()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Proxy(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        adress TEXT,
        port TEXT NOT NULL,
        login TEXT NOT NULL,
        password TEXT NOT NULL
        );""")
        self.conn.commit()

    def add_container(self, name):
        self.cur.execute("INSERT INTO Containers (Name, Delay, Is_ready) VALUES(?,?,?);",
                         [name, 60, True])
        self.conn.commit()
        self.cur.execute("SELECT ID FROM Containers WHERE Name = ?", [name])
        id_ = self.cur.fetchone()[0]
        return id_

    def get_containers(self):
        self.cur.execute("SELECT * FROM Containers")
        ids = self.cur.fetchall()
        return ids

    def get_container(self, container_id):
        self.cur.execute(f"SELECT * FROM Containers WHERE ID = '{container_id}'")
        result = self.cur.fetchall()
        print(result[0])
        return result[0]

    def update_container(self, name, key, value):
        self.cur.execute(f"UPDATE Containers SET '{key}' = '{value}' WHERE Name = '{name}';")
        self.conn.commit()
        return
