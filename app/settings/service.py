"""Settings service – manage system configuration and plan pricing."""

from app.extensions import db
from app.models.setting import Setting
from app.models.membership_plan import MembershipPlan
from app.training.repository import SettingRepository


class SettingsService:
    """Handles system settings and plan pricing management."""

    def __init__(self, setting_repo: SettingRepository | None = None):
        self.setting_repo = setting_repo or SettingRepository()

    # ── Key-value settings ──

    def get_all_settings(self) -> list[Setting]:
        """Return all settings."""
        return Setting.query.order_by(Setting.key).all()

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        """Get a setting value."""
        return self.setting_repo.get(key, default)

    def update_setting(self, key: str, value: str) -> Setting:
        """Create or update a setting."""
        setting = self.setting_repo.set(key, value)
        db.session.commit()
        return setting

    def update_max_days_per_week(self, value: int) -> Setting:
        """Update max_days_per_week (BR3 config, must be 1..7)."""
        if not (1 <= value <= 7):
            raise ValueError('Số ngày tập tối đa phải từ 1 đến 7.')
        return self.update_setting('max_days_per_week', str(value))

    # ── Membership plan pricing ──

    def get_all_plans(self) -> list[MembershipPlan]:
        """Return all membership plans."""
        return MembershipPlan.query.order_by(MembershipPlan.duration_months).all()

    def update_plan_price(self, plan_id: int, new_price: float) -> MembershipPlan:
        """Update a plan's price.

        BR2: This only affects FUTURE invoices.
        Existing invoices keep their price_snapshot unchanged.
        """
        plan = db.session.get(MembershipPlan, plan_id)
        if plan is None:
            raise ValueError('Gói tập không tồn tại.')
        if new_price <= 0:
            raise ValueError('Giá gói phải lớn hơn 0.')

        plan.price = new_price
        db.session.commit()
        return plan

    def toggle_plan_active(self, plan_id: int) -> MembershipPlan:
        """Toggle a plan's active status."""
        plan = db.session.get(MembershipPlan, plan_id)
        if plan is None:
            raise ValueError('Gói tập không tồn tại.')
        plan.is_active = not plan.is_active
        db.session.commit()
        return plan
