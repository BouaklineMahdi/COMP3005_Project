# app/db_raw.py
"""
Low-level PostgreSQL access using psycopg2.

This module is used by the "raw SQL" repositories, e.g.:
- app.repositories.admins_raw
- app.repositories.members_raw
- app.repositories.trainers_raw

It exposes:

    get_connection() -> psycopg2 connection

which uses the DB settings from app.config.
"""

from contextlib import contextmanager

import psycopg2

from app import config


def get_connection():
    """
    Open and return a new psycopg2 connection using app.config settings.

    Example usage:

        from app.db_raw import get_connection

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                print(cur.fetchone())

    The context manager protocol on the connection will automatically
    close the connection at the end of the 'with' block.
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
def get_connection_ctx():
    """
    Optional helper context manager if you prefer:

        from app.db_raw import get_connection_ctx

        with get_connection_ctx() as (conn, cur):
            cur.execute("SELECT 1")
            print(cur.fetchone())

    Not required by anything currently, but safe to keep.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
