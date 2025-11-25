# app/repositories/auth_orm.py
from passlib.hash import bcrypt
from app.db_orm import SessionLocal
from app.models.orm_models import Member, Trainer, Admin


def _check_member(email: str, password: str):
    with SessionLocal() as session:
        user = session.query(Member).filter(Member.email == email).first()
        if not user:
            return None
        if not bcrypt.verify(password, user.password_hash):
            return None
        return user.member_id, user.email


def _check_trainer(email: str, password: str):
    with SessionLocal() as session:
        user = session.query(Trainer).filter(Trainer.email == email).first()
        if not user:
            return None
        if not bcrypt.verify(password, user.password_hash):
            return None
        return user.trainer_id, user.email


def _check_admin(email: str, password: str):
    with SessionLocal() as session:
        user = session.query(Admin).filter(Admin.email == email).first()
        if not user:
            return None
        if not bcrypt.verify(password, user.password_hash):
            return None
        return user.admin_id, user.email


def login_member(email: str, password: str):
    return _check_member(email, password)


def login_trainer(email: str, password: str):
    return _check_trainer(email, password)


def login_admin(email: str, password: str):
    return _check_admin(email, password)
