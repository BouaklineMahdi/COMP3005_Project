from database import db
from datetime import datetime

class Member(db.Model):
    __tablename__ = 'members'
    
    member_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(255), nullable=False)  # For login
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    health_metrics = db.relationship('HealthMetric', back_populates='member', cascade='all, delete-orphan')
    fitness_goals = db.relationship('FitnessGoal', back_populates='member', cascade='all, delete-orphan')
    pt_sessions = db.relationship('PTSession', back_populates='member', cascade='all, delete-orphan')
    class_registrations = db.relationship('ClassRegistration', back_populates='member', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Member {self.name}>'