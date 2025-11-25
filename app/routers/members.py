# app/routers/members.py
import os
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    MemberRegisterRequest,
    MemberResponse,
    HealthMetricCreate,
    MemberDashboard,
    PTSessionCreate,
)
import app.repositories.admins_raw as admins_repo  # class registration

USE_ORM = os.getenv("USE_ORM", "false").lower() == "true"
if USE_ORM:
    import app.repositories.members_orm as members_repo
else:
    import app.repositories.members_raw as members_repo

print("USE_ORM (members router) =", USE_ORM)
router = APIRouter(prefix="/members", tags=["members"])


@router.post("/register", response_model=MemberResponse)
def register_member(data: MemberRegisterRequest):
    try:
        member_id = members_repo.register_member(data)
        return MemberResponse(
            member_id=member_id,
            name=data.name,
            email=data.email,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{member_id}/metrics")
def add_metric(member_id: int, metric: HealthMetricCreate):
    try:
        metric_id = members_repo.add_health_metric(member_id, metric)
        return {"metric_id": metric_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{member_id}/dashboard", response_model=MemberDashboard)
def dashboard(member_id: int):
    dashboard = members_repo.get_member_dashboard(member_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Member not found")
    return dashboard


@router.post("/{member_id}/pt-sessions")
def schedule_pt_session(member_id: int, session: PTSessionCreate):
    try:
        session_id = members_repo.schedule_pt_session(member_id, session)
        return {"session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{member_id}/classes/{class_id}/register")
def register_for_class(member_id: int, class_id: int):
    """
    Register a member for a class (always uses admins_raw/admins_orm indirectly).
    """
    try:
        admins_repo.register_member_for_class(member_id, class_id)
        return {"status": "registered", "member_id": member_id, "class_id": class_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
