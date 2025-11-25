# app/models/schemas.py
from datetime import date, datetime
from pydantic import BaseModel, EmailStr

# ===== Member schemas =====

class MemberRegisterRequest(BaseModel):
    name: str
    dob: date          # YYYY-MM-DD
    gender: str | None = None
    email: EmailStr
    phone: str | None = None
    password: str      # plain text from client, will be hashed


class MemberResponse(BaseModel):
    member_id: int
    name: str
    email: EmailStr


# ===== Trainer & Admin registration =====

class TrainerRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    specialization: str | None = None
    password: str


class AdminRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


# ===== Auth / Login =====

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    role: str        # "member" | "trainer" | "admin"
    user_id: int
    email: EmailStr


# ===== Health metrics & dashboard =====

class HealthMetricCreate(BaseModel):
    metric_type: str     # e.g., "weight", "heart_rate"
    metric_value: float  # health_metric.metric_value is NUMERIC(10,2)


class MemberDashboard(BaseModel):
    member_id: int
    name: str
    email: EmailStr
    latest_metric_value: float | None = None
    latest_metric_type: str | None = None
    total_classes_registered: int
    upcoming_pt_sessions: int


# ===== PT Sessions (member side) =====

class PTSessionCreate(BaseModel):
    trainer_id: int
    room_id: int
    start_time: datetime   # e.g., "2025-12-01T10:00:00"
    end_time: datetime


class PTSessionResponse(BaseModel):
    session_id: int
    member_id: int
    trainer_id: int
    room_id: int
    start_time: datetime
    end_time: datetime


# ===== Trainer availability & schedule =====

class TrainerAvailabilityCreate(BaseModel):
    start_time: datetime
    end_time: datetime


class TrainerAvailabilityResponse(BaseModel):
    availability_id: int
    trainer_id: int
    start_time: datetime
    end_time: datetime


class TrainerScheduleItem(BaseModel):
    item_type: str        # "pt_session" or "class"
    start_time: datetime
    end_time: datetime | None = None
    title: str


# ===== Rooms & Classes (admin side) =====

class RoomCreate(BaseModel):
    name: str
    capacity: int


class RoomResponse(BaseModel):
    room_id: int
    name: str
    capacity: int


class ClassCreate(BaseModel):
    name: str
    start_time: datetime
    capacity: int
    trainer_id: int
    room_id: int


class ClassResponse(BaseModel):
    class_id: int
    name: str
    start_time: datetime
    capacity: int
    trainer_id: int
    room_id: int
