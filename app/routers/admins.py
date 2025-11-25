# app/routers/admins.py
import os
from fastapi import APIRouter, HTTPException

from app.db_raw import get_cursor
from app.models.schemas import (
    RoomCreate,
    RoomResponse,
    ClassCreate,
    ClassResponse,
    AdminRegisterRequest,
)

USE_ORM = os.getenv("USE_ORM", "false").lower() == "true"
if USE_ORM:
    import app.repositories.admins_orm as admins_repo
else:
    import app.repositories.admins_raw as admins_repo

router = APIRouter(prefix="/admins", tags=["admins"])


@router.get("/db-health")
def db_health():
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1 AS ok;")
            row = cur.fetchone()
        return {"db": "ok", "value": row["ok"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
def register_admin(data: AdminRegisterRequest):
    try:
        admin_id = admins_repo.register_admin(data)
        return {"admin_id": admin_id, "email": data.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rooms", response_model=RoomResponse)
def create_room(data: RoomCreate):
    try:
        room_id = admins_repo.create_room(data)
        return RoomResponse(room_id=room_id, name=data.name, capacity=data.capacity)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rooms", response_model=list[RoomResponse])
def list_rooms():
    return admins_repo.list_rooms()


@router.post("/classes", response_model=ClassResponse)
def create_class(data: ClassCreate):
    try:
        class_id = admins_repo.create_class(data)
        return ClassResponse(
            class_id=class_id,
            name=data.name,
            start_time=data.start_time,
            capacity=data.capacity,
            trainer_id=data.trainer_id,
            room_id=data.room_id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/classes", response_model=list[ClassResponse])
def list_classes():
    return admins_repo.list_classes()
