"""Member model – gym member personal information."""

from app.extensions import db
from datetime import datetime, timezone


class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Nullable: walk-in members registered by receptionist may not have an account yet
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    full_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(
        db.Enum('MALE', 'FEMALE', 'OTHER', name='gender_enum'),
        nullable=False
    )
    birth_year = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)

    # BR4: Each member has at most 1 personal trainer (0..1 relationship)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    trainer = db.relationship('Trainer', backref='members')
    subscriptions = db.relationship('Subscription', backref='member',
                                    lazy='dynamic', order_by='Subscription.start_date.desc()')
    workout_plans = db.relationship('WorkoutPlan', backref='member', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Member {self.full_name} ({self.phone})>'
