# Health & Fitness Club Management System

**COMP 3005 - Fall 2025 - Database Project**  
**Team of 2 - Full ORM Implementation (SQLAlchemy)**

---

## Project Overview

This is a complete database-driven Health & Fitness Club Management System built with:
- **Backend**: Python FastAPI
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Bcrypt password hashing

The system supports three user roles (Members, Trainers, Admins) with 10 distinct operations, including user registration, health tracking, PT session scheduling, class management, and more.

### Why We Don't Have DDL.sql and DML.sql

According to the assignment:
> "For ORM-based submissions, DDL.sql and DML.sql files are **not required**. Instead, the ORM code must clearly demonstrate how the database schema is defined and populated programmatically."

**Our approach:**
-  **Table creation**: `app/db_orm.py` + `app/models/orm_models.py` (using SQLAlchemy `Base.metadata.create_all()`)
-  **Sample data**: `init_db.py` script (programmatically inserts data via ORM)
-  **All operations**: Use ORM sessions (no raw SQL)

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- pip (Python package manager)

### Step 1: Clone the Repository
git clone 
cd COMP3005_Project

### Step 2: Create PostgreSQL Database
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fitness_club;

# Exit
\q

### Step 3: Configure Environment Variables
Create a `.env` file in the project root:

DB_HOST=localhost
DB_PORT=5432
DB_NAME=fitness_club
DB_USER=postgres
DB_PASSWORD=your_password_here

**Replace `your_password_here` with your actual PostgreSQL password!**

### Step 4: Install Python Dependencies
pip install -r requirements.txt

**Dependencies installed:**
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `sqlalchemy==2.0.23` - ORM framework
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `passlib[bcrypt]==1.7.4` - Password hashing
- `pydantic==2.5.0` - Data validation
- `python-dotenv==1.0.0` - Environment variable management

### Step 5: Initialize Database (ORM Method)
python init_db.py

**This script will:**
1. Drop existing tables (if any)
2. Create all tables from ORM models
3. Populate database with sample data
4. Display test credentials

### Step 6: Run the Application
uvicorn app.main:app --reload

**Server will start at:** http://127.0.0.1:8000

---

## Database Schema

### Entities (8 Required for Team of 2)

1. **Member** - Gym member accounts with personal information
2. **Trainer** - Fitness trainers with specializations
3. **Admin** - Administrative staff accounts
4. **Room** - Physical spaces for classes and PT sessions
5. **FitnessClass** (`class` table) - Group fitness classes
6. **PTSession** - One-on-one personal training sessions
7. **HealthMetric** - Historical health data for members
8. **FitnessGoal** - Member fitness goals and targets

### Relationships (8 Required for Team of 2)

1. Member → HealthMetric (1:N)
2. Member → FitnessGoal (1:N)
3. Member → PTSession (1:N)
4. Member ↔ FitnessClass (M:N via `ClassRegistration`)
5. Trainer → PTSession (1:N)
6. Trainer → FitnessClass (1:N)
7. Trainer → TrainerAvailability (1:N)
8. Room → FitnessClass (1:N)
9. Room → PTSession (1:N)

---

##  Implemented Operations (10 Total)

### Member Operations (4 required, 5 implemented)
1.  **User Registration** - `POST /members/register`
2.  **Profile Management** - Included in registration (update can be added)
3.  **Health History Logging** - `POST /members/{id}/health-metrics`
4.  **PT Session Scheduling** - `POST /members/{id}/pt-sessions`
5.  **Member Dashboard** - `GET /members/{id}/dashboard`

### Trainer Operations (2 required, 2 implemented)
6.  **Set Availability** - `POST /trainers/{id}/availability`
7.  **Schedule View** - `GET /trainers/{id}/schedule`

### Admin Operations (2 required, 2 implemented)
8.  **Room Booking** - `POST /admins/rooms`
9.  **Class Management** - `POST /admins/classes`

### Additional Operations (2 required for 10 total)
10.  **Group Class Registration** - `POST /members/{member_id}/classes/{class_id}/register`

---

## ORM Bonus Implementation (10%)

### Qualification Criteria Met

**Complete ORM Usage**
- All database operations use SQLAlchemy ORM
- No raw SQL in business logic (except for view queries via `text()`)
- Entity classes fully replace DDL statements

**Entity Class Mapping**
- 8 entity classes in `app/models/orm_models.py`
- All relationships defined using `relationship()` and `ForeignKey()`
- Example:
  ```python
  class Member(Base):
      __tablename__ = "member"
      member_id = Column(Integer, primary_key=True)
      health_metrics = relationship('HealthMetric', back_populates='member')
  ```

**Relationship Handling**
- One-to-Many: `Member.health_metrics`, `Trainer.pt_sessions`
- Many-to-Many: `ClassRegistration` as association table
- Cascade deletes configured: `cascade="all, delete-orphan"`

**Code Organization**
- Clear separation: models, repositories, routers
- Repository pattern abstracts database access
- Pydantic schemas for request/response validation

---

## Demo Video

**Video Link:** [Insert YouTube/Vimeo link here]

**Video covers:**
- ER diagram explanation (entities, relationships, cardinality)
- ER to relational mapping (how entities become tables)
- ORM entity class walkthrough
- Database initialization using ORM
- All 10 operations demonstrated (success + failure cases)
- View, trigger, and index in action
- Code structure and organization

---

## Project Team

- **Team Member 1:** Mahdi Bouakline 101257788
- **Team Member 2:** Aranan

**Course:** COMP 3005 - Database Management Systems  
**Instructor:** Abdelghny Orogat  
**Semester:** Fall 2025

---