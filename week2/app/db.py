from __future__ import annotations

import sqlite3
from typing import Optional

from .config import get_settings


class DatabaseError(RuntimeError):
    pass


class RecordNotFoundError(DatabaseError):
    pass


NoteRecord = dict[str, int | str]
ActionItemRecord = dict[str, int | str | bool | None]


def get_db_path() -> str:
    return str(get_settings().db_path)


def ensure_data_directory_exists() -> None:
    get_settings().data_dir.mkdir(parents=True, exist_ok=True)


def _note_from_row(row: sqlite3.Row) -> NoteRecord:
    return {
        "id": int(row["id"]),
        "content": str(row["content"]),
        "created_at": str(row["created_at"]),
    }


def _action_item_from_row(row: sqlite3.Row) -> ActionItemRecord:
    return {
        "id": int(row["id"]),
        "note_id": int(row["note_id"]) if row["note_id"] is not None else None,
        "text": str(row["text"]),
        "done": bool(row["done"]),
        "created_at": str(row["created_at"]),
    }


def get_connection() -> sqlite3.Connection:
    ensure_data_directory_exists()
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    try:
        ensure_data_directory_exists()
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )
            connection.commit()
    except sqlite3.Error as exc:
        raise DatabaseError("Failed to initialize the database") from exc


def insert_note(content: str) -> int:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise DatabaseError("Failed to insert note") from exc


def list_notes() -> list[NoteRecord]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            return [_note_from_row(row) for row in cursor.fetchall()]
    except sqlite3.Error as exc:
        raise DatabaseError("Failed to list notes") from exc


def get_note(note_id: int) -> Optional[NoteRecord]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            row = cursor.fetchone()
            return _note_from_row(row) if row is not None else None
    except sqlite3.Error as exc:
        raise DatabaseError("Failed to fetch note") from exc


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            ids: list[int] = []
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cursor.lastrowid))
            connection.commit()
            return ids
    except sqlite3.Error as exc:
        raise DatabaseError("Failed to insert action items") from exc


def list_action_items(note_id: Optional[int] = None) -> list[ActionItemRecord]:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            return [_action_item_from_row(row) for row in cursor.fetchall()]
    except sqlite3.Error as exc:
        raise DatabaseError("Failed to list action items") from exc


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            if cursor.rowcount == 0:
                raise RecordNotFoundError(f"Action item {action_item_id} not found")
            connection.commit()
    except RecordNotFoundError:
        raise
    except sqlite3.Error as exc:
        raise DatabaseError("Failed to update action item") from exc

