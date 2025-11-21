# app/models/schemas.py
from datetime import date
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
