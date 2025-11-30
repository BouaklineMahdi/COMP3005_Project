# app/routers/auth.py
import os
from fastapi import APIRouter, HTTPException

from app.models.schemas import LoginRequest, LoginResponse

USE_ORM = os.getenv("USE_ORM", "false").lower() == "true"
if USE_ORM:
    import app.repositories.auth_orm as auth_repo
else:
    import app.repositories.auth_raw as auth_repo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/member-login", response_model=LoginResponse)
def member_login(data: LoginRequest):
    result = auth_repo.login_member(data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id, email = result
    return LoginResponse(role="member", user_id=user_id, email=email)


@router.post("/trainer-login", response_model=LoginResponse)
def trainer_login(data: LoginRequest):
    result = auth_repo.login_trainer(data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id, email = result
    return LoginResponse(role="trainer", user_id=user_id, email=email)


@router.post("/admin-login", response_model=LoginResponse)
def admin_login(data: LoginRequest):
    result = auth_repo.login_admin(data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id, email = result
    # include email so it satisfies LoginResponse
    return LoginResponse(role="admin", user_id=user_id, email=email)
