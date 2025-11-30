# app/db_raw.py
"""
Low-level PostgreSQL access using psycopg2.

Used by the "raw SQL" repositories, e.g.:
- app.repositories.admins_raw
- app.repositories.members_raw
- app.repositories.trainers_raw

Exposes:

    get_connection()  -> plain psycopg2 connection
    get_cursor(...)   -> context manager yielding a dict-like cursor
    get_connection_ctx() -> optional (conn, cur) context manager

All DB settings come from app.config.
"""

from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from app import config


def get_connection():
    """
    Open and return a new psycopg2 connection using app.config settings.

    Example:

        from app.db_raw import get_connection

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                print(cur.fetchone())

    The connection's context manager will commit on success and roll back
    on exception.
    """
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )
    return conn


@contextmanager
def get_cursor(commit: bool = False):
    """
    Convenience context manager used by members_raw, admins_raw, etc.

    Yields a cursor that returns rows as dictionaries, so code like:

        row = cur.fetchone()
        row["member_id"]

    works as expected.

    If commit=True, the connection is committed when the block exits
    without error; otherwise, changes are not committed automatically.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@contextmanager
def get_connection_ctx():
    """
    Optional helper:

        from app.db_raw import get_connection_ctx

        with get_connection_ctx() as (conn, cur):
            cur.execute("SELECT 1")
            print(cur.fetchone())

    Uses a RealDictCursor so row["col"] works.
    Always commits on success and rolls back on error.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
