import sqlite3
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Database:
    def __init__(self, path: str = "database.db"):
        self.path = path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _create_tables(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        role TEXT,
                        content TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы: {e}")

    def save_user(self, user_id: int):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute("INSERT INTO users(user_id) VALUES (?)", (user_id,))
                    conn.commit()
        except Exception as e:
            logger.error(f"Ошибка save_user: {e}")

    def delete_messages(self, user_id: int):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE user_id=?", (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка delete_messages: {e}")

    def get_messages(self, user_id: int, limit: int = 50) -> List[Tuple[str, str]]:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, content FROM messages WHERE user_id=? ORDER BY id ASC LIMIT ?",
                    (user_id, limit),
                )
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            logger.error(f"Ошибка get_messages: {e}")
            return []

    def save_message(self, user_id: int, role: str, content: str):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
                    (user_id, role, content),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка save_message: {e}")
