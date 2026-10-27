"""Subscription model – links members to membership plans.

BR1: end_date = start_date + plan.duration_months
Renewal = new Subscription row for the same member.
"""

from app.extensions import db
from datetime import datetime, timezone


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('membership_plans.id'), nullable=False)

    # BR1: end_date is computed as start_date + duration_months at registration time
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    invoice = db.relationship('Invoice', backref='subscription', uselist=False)

    def __repr__(self) -> str:
        return f'<Subscription member={self.member_id} plan={self.plan_id} {self.start_date}~{self.end_date}>'
