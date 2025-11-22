from database import db

class Room(db.Model):
    __tablename__ = 'rooms'
    
    room_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    classes = db.relationship('FitnessClass', back_populates='room')
    pt_sessions = db.relationship('PTSession', back_populates='room')
    
    def __repr__(self):
        return f'<Room {self.name}>'