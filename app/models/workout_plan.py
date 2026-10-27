"""WorkoutPlan and WorkoutPlanItem models.

BR3: Total distinct weekdays across all items in a plan must not exceed
     the max_days_per_week setting (validated in service layer).
"""

from app.extensions import db
from datetime import datetime, timezone


class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    items = db.relationship(
        'WorkoutPlanItem', backref='plan', lazy='joined',
        cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'<WorkoutPlan #{self.id} member={self.member_id}>'


class WorkoutPlanItem(db.Model):
    __tablename__ = 'workout_plan_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_id = db.Column(
        db.Integer, db.ForeignKey('workout_plans.id', ondelete='CASCADE'),
        nullable=False
    )
    exercise_id = db.Column(
        db.Integer, db.ForeignKey('exercises.id'), nullable=False
    )

    sets = db.Column(db.Integer, nullable=False)         # Number of sets
    reps_per_set = db.Column(db.Integer, nullable=False)  # Reps per set

    # Comma-separated weekday numbers: "1,3,5" = Mon, Wed, Fri (ISO: 1=Mon, 7=Sun)
    weekdays = db.Column(db.String(20), nullable=False)

    # Relationships
    exercise = db.relationship('Exercise')

    @property
    def weekday_list(self) -> list[int]:
        """Parse weekdays string into a list of ints."""
        return [int(d) for d in self.weekdays.split(',') if d.strip()]

    def __repr__(self) -> str:
        return f'<WorkoutPlanItem exercise={self.exercise_id} sets={self.sets}x{self.reps_per_set}>'
