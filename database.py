"""
database.py

Модуль для работы с базой данных (SQLite).
Хранит колоды и карты, умеет создавать таблицы, добавлять/редактировать карты и колоды.
"""

import sqlite3
from typing import Optional

_conn: Optional[sqlite3.Connection] = None

def init_db():
    global _conn
    _conn = sqlite3.connect('tarot_data.db')
    cursor = _conn.cursor()

    # Таблица колод
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
    ''')

    # Таблица карт
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            card_name TEXT NOT NULL,
            description TEXT,
            image_path TEXT,
            FOREIGN KEY(deck_id) REFERENCES decks(id)
        );
    ''')

    _conn.commit()

def get_connection() -> sqlite3.Connection:
    if _conn is None:
        raise ConnectionError("База не инициализирована! Сначала вызовите init_db().")
    return _conn

def close_db():
    global _conn
    if _conn:
        _conn.close()
        _conn = None

def create_deck(deck_name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO decks(name) VALUES(?);", (deck_name,))
    conn.commit()
    return cursor.lastrowid

def get_deck_id(deck_name: str) -> Optional[int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM decks WHERE name=?;", (deck_name,))
    row = cursor.fetchone()
    return row[0] if row else None

def create_or_update_card(deck_id: int, card_name: str, description: str, image_path: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM cards WHERE deck_id=? AND card_name=?
    """, (deck_id, card_name))
    row = cursor.fetchone()
    if row:
        card_id = row[0]
        cursor.execute("""
            UPDATE cards
            SET description=?, image_path=?
            WHERE id=?
        """, (description, image_path, card_id))
    else:
        cursor.execute("""
            INSERT INTO cards(deck_id, card_name, description, image_path)
            VALUES(?, ?, ?, ?)
        """, (deck_id, card_name, description, image_path))
        card_id = cursor.lastrowid

    conn.commit()
    return card_id

def get_card(deck_id: int, card_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT description, image_path 
        FROM cards
        WHERE deck_id=? AND card_name=?
    """, (deck_id, card_name))
    return cursor.fetchone()

def get_all_decks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM decks;")
    rows = cursor.fetchall()
    return [r[0] for r in rows]
