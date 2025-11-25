# app/repositories/trainers_raw.py
from passlib.hash import bcrypt
from app.db_raw import get_cursor
from app.models.schemas import (
    TrainerAvailabilityCreate,
    TrainerAvailabilityResponse,
    TrainerScheduleItem,
    TrainerRegisterRequest,
)


def register_trainer(data: TrainerRegisterRequest) -> int:
    """
    Create a new trainer with a hashed password.
    """
    password_hash = bcrypt.hash(data.password)
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO trainer (name, email, specialization, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING trainer_id;
            """,
            (data.name, data.email, data.specialization, password_hash),
        )
        row = cur.fetchone()
        return row["trainer_id"]


def add_availability(trainer_id: int, data: TrainerAvailabilityCreate) -> int:
    """
    Insert a new availability block for a trainer and return availability_id.
    """
    if data.end_time <= data.start_time:
        raise ValueError("end_time must be after start_time")

    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO trainer_availability (trainer_id, start_time, end_time)
            VALUES (%s, %s, %s)
            RETURNING availability_id;
            """,
            (trainer_id, data.start_time, data.end_time),
        )
        row = cur.fetchone()
        return row["availability_id"]


def list_availability(trainer_id: int) -> list[TrainerAvailabilityResponse]:
    """
    Return all availability blocks for this trainer, ordered by start_time.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT availability_id, trainer_id, start_time, end_time
            FROM trainer_availability
            WHERE trainer_id = %s
            ORDER BY start_time;
            """,
            (trainer_id,),
        )
        rows = cur.fetchall()
        return [TrainerAvailabilityResponse(**row) for row in rows]


def get_trainer_schedule(trainer_id: int) -> list[TrainerScheduleItem]:
    """
    Combined schedule for trainer:
    - PT sessions from ptsession
    - Classes from class
    """
    items: list[TrainerScheduleItem] = []

    with get_cursor() as cur:
        # PT sessions
        cur.execute(
            """
            SELECT
                'pt_session' AS item_type,
                start_time,
                end_time,
                'PT session with member ' || member_id::text AS title
            FROM ptsession
            WHERE trainer_id = %s
            """,
            (trainer_id,),
        )
        for row in cur.fetchall():
            items.append(TrainerScheduleItem(**row))

        # Classes
        cur.execute(
            """
            SELECT
                'class' AS item_type,
                start_time,
                NULL::timestamptz AS end_time,
                name AS title
            FROM class
            WHERE trainer_id = %s
            """,
            (trainer_id,),
        )
        for row in cur.fetchall():
            items.append(TrainerScheduleItem(**row))

    items.sort(key=lambda x: x.start_time)
    return items
