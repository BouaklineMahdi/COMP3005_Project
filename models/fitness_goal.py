from database import db

class FitnessGoal(db.Model):
    __tablename__ = 'fitness_goals'
    
    goal_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    goal_type = db.Column(db.String(100), nullable=False)  # lose_weight, build_muscle, improve_cardio, etc.
    target_value = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    
    # Relationships
    member = db.relationship('Member', back_populates='fitness_goals')
    
    def __repr__(self):
        return f'<FitnessGoal {self.goal_type}>'