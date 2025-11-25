# app/repositories/admins_orm.py
from passlib.hash import bcrypt
from app.db_orm import SessionLocal
from app.models.orm_models import Admin, Room, FitnessClass, ClassRegistration
from app.models.schemas import (
    RoomCreate,
    RoomResponse,
    ClassCreate,
    ClassResponse,
    AdminRegisterRequest,
)


def register_admin(data: AdminRegisterRequest) -> int:
    password_hash = bcrypt.hash(data.password)
    with SessionLocal() as session:
        admin = Admin(
            name=data.name,
            email=data.email,
            password_hash=password_hash,
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return admin.admin_id


def create_room(data: RoomCreate) -> int:
    with SessionLocal() as session:
        room = Room(name=data.name, capacity=data.capacity)
        session.add(room)
        session.commit()
        session.refresh(room)
        return room.room_id


def list_rooms() -> list[RoomResponse]:
    with SessionLocal() as session:
        rooms = session.query(Room).order_by(Room.room_id).all()
        return [
            RoomResponse(room_id=r.room_id, name=r.name, capacity=r.capacity)
            for r in rooms
        ]


def create_class(data: ClassCreate) -> int:
    with SessionLocal() as session:
        cls = FitnessClass(
            name=data.name,
            start_time=data.start_time,
            capacity=data.capacity,
            trainer_id=data.trainer_id,
            room_id=data.room_id,
        )
        session.add(cls)
        session.commit()
        session.refresh(cls)
        return cls.class_id


def list_classes() -> list[ClassResponse]:
    with SessionLocal() as session:
        classes = session.query(FitnessClass).order_by(FitnessClass.class_id).all()
        return [
            ClassResponse(
                class_id=c.class_id,
                name=c.name,
                start_time=c.start_time,
                capacity=c.capacity,
                trainer_id=c.trainer_id,
                room_id=c.room_id,
            )
            for c in classes
        ]


def register_member_for_class(member_id: int, class_id: int) -> None:
    with SessionLocal() as session:
        reg = ClassRegistration(member_id=member_id, class_id=class_id)
        session.add(reg)
        # trigger will fire in DB and raise if full
        session.commit()
