import sqlite3
import os
import random

DATABASE = 'history.db'

def generate_random():
    return ''.join(random.choices('0123456789abcdef', k=16))

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS history')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    table_name = f'_{generate_random()}'
    print(table_name)
    column_name = f'flag_{generate_random()}'

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {column_name} TEXT NOT NULL
        )
    ''')

    print(column_name)

    cursor.execute(f'''
        INSERT INTO {table_name} ({column_name}) VALUES (?)
    ''', ('nexus{fake_flag} ',))

    conn.commit()
    conn.close()

def insert_into_history(filename, content_type):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (filename, content_type) VALUES (?, ?)
    ''', (filename, content_type))
    conn.commit()
    conn.close()
