from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "service_center.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          username TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          salt TEXT NOT NULL,
          role TEXT NOT NULL DEFAULT 'AGENT',
          active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS tickets(
          id INTEGER PRIMARY KEY,
          public_id TEXT NOT NULL UNIQUE,
          title TEXT NOT NULL,
          customer_name TEXT,
          category TEXT,
          status TEXT NOT NULL DEFAULT 'OPEN',
          priority TEXT NOT NULL DEFAULT 'NORMAL',
          owner_id INTEGER REFERENCES users(id),
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ticket_events(
          id INTEGER PRIMARY KEY,
          ticket_id INTEGER NOT NULL REFERENCES tickets(id),
          actor_id INTEGER REFERENCES users(id),
          event_type TEXT NOT NULL,
          details TEXT,
          occurred_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS settings(
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        """)
