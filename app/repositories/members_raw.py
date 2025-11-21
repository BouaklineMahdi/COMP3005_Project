# app/repositories/members_raw.py
from passlib.hash import bcrypt
from app.db_raw import get_cursor
from app.models.schemas import MemberRegisterRequest

def register_member(data: MemberRegisterRequest) -> int:
    """
    Insert a new member and return the generated member_id.
    """
    password_hash = bcrypt.hash(data.password)

    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO member (name, dob, gender, email, phone, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING member_id;
            """,
            (data.name, data.dob, data.gender, data.email, data.phone, password_hash),
        )
        row = cur.fetchone()
        return row["member_id"]
