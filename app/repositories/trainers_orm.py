# app/repositories/trainers_orm.py
from passlib.hash import bcrypt
from app.db_orm import SessionLocal
from app.models.orm_models import Trainer, TrainerAvailability, PTSession, FitnessClass
from app.models.schemas import (
    TrainerAvailabilityCreate,
    TrainerAvailabilityResponse,
    TrainerScheduleItem,
    TrainerRegisterRequest,
)


def register_trainer(data: TrainerRegisterRequest) -> int:
    password_hash = bcrypt.hash(data.password)
    with SessionLocal() as session:
        trainer = Trainer(
            name=data.name,
            email=data.email,
            specialization=data.specialization,
            password_hash=password_hash,
        )
        session.add(trainer)
        session.commit()
        session.refresh(trainer)
        return trainer.trainer_id


def add_availability(trainer_id: int, data: TrainerAvailabilityCreate) -> int:
    if data.end_time <= data.start_time:
        raise ValueError("end_time must be after start_time")

    with SessionLocal() as session:
        av = TrainerAvailability(
            trainer_id=trainer_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        session.add(av)
        session.commit()
        session.refresh(av)
        return av.availability_id


def list_availability(trainer_id: int) -> list[TrainerAvailabilityResponse]:
    with SessionLocal() as session:
        avs = (
            session.query(TrainerAvailability)
            .filter(TrainerAvailability.trainer_id == trainer_id)
            .order_by(TrainerAvailability.start_time)
            .all()
        )
        return [
            TrainerAvailabilityResponse(
                availability_id=a.availability_id,
                trainer_id=a.trainer_id,
                start_time=a.start_time,
                end_time=a.end_time,
            )
            for a in avs
        ]


def get_trainer_schedule(trainer_id: int) -> list[TrainerScheduleItem]:
    items: list[TrainerScheduleItem] = []
    with SessionLocal() as session:
        # PT sessions
        sessions = (
            session.query(PTSession)
            .filter(PTSession.trainer_id == trainer_id)
            .all()
        )
        for s in sessions:
            items.append(
                TrainerScheduleItem(
                    item_type="pt_session",
                    start_time=s.start_time,
                    end_time=s.end_time,
                    title=f"PT session with member {s.member_id}",
                )
            )

        # Classes
        classes = (
            session.query(FitnessClass)
            .filter(FitnessClass.trainer_id == trainer_id)
            .all()
        )
        for c in classes:
            items.append(
                TrainerScheduleItem(
                    item_type="class",
                    start_time=c.start_time,
                    end_time=None,
                    title=c.name,
                )
            )

    items.sort(key=lambda x: x.start_time)
    return items
