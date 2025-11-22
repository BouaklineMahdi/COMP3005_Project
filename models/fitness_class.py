from database import db
from datetime import datetime

class FitnessClass(db.Model):
    __tablename__ = 'classes'
    
    class_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.trainer_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    
    # Relationships
    trainer = db.relationship('Trainer', back_populates='classes')
    room = db.relationship('Room', back_populates='classes')
    registrations = db.relationship('ClassRegistration', back_populates='fitness_class', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FitnessClass {self.name}>'


# Many-to-Many relationship table (not an entity)
class ClassRegistration(db.Model):
    __tablename__ = 'class_registrations'
    
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), primary_key=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    member = db.relationship('Member', back_populates='class_registrations')
    fitness_class = db.relationship('FitnessClass', back_populates='registrations')