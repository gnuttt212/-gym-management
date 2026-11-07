"""Settings routes – system configuration for ADMIN."""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.auth.decorators import roles_required
from app.settings.service import SettingsService

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

settings_service = SettingsService()


@settings_bp.route('/')
@roles_required('ADMIN')
def index():
    """Settings management page."""
    settings = settings_service.get_all_settings()
    plans = settings_service.get_all_plans()
    max_days = settings_service.get_setting('max_days_per_week', '6')
    return render_template('settings/index.html',
                           settings=settings, plans=plans,
                           max_days=int(max_days))


@settings_bp.route('/max-days', methods=['POST'])
@roles_required('ADMIN')
def update_max_days():
    """Update max_days_per_week setting (BR3)."""
    value = request.form.get('max_days', type=int, default=6)
    try:
        settings_service.update_max_days_per_week(value)
        flash(f'Đã cập nhật số ngày tập tối đa: {value} ngày/tuần.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('settings.index'))


@settings_bp.route('/plans/<int:plan_id>/price', methods=['POST'])
@roles_required('ADMIN')
def update_plan_price(plan_id):
    """Update a plan's price (BR2: only affects future invoices)."""
    try:
        price_str = request.form.get('price', '0').replace(',', '').replace('.', '')
        new_price = float(price_str)
        settings_service.update_plan_price(plan_id, new_price)
        flash('Đã cập nhật giá gói tập.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('settings.index'))


@settings_bp.route('/plans/<int:plan_id>/toggle', methods=['POST'])
@roles_required('ADMIN')
def toggle_plan(plan_id):
    """Toggle a plan's active status."""
    try:
        plan = settings_service.toggle_plan_active(plan_id)
        status = 'kích hoạt' if plan.is_active else 'vô hiệu hóa'
        flash(f'Đã {status} gói "{plan.name}".', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('settings.index'))
