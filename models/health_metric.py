from database import db
from datetime import datetime

class HealthMetric(db.Model):
    __tablename__ = 'health_metrics'
    
    metric_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # weight, heart_rate, blood_pressure, etc.
    metric_value = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    member = db.relationship('Member', back_populates='health_metrics')
    
    def __repr__(self):
        return f'<HealthMetric {self.metric_type}: {self.metric_value}>'