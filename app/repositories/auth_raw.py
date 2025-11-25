# app/repositories/auth_raw.py
from passlib.hash import bcrypt
from app.db_raw import get_cursor


def _check_credentials(table: str, id_column: str, email: str, password: str):
    """
    Generic helper to check credentials in member/trainer/admin tables.
    Returns (user_id, email) if valid, or None if invalid.
    """
    with get_cursor() as cur:
        cur.execute(
            f"""
            SELECT {id_column} AS user_id, email, password_hash
            FROM {table}
            WHERE email = %s;
            """,
            (email,),
        )
        row = cur.fetchone()
        if not row:
            return None
        if not bcrypt.verify(password, row["password_hash"]):
            return None
        return row["user_id"], row["email"]


def login_member(email: str, password: str):
    return _check_credentials("member", "member_id", email, password)


def login_trainer(email: str, password: str):
    return _check_credentials("trainer", "trainer_id", email, password)


def login_admin(email: str, password: str):
    return _check_credentials("admin", "admin_id", email, password)
