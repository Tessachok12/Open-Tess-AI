# db_manager.py
import sqlite3
import os

class DatabaseManager:
    def __init__(self, bot_name, lang='ru'):
        self.bot_name = bot_name
        self.lang = lang
        self.db_path = f"{bot_name}.otai.{lang}.db"
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dialogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_dialog(self, user_msg, bot_msg):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO dialogs (user_message, bot_response) VALUES (?, ?)',
                       (user_msg, bot_msg))
        self.conn.commit()

    def get_all_dialogs(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_message, bot_response FROM dialogs')
        return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
