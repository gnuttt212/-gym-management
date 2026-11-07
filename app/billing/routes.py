"""Billing routes – invoice management and payment confirmation."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.auth.decorators import login_required, roles_required
from app.billing.service import BillingService
from app.members.service import MemberService

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

billing_service = BillingService()
member_service = MemberService()


@billing_bp.route('/')
@roles_required('ADMIN', 'CASHIER')
def invoice_list():
    """List all invoices – filter by status."""
    status_filter = request.args.get('status', '')
    if status_filter == 'UNPAID':
        invoices = billing_service.get_unpaid_invoices()
    else:
        invoices = billing_service.get_all_invoices()
    return render_template('billing/list.html',
                           invoices=invoices, status_filter=status_filter)


@billing_bp.route('/<int:invoice_id>/pay', methods=['POST'])
@roles_required('ADMIN', 'CASHIER')
def confirm_payment(invoice_id):
    """Confirm payment for an invoice (CASHIER action)."""
    payment_method = request.form.get('payment_method', '')
    cashier_id = session.get('user_id')

    try:
        billing_service.confirm_payment(invoice_id, payment_method, cashier_id)
        flash('Thanh toán thành công!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')

    return redirect(url_for('billing.invoice_list'))


@billing_bp.route('/my-invoices')
@login_required
def my_invoices():
    """Member views their own invoices."""
    if session.get('role') != 'MEMBER':
        flash('Chức năng dành cho hội viên.', 'warning')
        return redirect(url_for('auth.dashboard'))

    user_id = session.get('user_id')
    member = member_service.get_member_for_user(user_id)
    if member is None:
        flash('Không tìm thấy thông tin hội viên.', 'warning')
        return redirect(url_for('auth.dashboard'))

    # Service-level ownership check (not just UI)
    invoices = billing_service.get_member_invoices(member.id)
    return render_template('billing/my_invoices.html', invoices=invoices)
