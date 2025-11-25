# app/routers/trainers.py
import os
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    TrainerAvailabilityCreate,
    TrainerAvailabilityResponse,
    TrainerScheduleItem,
    TrainerRegisterRequest,
)

USE_ORM = os.getenv("USE_ORM", "false").lower() == "true"
if USE_ORM:
    import app.repositories.trainers_orm as trainers_repo
else:
    import app.repositories.trainers_raw as trainers_repo

router = APIRouter(prefix="/trainers", tags=["trainers"])


@router.post("/register")
def register_trainer(data: TrainerRegisterRequest):
    try:
        trainer_id = trainers_repo.register_trainer(data)
        return {"trainer_id": trainer_id, "email": data.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{trainer_id}/availability", response_model=TrainerAvailabilityResponse)
def create_availability(trainer_id: int, data: TrainerAvailabilityCreate):
    try:
        availability_id = trainers_repo.add_availability(trainer_id, data)
        avails = trainers_repo.list_availability(trainer_id)
        for a in avails:
            if a.availability_id == availability_id:
                return a
        raise HTTPException(status_code=500, detail="Availability created but not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{trainer_id}/availability", response_model=list[TrainerAvailabilityResponse])
def list_availability(trainer_id: int):
    return trainers_repo.list_availability(trainer_id)


@router.get("/{trainer_id}/schedule", response_model=list[TrainerScheduleItem])
def trainer_schedule(trainer_id: int):
    return trainers_repo.get_trainer_schedule(trainer_id)
