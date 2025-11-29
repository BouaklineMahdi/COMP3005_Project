"""
app/init_db.py - Initialize database using SQLAlchemy ORM

This script:
1. Drops and recreates all tables from ORM models
2. Creates VIEW, TRIGGER, and INDEXES
3. Populates the database with sample data

Usage (from project root):
    python -m app.init_db
"""

from datetime import datetime, timedelta, date

from passlib.hash import bcrypt
from sqlalchemy import text
from app.db_orm import engine, SessionLocal
from app.models.orm_models import (
    Base,
    Member,
    Trainer,
    Admin,
    Room,
    FitnessClass,
    PTSession,
    HealthMetric,
    FitnessGoal,
    ClassRegistration,
    TrainerAvailability,
)


# ---------------------------------------------------------------------------
# DB objects: VIEW, TRIGGER, INDEXES
# ---------------------------------------------------------------------------

def create_view_trigger_indexes(session):
    """Create member_dashboard_view, capacity trigger, and indexes."""

    # 1. VIEW: member_dashboard_view
    print("Creating VIEW: member_dashboard_view...")
    session.execute(
        text(
            """
        CREATE OR REPLACE VIEW member_dashboard_view AS
        SELECT
            m.member_id,
            m.name,
            m.email,
            (
                SELECT hm.metric_value
                FROM health_metric hm
                WHERE hm.member_id = m.member_id
                ORDER BY hm.measured_at DESC
                LIMIT 1
            ) AS latest_metric_value,
            (
                SELECT hm.metric_type
                FROM health_metric hm
                WHERE hm.member_id = m.member_id
                ORDER BY hm.measured_at DESC
                LIMIT 1
            ) AS latest_metric_type,
            (
                SELECT COUNT(*)
                FROM class_registration cr
                WHERE cr.member_id = m.member_id
            ) AS total_classes_registered,
            (
                SELECT COUNT(*)
                FROM ptsession s
                WHERE s.member_id = m.member_id
                  AND s.start_time > NOW()
            ) AS upcoming_pt_sessions
        FROM member m;
        """
        )
    )

    # 2. FUNCTION: check_class_capacity()
    print("Creating TRIGGER FUNCTION: check_class_capacity()...")
    session.execute(
        text(
            """
        CREATE OR REPLACE FUNCTION check_class_capacity()
        RETURNS TRIGGER AS $$
        DECLARE
            current_count INTEGER;
            max_capacity  INTEGER;
        BEGIN
            SELECT COUNT(*)
            INTO current_count
            FROM class_registration
            WHERE class_id = NEW.class_id;

            SELECT capacity
            INTO max_capacity
            FROM class
            WHERE class_id = NEW.class_id;

            IF max_capacity IS NULL THEN
                RAISE EXCEPTION 'Class % does not exist', NEW.class_id;
            END IF;

            IF current_count >= max_capacity THEN
                RAISE EXCEPTION 'Class % is full (capacity: %)', NEW.class_id, max_capacity;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        )
    )

    # 3. TRIGGER: trg_class_capacity
    print("Creating TRIGGER: trg_class_capacity...")
    session.execute(
        text(
            """
        DROP TRIGGER IF EXISTS trg_class_capacity ON class_registration;

        CREATE TRIGGER trg_class_capacity
        BEFORE INSERT ON class_registration
        FOR EACH ROW
        EXECUTE FUNCTION check_class_capacity();
        """
        )
    )

    # 4. INDEXES (match our ddl.sql intent)
    print("Creating INDEXES...")

    session.execute(
        text(
            """
        CREATE INDEX IF NOT EXISTS idx_class_registration_class_id
        ON class_registration(class_id);
        """
        )
    )

    session.execute(
        text(
            """
        CREATE INDEX IF NOT EXISTS idx_ptsession_trainer_start
        ON ptsession(trainer_id, start_time);
        """
        )
    )

    session.execute(
        text(
            """
        CREATE INDEX IF NOT EXISTS idx_health_metric_member_time
        ON health_metric(member_id, measured_at DESC);
        """
        )
    )

    session.commit()
    print("VIEW, TRIGGER, and INDEXES created successfully!\n")


# ---------------------------------------------------------------------------
# Sample data seeding
# ---------------------------------------------------------------------------

def seed_database():
    """Drop all tables, recreate them from ORM, and populate with sample data."""

    print("=" * 60)
    print("Dropping existing tables...")

    # First drop the view that depends on tables, if it exists
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS member_dashboard_view CASCADE;"))
        conn.commit()

    # Now it's safe to drop all tables
    Base.metadata.drop_all(bind=engine)

    print("Creating tables from ORM models...")
    Base.metadata.create_all(bind=engine)
    ...

    print("Tables created successfully!\n")

    db = SessionLocal()
    try:
        # Create view, trigger, indexes
        create_view_trigger_indexes(db)

        # All test accounts share this password:
        #   password: "password123"
        password_hash = bcrypt.hash("password123")

        now = datetime.now()

        print("Populating sample data...")

        # 1. Admins
        admins = [
            Admin(
                name="John Admin",
                email="admin@gym.com",
                password_hash=password_hash,
            ),
            Admin(
                name="Sarah Manager",
                email="sarah.manager@gym.com",
                password_hash=password_hash,
            ),
        ]
        db.add_all(admins)
        db.flush()
        print(f"  Added {len(admins)} admins")

        # 2. Rooms
        rooms = [
            Room(name="Studio A", capacity=20),
            Room(name="Studio B", capacity=15),
            Room(name="Yoga Room", capacity=25),
            Room(name="Spin Studio", capacity=30),
            Room(name="Private Room 1", capacity=2),
            Room(name="Private Room 2", capacity=2),
            Room(name="Private Room 3", capacity=2),
        ]
        db.add_all(rooms)
        db.flush()
        print(f"  Added {len(rooms)} rooms")

        # 3. Trainers
        trainers = [
            Trainer(
                name="Sarah Fit",
                email="sarah@gym.com",
                specialization="Strength Training",
                password_hash=password_hash,
            ),
            Trainer(
                name="Mike Power",
                email="mike@gym.com",
                specialization="Cardio & HIIT",
                password_hash=password_hash,
            ),
            Trainer(
                name="Emma Zen",
                email="emma@gym.com",
                specialization="Yoga & Pilates",
                password_hash=password_hash,
            ),
            Trainer(
                name="Chris Beast",
                email="chris@gym.com",
                specialization="CrossFit",
                password_hash=password_hash,
            ),
        ]
        db.add_all(trainers)
        db.flush()
        print(f"  Added {len(trainers)} trainers")

        # 4. Members
        members = [
            Member(
                name="Alice Johnson",
                dob=date(1990, 5, 15),
                gender="Female",
                email="alice@email.com",
                phone="123-456-7890",
                password_hash=password_hash,
            ),
            Member(
                name="Bob Smith",
                dob=date(1985, 8, 20),
                gender="Male",
                email="bob@email.com",
                phone="123-456-7891",
                password_hash=password_hash,
            ),
            Member(
                name="Carol White",
                dob=date(1995, 3, 10),
                gender="Female",
                email="carol@email.com",
                phone="123-456-7892",
                password_hash=password_hash,
            ),
            Member(
                name="David Lee",
                dob=date(1988, 11, 5),
                gender="Male",
                email="david@email.com",
                phone="123-456-7893",
                password_hash=password_hash,
            ),
            Member(
                name="Emily Brown",
                dob=date(1992, 7, 22),
                gender="Female",
                email="emily@email.com",
                phone="123-456-7894",
                password_hash=password_hash,
            ),
        ]
        db.add_all(members)
        db.flush()
        print(f"  Added {len(members)} members")

        # 5. Health Metrics
        health_metrics = [
            # Alice
            HealthMetric(
                member_id=members[0].member_id,
                metric_type="weight",
                metric_value=150.0,
                measured_at=now - timedelta(days=30),
            ),
            HealthMetric(
                member_id=members[0].member_id,
                metric_type="weight",
                metric_value=148.5,
                measured_at=now - timedelta(days=15),
            ),
            HealthMetric(
                member_id=members[0].member_id,
                metric_type="weight",
                metric_value=147.0,
                measured_at=now,
            ),
            HealthMetric(
                member_id=members[0].member_id,
                metric_type="heart_rate",
                metric_value=72.0,
                measured_at=now - timedelta(days=7),
            ),
            HealthMetric(
                member_id=members[0].member_id,
                metric_type="heart_rate",
                metric_value=68.0,
                measured_at=now,
            ),
            # Bob
            HealthMetric(
                member_id=members[1].member_id,
                metric_type="weight",
                metric_value=180.0,
                measured_at=now - timedelta(days=20),
            ),
            HealthMetric(
                member_id=members[1].member_id,
                metric_type="weight",
                metric_value=182.0,
                measured_at=now,
            ),
            HealthMetric(
                member_id=members[1].member_id,
                metric_type="heart_rate",
                metric_value=75.0,
                measured_at=now,
            ),
            # Carol
            HealthMetric(
                member_id=members[2].member_id,
                metric_type="weight",
                metric_value=130.0,
                measured_at=now,
            ),
            HealthMetric(
                member_id=members[2].member_id,
                metric_type="heart_rate",
                metric_value=65.0,
                measured_at=now,
            ),
            # David
            HealthMetric(
                member_id=members[3].member_id,
                metric_type="weight",
                metric_value=175.0,
                measured_at=now - timedelta(days=10),
            ),
            HealthMetric(
                member_id=members[3].member_id,
                metric_type="weight",
                metric_value=174.0,
                measured_at=now,
            ),
        ]
        db.add_all(health_metrics)
        print(f"  Added {len(health_metrics)} health metrics")

        # 6. Fitness Goals
        goals = [
            FitnessGoal(
                member_id=members[0].member_id,
                goal_type="lose_weight",
                target_value=140.0,
                status="active",
            ),
            FitnessGoal(
                member_id=members[0].member_id,
                goal_type="improve_cardio",
                target_value=60.0,
                status="active",
            ),
            FitnessGoal(
                member_id=members[1].member_id,
                goal_type="build_muscle",
                target_value=190.0,
                status="active",
            ),
            FitnessGoal(
                member_id=members[2].member_id,
                goal_type="improve_flexibility",
                status="active",
            ),
            FitnessGoal(
                member_id=members[3].member_id,
                goal_type="lose_weight",
                target_value=165.0,
                status="active",
            ),
            FitnessGoal(
                member_id=members[4].member_id,
                goal_type="build_muscle",
                status="active",
            ),
        ]
        db.add_all(goals)
        print(f"  Added {len(goals)} fitness goals")

        # 7. Trainer Availability
        availabilities = [
            TrainerAvailability(
                trainer_id=trainers[0].trainer_id,
                start_time=now + timedelta(days=1, hours=9),
                end_time=now + timedelta(days=1, hours=12),
            ),
            TrainerAvailability(
                trainer_id=trainers[0].trainer_id,
                start_time=now + timedelta(days=1, hours=14),
                end_time=now + timedelta(days=1, hours=17),
            ),
            TrainerAvailability(
                trainer_id=trainers[1].trainer_id,
                start_time=now + timedelta(days=1, hours=10),
                end_time=now + timedelta(days=1, hours=18),
            ),
            TrainerAvailability(
                trainer_id=trainers[2].trainer_id,
                start_time=now + timedelta(days=1, hours=8),
                end_time=now + timedelta(days=1, hours=16),
            ),
        ]
        db.add_all(availabilities)
        print(f"  Added {len(availabilities)} trainer availability slots")

        # 8. Fitness Classes
        classes = [
            FitnessClass(
                name="Morning Yoga",
                start_time=now + timedelta(days=1, hours=8),
                capacity=20,
                trainer_id=trainers[2].trainer_id,
                room_id=rooms[2].room_id,
            ),
            FitnessClass(
                name="HIIT Blast",
                start_time=now + timedelta(days=1, hours=17),
                capacity=15,
                trainer_id=trainers[1].trainer_id,
                room_id=rooms[1].room_id,
            ),
            FitnessClass(
                name="Strength Training 101",
                start_time=now + timedelta(days=2, hours=10),
                capacity=12,
                trainer_id=trainers[0].trainer_id,
                room_id=rooms[0].room_id,
            ),
            FitnessClass(
                name="Spin Class",
                start_time=now + timedelta(days=2, hours=18),
                capacity=25,
                trainer_id=trainers[1].trainer_id,
                room_id=rooms[3].room_id,
            ),
            FitnessClass(
                name="Power Yoga",
                start_time=now + timedelta(days=3, hours=9),
                capacity=18,
                trainer_id=trainers[2].trainer_id,
                room_id=rooms[2].room_id,
            ),
        ]
        db.add_all(classes)
        db.flush()
        print(f"  Added {len(classes)} fitness classes")

        # 9. Class Registrations
        registrations = [
            ClassRegistration(member_id=members[0].member_id, class_id=classes[0].class_id),
            ClassRegistration(member_id=members[0].member_id, class_id=classes[1].class_id),
            ClassRegistration(member_id=members[1].member_id, class_id=classes[1].class_id),
            ClassRegistration(member_id=members[1].member_id, class_id=classes[2].class_id),
            ClassRegistration(member_id=members[2].member_id, class_id=classes[0].class_id),
            ClassRegistration(member_id=members[2].member_id, class_id=classes[4].class_id),
            ClassRegistration(member_id=members[3].member_id, class_id=classes[2].class_id),
            ClassRegistration(member_id=members[4].member_id, class_id=classes[1].class_id),
        ]
        db.add_all(registrations)
        print(f"  Added {len(registrations)} class registrations")

        # 10. PT Sessions
        pt_sessions = [
            PTSession(
                member_id=members[0].member_id,
                trainer_id=trainers[0].trainer_id,
                room_id=rooms[4].room_id,
                start_time=now + timedelta(days=1, hours=14),
                end_time=now + timedelta(days=1, hours=15),
            ),
            PTSession(
                member_id=members[1].member_id,
                trainer_id=trainers[1].trainer_id,
                room_id=rooms[5].room_id,
                start_time=now + timedelta(days=2, hours=11),
                end_time=now + timedelta(days=2, hours=12),
            ),
            PTSession(
                member_id=members[2].member_id,
                trainer_id=trainers[2].trainer_id,
                room_id=rooms[4].room_id,
                start_time=now + timedelta(days=2, hours=9),
                end_time=now + timedelta(days=2, hours=10),
            ),
            PTSession(
                member_id=members[3].member_id,
                trainer_id=trainers[0].trainer_id,
                room_id=rooms[6].room_id,
                start_time=now + timedelta(days=2, hours=15),
                end_time=now + timedelta(days=2, hours=16),
            ),
        ]
        db.add_all(pt_sessions)
        print(f"  Added {len(pt_sessions)} PT sessions")

        db.commit()

        print("\n" + "=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        print("\nTest credentials (all use password: password123):")
        print("  Admins:   admin@gym.com, sarah.manager@gym.com")
        print("  Trainers: sarah@gym.com, mike@gym.com, emma@gym.com, chris@gym.com")
        print(
            "  Members:  alice@email.com, bob@email.com, "
            "carol@email.com, david@email.com, emily@email.com"
        )
        print("\nDatabase objects created:")
        print(f"  - {len(admins)} admins")
        print(f"  - {len(rooms)} rooms")
        print(f"  - {len(trainers)} trainers")
        print(f"  - {len(members)} members")
        print(f"  - {len(health_metrics)} health metrics")
        print(f"  - {len(goals)} fitness goals")
        print(f"  - {len(availabilities)} trainer availability slots")
        print(f"  - {len(classes)} fitness classes")
        print(f"  - {len(registrations)} class registrations")
        print(f"  - {len(pt_sessions)} PT sessions")
        print("  - 1 view (member_dashboard_view)")
        print("  - 1 trigger (trg_class_capacity)")
        print("  - 3 indexes "
              "(idx_class_registration_class_id, "
              "idx_ptsession_trainer_start, "
              "idx_health_metric_member_time)")
        print("=" * 60)

    except Exception as e:
        print(f"\nError seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
