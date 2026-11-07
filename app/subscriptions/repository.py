"""Subscription repository – data access for subscriptions table."""

from datetime import date

from app.extensions import db
from app.models.subscription import Subscription
from app.models.membership_plan import MembershipPlan


class SubscriptionRepository:
    """Handles all database queries related to Subscription."""

    def find_by_id(self, sub_id: int) -> Subscription | None:
        """Find a subscription by primary key."""
        return db.session.get(Subscription, sub_id)

    def find_by_member(self, member_id: int) -> list[Subscription]:
        """Find all subscriptions for a member (newest first)."""
        return Subscription.query.filter_by(member_id=member_id) \
            .order_by(Subscription.start_date.desc()).all()

    def find_active_by_member(self, member_id: int) -> Subscription | None:
        """Find the active subscription (end_date >= today) for a member.

        BR1: A member is 'active' when current_date <= end_date.
        """
        today = date.today()
        return Subscription.query.filter(
            Subscription.member_id == member_id,
            Subscription.end_date >= today
        ).order_by(Subscription.end_date.desc()).first()

    def create(self, member_id: int, plan_id: int,
               start_date: date, end_date: date) -> Subscription:
        """Create a new subscription.

        Note: Does NOT commit – caller handles transaction.
        """
        sub = Subscription(
            member_id=member_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(sub)
        return sub

    def find_all_plans(self, active_only: bool = True) -> list[MembershipPlan]:
        """Return all membership plans."""
        query = MembershipPlan.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(MembershipPlan.duration_months).all()

    def find_plan_by_id(self, plan_id: int) -> MembershipPlan | None:
        """Find a membership plan by ID."""
        return db.session.get(MembershipPlan, plan_id)
