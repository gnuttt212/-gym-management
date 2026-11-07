"""Subscription service – business logic for membership subscriptions.

BR1: end_date = start_date + plan.duration_months (using dateutil.relativedelta).
     A member is 'active' when date.today() <= end_date.

Renewal: creates a NEW Subscription row for the same member (does NOT create
         a new member record).
"""

from datetime import date
from dateutil.relativedelta import relativedelta

from app.extensions import db
from app.models.subscription import Subscription
from app.models.membership_plan import MembershipPlan
from app.subscriptions.repository import SubscriptionRepository


class SubscriptionService:
    """Handles subscription business logic."""

    def __init__(self, sub_repo: SubscriptionRepository | None = None):
        self.sub_repo = sub_repo or SubscriptionRepository()

    def get_plans(self, active_only: bool = True) -> list[MembershipPlan]:
        """Return all available membership plans."""
        return self.sub_repo.find_all_plans(active_only)

    def get_plan_by_id(self, plan_id: int) -> MembershipPlan:
        """Get a plan by ID or raise ValueError."""
        plan = self.sub_repo.find_plan_by_id(plan_id)
        if plan is None:
            raise ValueError('Gói tập không tồn tại.')
        if not plan.is_active:
            raise ValueError('Gói tập này đã ngừng hoạt động.')
        return plan

    def calculate_end_date(self, start_date: date,
                           duration_months: int) -> date:
        """Calculate subscription end date.

        BR1: end_date = start_date + duration_months.
        Uses dateutil.relativedelta for accurate month arithmetic.
        E.g. 2026-01-31 + 1 month = 2026-02-28 (not March 3).
        """
        return start_date + relativedelta(months=duration_months)

    def create_subscription(self, member_id: int, plan_id: int,
                            start_date: date | None = None) -> Subscription:
        """Create a new subscription for a member.

        BR1: Automatically calculates end_date from plan duration.

        Args:
            member_id: The member to subscribe.
            plan_id: The membership plan.
            start_date: Defaults to today if not provided.

        Returns:
            The created Subscription (not yet committed).

        Raises:
            ValueError: If plan doesn't exist or is inactive.
        """
        plan = self.get_plan_by_id(plan_id)

        if start_date is None:
            start_date = date.today()

        # BR1: Calculate end_date based on plan duration
        end_date = self.calculate_end_date(start_date, plan.duration_months)

        subscription = self.sub_repo.create(
            member_id=member_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date
        )
        return subscription

    def get_member_subscriptions(self, member_id: int) -> list[Subscription]:
        """Get all subscriptions for a member."""
        return self.sub_repo.find_by_member(member_id)

    def get_active_subscription(self, member_id: int) -> Subscription | None:
        """Get the active subscription for a member (BR1)."""
        return self.sub_repo.find_active_by_member(member_id)

    def is_member_active(self, member_id: int) -> bool:
        """Check if a member has an active (non-expired) subscription.

        BR1: Active when date.today() <= end_date.
        """
        return self.get_active_subscription(member_id) is not None

    def renew_subscription(self, member_id: int,
                           plan_id: int) -> Subscription:
        """Renew a member's subscription.

        Creates a new Subscription row (does NOT create a new member).
        If the member still has an active subscription, the new one
        starts from the day after the current one expires.
        """
        plan = self.get_plan_by_id(plan_id)

        # If currently active, new sub starts after current one ends
        active = self.get_active_subscription(member_id)
        if active and active.end_date >= date.today():
            start_date = active.end_date + relativedelta(days=1)
        else:
            start_date = date.today()

        end_date = self.calculate_end_date(start_date, plan.duration_months)

        subscription = self.sub_repo.create(
            member_id=member_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date
        )
        return subscription
