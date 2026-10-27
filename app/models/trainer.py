"""Trainer model – personal trainers linked to user accounts."""

from app.extensions import db


class Trainer(db.Model):
    __tablename__ = 'trainers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)

    # Relationships
    workout_plans = db.relationship('WorkoutPlan', backref='trainer', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Trainer {self.full_name}>'
