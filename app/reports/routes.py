"""Reports routes – admin dashboard with Chart.js data endpoints."""

from datetime import date
from flask import Blueprint, render_template, request, jsonify

from app.auth.decorators import roles_required
from app.reports.service import ReportService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

report_service = ReportService()


@reports_bp.route('/')
@roles_required('ADMIN')
def dashboard():
    """Admin reports dashboard with summary stats and charts."""
    summary = report_service.get_summary()
    current_year = date.today().year
    return render_template('reports/dashboard.html',
                           summary=summary, current_year=current_year)


@reports_bp.route('/registrations.json')
@roles_required('ADMIN')
def registrations_json():
    """JSON endpoint for registration chart (Chart.js).

    Query param: ?year=2026 (defaults to current year).
    """
    year = request.args.get('year', type=int, default=date.today().year)
    data = report_service.get_registration_chart_data(year)
    return jsonify(data)


@reports_bp.route('/revenue.json')
@roles_required('ADMIN')
def revenue_json():
    """JSON endpoint for revenue chart (Chart.js).

    Revenue = PAID invoices only, grouped by paid_at month.
    Query param: ?year=2026 (defaults to current year).
    """
    year = request.args.get('year', type=int, default=date.today().year)
    data = report_service.get_revenue_chart_data(year)
    return jsonify(data)
