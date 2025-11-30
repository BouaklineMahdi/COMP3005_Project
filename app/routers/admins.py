# app/routers/admins.py
"""
Admin-facing API endpoints.

Routes implemented:
- GET  /admins/db-health          -> basic DB health check
- POST /admins/register           -> create new admin
- GET  /admins/rooms              -> list rooms
- POST /admins/rooms              -> create room
- GET  /admins/classes            -> list classes
- POST /admins/classes            -> create class
"""

import os
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AdminRegisterRequest,
    RoomCreate,
    RoomResponse,
    ClassCreate,
    ClassResponse,
)

# Choose raw SQL or ORM repository implementation
USE_ORM = os.getenv("USE_ORM", "false").lower() == "true"
if USE_ORM:
    import app.repositories.admins_orm as admins_repo  # type: ignore
else:
    import app.repositories.admins_raw as admins_repo

router = APIRouter(prefix="/admins", tags=["admins"])


# ---------------------------------------------------------
# DB health
# ---------------------------------------------------------

@router.get("/db-health")
def db_health():
    """
    Simple DB health check: SELECT 1.
    """
    try:
        return admins_repo.get_db_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# Admin registration
# ---------------------------------------------------------

@router.post("/register")
def register_admin(data: AdminRegisterRequest):
    """
    Create a new admin user.

    Returns a simple dict instead of a Pydantic response model
    to avoid depending on AdminResponse.
    """
    try:
        admin_id = admins_repo.register_admin(data)
        return {
            "admin_id": admin_id,
            "name": data.name,
            "email": data.email,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------
# Rooms
# ---------------------------------------------------------

@router.get("/rooms", response_model=list[RoomResponse])
def list_rooms():
    """
    List all rooms.
    """
    try:
        return admins_repo.list_rooms()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rooms", response_model=RoomResponse)
def create_room(data: RoomCreate):
    """
    Create a new room.
    """
    try:
        return admins_repo.create_room(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------
# Classes
# ---------------------------------------------------------

@router.get("/classes", response_model=list[ClassResponse])
def list_classes():
    """
    List all fitness classes.
    """
    try:
        return admins_repo.list_classes()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/classes", response_model=ClassResponse)
def create_class(data: ClassCreate):
    """
    Create a new fitness class.
    """
    try:
        return admins_repo.create_class(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
