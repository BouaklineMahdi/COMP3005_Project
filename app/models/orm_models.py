# app/models/orm_models.py
from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Member(Base):
    __tablename__ = "member"

    member_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(Text)
    email = Column(Text, nullable=False, unique=True)
    phone = Column(Text)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    health_metrics = relationship(
        "HealthMetric", back_populates="member", cascade="all, delete-orphan"
    )
    fitness_goals = relationship(
        "FitnessGoal", back_populates="member", cascade="all, delete-orphan"
    )
    pt_sessions = relationship(
        "PTSession", back_populates="member", cascade="all, delete-orphan"
    )
    class_registrations = relationship(
        "ClassRegistration", back_populates="member", cascade="all, delete-orphan"
    )


class Trainer(Base):
    __tablename__ = "trainer"

    trainer_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    specialization = Column(Text)
    password_hash = Column(Text, nullable=False)

    pt_sessions = relationship("PTSession", back_populates="trainer")
    classes = relationship("FitnessClass", back_populates="trainer")
    availabilities = relationship(
        "TrainerAvailability", back_populates="trainer", cascade="all, delete-orphan"
    )


class Admin(Base):
    __tablename__ = "admin"

    admin_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)


class Room(Base):
    __tablename__ = "room"

    room_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)

    classes = relationship("FitnessClass", back_populates="room")
    pt_sessions = relationship("PTSession", back_populates="room")


class FitnessClass(Base):
    __tablename__ = "class"

    class_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    capacity = Column(Integer, nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainer.trainer_id"), nullable=False)
    room_id = Column(Integer, ForeignKey("room.room_id"), nullable=False)

    trainer = relationship("Trainer", back_populates="classes")
    room = relationship("Room", back_populates="classes")
    registrations = relationship(
        "ClassRegistration", back_populates="fitness_class", cascade="all, delete-orphan"
    )


class PTSession(Base):
    __tablename__ = "ptsession"

    session_id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainer.trainer_id"), nullable=False)
    room_id = Column(Integer, ForeignKey("room.room_id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    member = relationship("Member", back_populates="pt_sessions")
    trainer = relationship("Trainer", back_populates="pt_sessions")
    room = relationship("Room", back_populates="pt_sessions")


class HealthMetric(Base):
    __tablename__ = "health_metric"

    metric_id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    metric_type = Column(Text, nullable=False)
    metric_value = Column(Numeric(10, 2), nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    member = relationship("Member", back_populates="health_metrics")


class FitnessGoal(Base):
    __tablename__ = "fitness_goal"

    goal_id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("member.member_id"), nullable=False)
    goal_type = Column(Text, nullable=False)
    target_value = Column(Numeric(10, 2))
    status = Column(Text, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    member = relationship("Member", back_populates="fitness_goals")


class ClassRegistration(Base):
    __tablename__ = "class_registration"

    member_id = Column(Integer, ForeignKey("member.member_id"), primary_key=True)
    class_id = Column(Integer, ForeignKey("class.class_id"), primary_key=True)
    registered_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    member = relationship("Member", back_populates="class_registrations")
    fitness_class = relationship("FitnessClass", back_populates="registrations")


class TrainerAvailability(Base):
    __tablename__ = "trainer_availability"

    availability_id = Column(Integer, primary_key=True)
    trainer_id = Column(Integer, ForeignKey("trainer.trainer_id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    trainer = relationship("Trainer", back_populates="availabilities")
