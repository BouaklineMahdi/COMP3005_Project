# app/repositories/members_orm.py
from datetime import datetime

from sqlalchemy import text, or_
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from app.db_orm import SessionLocal
from app.models.orm_models import Member, HealthMetric, PTSession, ClassRegistration
from app.models.schemas import (
    MemberRegisterRequest,
    HealthMetricCreate,
    MemberDashboard,
    PTSessionCreate,
)

def register_for_class(member_id: int, class_id: int) -> None:
    """
    Register a member for a class using ORM.
    Ensures registered_at is non-null.
    """
    with SessionLocal() as session:
        reg = ClassRegistration(
            member_id=member_id,
            class_id=class_id,
            registered_at=datetime.utcnow(),  # 👈 important
        )
        session.add(reg)
        session.commit()

def register_member(data: MemberRegisterRequest) -> int:
    password_hash = bcrypt.hash(data.password)
    with SessionLocal() as session:
        member = Member(
            name=data.name,
            dob=data.dob,
            gender=data.gender,
            email=data.email,
            phone=data.phone,
            password_hash=password_hash,
        )
        session.add(member)
        session.commit()
        session.refresh(member)
        return member.member_id


def add_health_metric(member_id: int, metric: HealthMetricCreate) -> int:
    with SessionLocal() as session:
        hm = HealthMetric(
            member_id=member_id,
            metric_type=metric.metric_type,
            metric_value=metric.metric_value,
            measured_at=datetime.utcnow(),  # 👈 force non-null timestamp
        )
        session.add(hm)
        session.commit()
        session.refresh(hm)
        return hm.metric_id


def get_member_dashboard(member_id: int) -> MemberDashboard | None:
    """
    Use the existing view member_dashboard_view via text SQL.
    """
    with SessionLocal() as session:
        row = (
            session.execute(
                text(
                    """
                    SELECT *
                    FROM member_dashboard_view
                    WHERE member_id = :mid
                    """
                ),
                {"mid": member_id},
            )
            .mappings()
            .first()
        )
        if not row:
            return None
        return MemberDashboard(**row)


def _has_time_conflict(
    session: Session,
    entity,
    filter_column,
    filter_value: int,
    start_time,
    end_time,
) -> bool:
    return (
        session.query(entity)
        .filter(
            filter_column == filter_value,
            # overlapping: NOT (end <= start OR start >= end)
            ~(
                (entity.end_time <= start_time)
                | (entity.start_time >= end_time)
            ),
        )
        .count()
        > 0
    )


def schedule_pt_session(member_id: int, data: PTSessionCreate) -> int:
    if data.end_time <= data.start_time:
        raise ValueError("end_time must be after start_time")

    with SessionLocal() as session:
        # Trainer conflict
        if _has_time_conflict(
            session, PTSession, PTSession.trainer_id, data.trainer_id, data.start_time, data.end_time
        ):
            raise ValueError("Trainer is not available in this time slot")

        # Room conflict
        if _has_time_conflict(
            session, PTSession, PTSession.room_id, data.room_id, data.start_time, data.end_time
        ):
            raise ValueError("Room is not available in this time slot")

        # Member conflict
        if _has_time_conflict(
            session, PTSession, PTSession.member_id, member_id, data.start_time, data.end_time
        ):
            raise ValueError("Member already has a session in this time slot")

        pts = PTSession(
            member_id=member_id,
            trainer_id=data.trainer_id,
            room_id=data.room_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        session.add(pts)
        session.commit()
        session.refresh(pts)
        return pts.session_id
