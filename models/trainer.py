from database import db
from datetime import time

class Trainer(db.Model):
    __tablename__ = 'trainers'
    
    trainer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(100))
    availability_start = db.Column(db.Time)  # e.g., 09:00
    availability_end = db.Column(db.Time)    # e.g., 17:00
    
    # Relationships
    pt_sessions = db.relationship('PTSession', back_populates='trainer')
    classes = db.relationship('FitnessClass', back_populates='trainer')
    
    def __repr__(self):
        return f'<Trainer {self.name}>'