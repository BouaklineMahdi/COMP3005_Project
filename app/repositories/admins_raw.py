# app/repositories/admins_raw.py
"""
Raw-SQL implementation for admin operations.

Used by:
- /admins/db-health
- /admins/register
- /admins/rooms (GET/POST)
- /admins/classes (GET/POST)
- /auth/admin-login  (via verify_admin_credentials)
- /members/{member_id}/classes/{class_id}/register
"""

from typing import List, Optional

from passlib.hash import bcrypt

from app.db_raw import get_connection
from app.models.schemas import (
    AdminRegisterRequest,
    RoomCreate,
    RoomResponse,
    ClassCreate,
    ClassResponse,
)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

def get_db_health() -> dict:
    """
    Simple DB health check: SELECT 1.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
    return {"status": "ok"}


# ---------------------------------------------------------
# Admin registration & login
# ---------------------------------------------------------

def register_admin(data: AdminRegisterRequest) -> int:
    """
    Insert a new admin into the admin table.
    """
    password_hash = bcrypt.hash(data.password)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO admin (name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING admin_id;
                """,
                (data.name, data.email, password_hash),
            )
            admin_id = cur.fetchone()[0]
        conn.commit()

    return admin_id


def verify_admin_credentials(email: str, password: str) -> Optional[int]:
    """
    Used by /auth/admin-login.

    Returns admin_id if credentials are valid, otherwise None.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT admin_id, password_hash
                FROM admin
                WHERE email = %s;
                """,
                (email,),
            )
            row = cur.fetchone()

    if not row:
        return None

    admin_id, password_hash = row
    if not bcrypt.verify(password, password_hash):
        return None

    return admin_id


# ---------------------------------------------------------
# Rooms
# ---------------------------------------------------------

def list_rooms() -> List[RoomResponse]:
    """
    Return all rooms.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT room_id, name, capacity
                FROM room
                ORDER BY room_id;
                """
            )
            rows = cur.fetchall()

    return [
        RoomResponse(room_id=r[0], name=r[1], capacity=r[2])
        for r in rows
    ]


def create_room(data: RoomCreate) -> RoomResponse:
    """
    Create a new room and return it.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO room (name, capacity)
                VALUES (%s, %s)
                RETURNING room_id, name, capacity;
                """,
                (data.name, data.capacity),
            )
            row = cur.fetchone()
        conn.commit()

    return RoomResponse(room_id=row[0], name=row[1], capacity=row[2])


# ---------------------------------------------------------
# Classes
# ---------------------------------------------------------

def list_classes() -> List[ClassResponse]:
    """
    Return all fitness classes.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT class_id, name, start_time, capacity, trainer_id, room_id
                FROM class
                ORDER BY class_id;
                """
            )
            rows = cur.fetchall()

    return [
        ClassResponse(
            class_id=r[0],
            name=r[1],
            start_time=r[2],
            capacity=r[3],
            trainer_id=r[4],
            room_id=r[5],
        )
        for r in rows
    ]


def create_class(data: ClassCreate) -> ClassResponse:
    """
    Create a new fitness class and return it.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO class (name, start_time, capacity, trainer_id, room_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING class_id, name, start_time, capacity, trainer_id, room_id;
                """,
                (
                    data.name,
                    data.start_time,
                    data.capacity,
                    data.trainer_id,
                    data.room_id,
                ),
            )
            row = cur.fetchone()
        conn.commit()

    return ClassResponse(
        class_id=row[0],
        name=row[1],
        start_time=row[2],
        capacity=row[3],
        trainer_id=row[4],
        room_id=row[5],
    )


# ---------------------------------------------------------
# Class registration (used by members router)
# ---------------------------------------------------------

def register_member_for_class(member_id: int, class_id: int) -> None:
    """
    Register a member for a class.

    IMPORTANT:
    - Sets registered_at to NOW() to satisfy NOT NULL constraint.
    - Relies on DB trigger `trg_class_capacity` to enforce capacity.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO class_registration (member_id, class_id, registered_at)
                VALUES (%s, %s, NOW());
                """,
                (member_id, class_id),
            )
        conn.commit()
