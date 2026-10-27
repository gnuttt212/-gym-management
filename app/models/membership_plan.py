"""MembershipPlan model – gym subscription plans with pricing."""

from app.extensions import db


class MembershipPlan(db.Model):
    __tablename__ = 'membership_plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # e.g. "Gói 1 tháng"
    duration_months = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(12, 0), nullable=False)  # VND, no decimals
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    subscriptions = db.relationship('Subscription', backref='plan', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<MembershipPlan {self.name} ({self.duration_months}m)>'
