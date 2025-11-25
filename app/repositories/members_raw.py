# app/repositories/members_raw.py
from passlib.hash import bcrypt
from app.db_raw import get_cursor
from app.models.schemas import (
    MemberRegisterRequest,
    HealthMetricCreate,
    MemberDashboard,
    PTSessionCreate,
)


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


def add_health_metric(member_id: int, metric: HealthMetricCreate) -> int:
    """
    Insert a new health metric for this member and return metric_id.
    """
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO health_metric (member_id, metric_type, metric_value)
            VALUES (%s, %s, %s)
            RETURNING metric_id;
            """,
            (member_id, metric.metric_type, metric.metric_value),
        )
        row = cur.fetchone()
        return row["metric_id"]


def get_member_dashboard(member_id: int) -> MemberDashboard | None:
    """
    Read from the member_dashboard_view for this member.
    Returns None if the member doesn't exist in the view.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM member_dashboard_view
            WHERE member_id = %s;
            """,
            (member_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return MemberDashboard(**row)


def _has_time_conflict_for_trainer(trainer_id: int, start_time, end_time) -> bool:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM ptsession
            WHERE trainer_id = %s
              AND NOT (end_time <= %s OR start_time >= %s);
            """,
            (trainer_id, start_time, end_time),
        )
        row = cur.fetchone()
        return row["cnt"] > 0


def _has_time_conflict_for_room(room_id: int, start_time, end_time) -> bool:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM ptsession
            WHERE room_id = %s
              AND NOT (end_time <= %s OR start_time >= %s);
            """,
            (room_id, start_time, end_time),
        )
        row = cur.fetchone()
        return row["cnt"] > 0


def _has_time_conflict_for_member(member_id: int, start_time, end_time) -> bool:
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM ptsession
            WHERE member_id = %s
              AND NOT (end_time <= %s OR start_time >= %s);
            """,
            (member_id, start_time, end_time),
        )
        row = cur.fetchone()
        return row["cnt"] > 0


def schedule_pt_session(member_id: int, data: PTSessionCreate) -> int:
    """
    Schedule a PT session if there are no time conflicts for the member,
    trainer, or room. Returns the new session_id.
    """
    if data.end_time <= data.start_time:
        raise ValueError("end_time must be after start_time")

    # Check conflicts
    if _has_time_conflict_for_trainer(data.trainer_id, data.start_time, data.end_time):
        raise ValueError("Trainer is not available in this time slot")

    if _has_time_conflict_for_room(data.room_id, data.start_time, data.end_time):
        raise ValueError("Room is not available in this time slot")

    if _has_time_conflict_for_member(member_id, data.start_time, data.end_time):
        raise ValueError("Member already has a session in this time slot")

    # If all clear, insert
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO ptsession (member_id, trainer_id, room_id, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING session_id;
            """,
            (member_id, data.trainer_id, data.room_id, data.start_time, data.end_time),
        )
        row = cur.fetchone()
        return row["session_id"]
