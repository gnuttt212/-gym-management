"""Reports repository – statistical queries for admin dashboard.

Revenue is calculated from PAID invoices only, grouped by paid_at month.
"""

from datetime import date
from sqlalchemy import func, extract

from app.extensions import db
from app.models.member import Member
from app.models.subscription import Subscription
from app.models.invoice import Invoice


class ReportRepository:
    """Handles statistical database queries for reports."""

    def count_active_members(self) -> int:
        """Count members with at least one active subscription.

        BR1: Active = current_date <= end_date.
        """
        today = date.today()
        return db.session.query(func.count(func.distinct(Subscription.member_id))) \
            .filter(Subscription.end_date >= today).scalar() or 0

    def count_total_members(self) -> int:
        """Count total registered members."""
        return db.session.query(func.count(Member.id)).scalar() or 0

    def registrations_by_month(self, year: int | None = None) -> list[dict]:
        """Count new member registrations grouped by month.

        Returns list of {'month': int, 'year': int, 'count': int}.
        """
        query = db.session.query(
            extract('year', Member.created_at).label('year'),
            extract('month', Member.created_at).label('month'),
            func.count(Member.id).label('count'),
        ).group_by('year', 'month').order_by('year', 'month')

        if year:
            query = query.filter(extract('year', Member.created_at) == year)

        rows = query.all()
        return [
            {'year': int(r.year), 'month': int(r.month), 'count': r.count}
            for r in rows
        ]

    def revenue_by_month(self, year: int | None = None) -> list[dict]:
        """Calculate total revenue grouped by month.

        Revenue = sum of price_snapshot for PAID invoices,
        grouped by month of paid_at.

        Returns list of {'month': int, 'year': int, 'revenue': float}.
        """
        query = db.session.query(
            extract('year', Invoice.paid_at).label('year'),
            extract('month', Invoice.paid_at).label('month'),
            func.sum(Invoice.price_snapshot).label('revenue'),
        ).filter(
            Invoice.status == 'PAID',
            Invoice.paid_at.isnot(None),
        ).group_by('year', 'month').order_by('year', 'month')

        if year:
            query = query.filter(extract('year', Invoice.paid_at) == year)

        rows = query.all()
        return [
            {'year': int(r.year), 'month': int(r.month),
             'revenue': float(r.revenue)}
            for r in rows
        ]

    def total_revenue(self) -> float:
        """Total revenue from all PAID invoices."""
        result = db.session.query(func.sum(Invoice.price_snapshot)) \
            .filter(Invoice.status == 'PAID').scalar()
        return float(result) if result else 0.0

    def unpaid_count(self) -> int:
        """Count unpaid invoices."""
        return db.session.query(func.count(Invoice.id)) \
            .filter(Invoice.status == 'UNPAID').scalar() or 0
