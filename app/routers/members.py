# app/routers/members.py
from fastapi import APIRouter, HTTPException

from app.models.schemas import MemberRegisterRequest, MemberResponse
from app.repositories import members_raw  # later we'll alias raw/orm based on USE_ORM

router = APIRouter(prefix="/members", tags=["members"])

@router.post("/register", response_model=MemberResponse)
def register_member(data: MemberRegisterRequest):
    try:
        member_id = members_raw.register_member(data)
        return MemberResponse(
            member_id=member_id,
            name=data.name,
            email=data.email,
        )
    except Exception as e:
        # could be unique email violation, etc.
        raise HTTPException(status_code=400, detail=str(e))
