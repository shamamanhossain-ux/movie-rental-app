
import sqlite3
from contextlib import contextmanager

DB_FILE = "rental.db"

def sqlite_connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_connection():
    conn = sqlite_connect()
    try:
        yield conn
    finally:
        conn.close()
