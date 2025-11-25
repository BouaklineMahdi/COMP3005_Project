# app/repositories/admins_raw.py
from passlib.hash import bcrypt
from app.db_raw import get_cursor
from app.models.schemas import (
    RoomCreate,
    RoomResponse,
    ClassCreate,
    ClassResponse,
    AdminRegisterRequest,
)


def register_admin(data: AdminRegisterRequest) -> int:
    """
    Create a new admin with a hashed password.
    """
    password_hash = bcrypt.hash(data.password)
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO admin (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING admin_id;
            """,
            (data.name, data.email, password_hash),
        )
        row = cur.fetchone()
        return row["admin_id"]


def create_room(data: RoomCreate) -> int:
    """
    Insert a new room and return room_id.
    """
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO room (name, capacity)
            VALUES (%s, %s)
            RETURNING room_id;
            """,
            (data.name, data.capacity),
        )
        row = cur.fetchone()
        return row["room_id"]


def list_rooms() -> list[RoomResponse]:
    """
    Return all rooms.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT room_id, name, capacity
            FROM room
            ORDER BY room_id;
            """
        )
        rows = cur.fetchall()
        return [RoomResponse(**row) for row in rows]


def create_class(data: ClassCreate) -> int:
    """
    Insert a new class and return class_id.
    """
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO class (name, start_time, capacity, trainer_id, room_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING class_id;
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
        return row["class_id"]


def list_classes() -> list[ClassResponse]:
    """
    Return all classes.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT class_id, name, start_time, capacity, trainer_id, room_id
            FROM class
            ORDER BY class_id;
            """
        )
        rows = cur.fetchall()
        return [ClassResponse(**row) for row in rows]


def register_member_for_class(member_id: int, class_id: int) -> None:
    """
    Register a member for a class.
    Uses trigger trg_class_capacity to enforce capacity.
    """
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO class_registration (member_id, class_id)
            VALUES (%s, %s);
            """,
            (member_id, class_id),
        )
