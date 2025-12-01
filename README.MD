# Health & Fitness Club Management System

**COMP 3005 - Fall 2025**  
**Team Members:** Mahdi Bouakline 101257788, Aranan

---

## Overview

Database-driven fitness club management system supporting three user roles: Members, Trainers, and Administrative Staff.

**Technology Stack:**
- Python FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Bcrypt authentication

---

## ORM Implementation

**Why No DDL.sql/DML.sql:**  
Per assignment guidelines, ORM-based projects use programmatic schema definition instead of SQL files.

**Our Approach:**
- Tables created via `Base.metadata.create_all()` in `app/db_orm.py`
- Entity classes in `app/models/orm_models.py` define schema
- Sample data inserted via `init_db.py` using ORM sessions
- All operations use SQLAlchemy (no raw SQL except VIEW query)

**Key Features:**
- 10 entity classes with proper relationships
- Operations configured
- Foreign keys handled
- Repository pattern for database access

---

## Web Interface

Navigate to `http://127.0.0.1:8000/` for role-based dashboards.

**Features:**
- Home page with role selection
- Secure login for each role
- Member dashboard (VIEW data, add metrics, schedule sessions, etc...)
- Trainer dashboard (view schedule, set availability, etc...)
- Admin dashboard (create rooms/classes, view all classes, etc...)

---

## API Documentation

Interactive API docs: http://127.0.0.1:8000/docs

This UI allows the user to test all operations.

---

## Demo Video

https://youtu.be/EIcz4V0cz1s

**Contents:**
- ER diagram and design assumptions
- Entity class definitions and ORM mapping
- Database initialization walkthrough
- Most operations demonstrated
- VIEW, TRIGGER, INDEX in action
- Code organization overview

---

## Notes

- All passwords hashed with bcrypt
- Historical health metrics (never overwritten)
- Time conflict validation for PT sessions
- Class capacity enforced by database trigger
- Full 3NF normalization