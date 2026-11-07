"""Reports service – aggregate data for admin dashboard and Chart.js."""

from datetime import date

from app.reports.repository import ReportRepository


class ReportService:
    """Handles report business logic and data formatting."""

    def __init__(self, report_repo: ReportRepository | None = None):
        self.report_repo = report_repo or ReportRepository()

    def get_summary(self) -> dict:
        """Get dashboard summary stats."""
        return {
            'total_members': self.report_repo.count_total_members(),
            'active_members': self.report_repo.count_active_members(),
            'total_revenue': self.report_repo.total_revenue(),
            'unpaid_count': self.report_repo.unpaid_count(),
        }

    def get_registration_chart_data(self, year: int | None = None) -> dict:
        """Format registration data for Chart.js.

        Returns {'labels': ['T1', 'T2', ...], 'data': [count, ...]}.
        """
        if year is None:
            year = date.today().year

        rows = self.report_repo.registrations_by_month(year)

        # Build full 12-month data with zeros for missing months
        month_map = {r['month']: r['count'] for r in rows}
        labels = [f'T{m}' for m in range(1, 13)]
        data = [month_map.get(m, 0) for m in range(1, 13)]

        return {'labels': labels, 'data': data, 'year': year}

    def get_revenue_chart_data(self, year: int | None = None) -> dict:
        """Format revenue data for Chart.js.

        Revenue only counts PAID invoices, grouped by paid_at month.
        Returns {'labels': ['T1', ...], 'data': [revenue, ...]}.
        """
        if year is None:
            year = date.today().year

        rows = self.report_repo.revenue_by_month(year)

        month_map = {r['month']: r['revenue'] for r in rows}
        labels = [f'T{m}' for m in range(1, 13)]
        data = [month_map.get(m, 0) for m in range(1, 13)]

        return {'labels': labels, 'data': data, 'year': year}
