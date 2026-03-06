"""SQLite database access layer."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    _ensure_data_dir()
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
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


# ---- Notes ----

def insert_note(content: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        return int(cursor.lastrowid)  # type: ignore[arg-type]


def list_notes() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return list(
            conn.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC").fetchall()
        )


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?", (note_id,)
        ).fetchone()


# ---- Action Items ----

def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    with get_connection() as conn:
        ids: list[int] = []
        for item in items:
            cursor = conn.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item),
            )
            ids.append(int(cursor.lastrowid))  # type: ignore[arg-type]
        return ids


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    with get_connection() as conn:
        if note_id is None:
            return list(
                conn.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                ).fetchall()
            )
        return list(
            conn.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            ).fetchall()
        )


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
