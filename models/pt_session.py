from database import db
from datetime import datetime

class PTSession(db.Model):
    __tablename__ = 'pt_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.trainer_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    
    # Relationships
    member = db.relationship('Member', back_populates='pt_sessions')
    trainer = db.relationship('Trainer', back_populates='pt_sessions')
    room = db.relationship('Room', back_populates='pt_sessions')
    
    def __repr__(self):
        return f'<PTSession {self.session_id}>'