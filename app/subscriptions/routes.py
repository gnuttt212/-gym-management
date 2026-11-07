"""Subscription routes – registration (online + walk-in) and renewal."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from marshmallow import ValidationError

from app.auth.decorators import login_required, roles_required
from app.extensions import db
from app.auth.repository import UserRepository
from app.members.service import MemberService
from app.subscriptions.service import SubscriptionService
from app.subscriptions.schemas import WalkInRegistrationSchema
from app.billing.service import BillingService
from app.notifications.service import NotificationService

subscriptions_bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

member_service = MemberService()
sub_service = SubscriptionService()
billing_service = BillingService()
notification_service = NotificationService()
user_repo = UserRepository()
_walkin_schema = WalkInRegistrationSchema()


@subscriptions_bp.route('/')
@roles_required('ADMIN', 'RECEPTIONIST')
def subscription_list():
    """List view – redirects to members list for now."""
    return redirect(url_for('members.member_list'))


@subscriptions_bp.route('/register', methods=['GET', 'POST'])
@roles_required('ADMIN', 'RECEPTIONIST')
def walk_in_register():
    """Walk-in registration by receptionist (UC02).

    Creates member + subscription + invoice in ONE transaction.
    Member has user_id=NULL (no account yet).
    """
    plans = sub_service.get_plans()

    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'gender': request.form.get('gender'),
            'birth_year': request.form.get('birth_year', type=int),
            'phone': request.form.get('phone', '').strip(),
            'email': request.form.get('email', '').strip() or None,
            'plan_id': request.form.get('plan_id', type=int),
        }

        try:
            # Validate
            validated = _walkin_schema.load(data)

            plan = sub_service.get_plan_by_id(validated['plan_id'])

            # ── ONE TRANSACTION: member + subscription + invoice ──
            # 1. Create member (user_id=NULL for walk-in)
            member = member_service.create_member({
                'full_name': validated['full_name'],
                'gender': validated['gender'],
                'birth_year': validated['birth_year'],
                'phone': validated['phone'],
                'email': validated.get('email'),
            })
            db.session.flush()  # Get member.id

            # 2. Create subscription (BR1: auto-calculates end_date)
            subscription = sub_service.create_subscription(
                member_id=member.id, plan_id=plan.id
            )
            db.session.flush()  # Get subscription.id

            # 3. Create invoice (BR2: snapshot current plan price)
            invoice = billing_service.create_invoice(
                subscription_id=subscription.id,
                price_snapshot=float(plan.price)
            )

            # Commit all in one transaction
            db.session.commit()

            # Send email notification (BR5: async, won't cancel registration)
            if member.email:
                notification_service.send_registration_email(
                    to_email=member.email,
                    member_name=member.full_name,
                    plan_name=plan.name,
                    start_date=str(subscription.start_date),
                    end_date=str(subscription.end_date),
                    price=f'{plan.price:,.0f}đ'
                )

            flash(f'Đăng ký thành công cho {member.full_name}!', 'success')
            return redirect(url_for('members.member_detail', member_id=member.id))

        except ValidationError as e:
            db.session.rollback()
            for field, msgs in e.messages.items():
                for msg in msgs:
                    flash(f'{msg}', 'danger')
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi hệ thống: {e}', 'danger')

    return render_template('subscriptions/register.html', plans=plans)


@subscriptions_bp.route('/renew/<int:member_id>', methods=['GET', 'POST'])
@roles_required('ADMIN', 'RECEPTIONIST')
def renew(member_id):
    """Renew a member's subscription – creates new subscription + invoice."""
    try:
        member = member_service.get_member_by_id(member_id)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('members.member_list'))

    plans = sub_service.get_plans()

    if request.method == 'POST':
        plan_id = request.form.get('plan_id', type=int)
        try:
            plan = sub_service.get_plan_by_id(plan_id)

            # Create new subscription (renewal logic in service)
            subscription = sub_service.renew_subscription(member.id, plan.id)
            db.session.flush()

            # Create invoice (BR2)
            billing_service.create_invoice(
                subscription_id=subscription.id,
                price_snapshot=float(plan.price)
            )
            db.session.commit()

            # Email notification (BR5)
            if member.email:
                notification_service.send_registration_email(
                    to_email=member.email,
                    member_name=member.full_name,
                    plan_name=plan.name,
                    start_date=str(subscription.start_date),
                    end_date=str(subscription.end_date),
                    price=f'{plan.price:,.0f}đ'
                )

            flash(f'Gia hạn thành công cho {member.full_name}!', 'success')
            return redirect(url_for('members.member_detail', member_id=member.id))

        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')

    return render_template('subscriptions/renew.html',
                           member=member, plans=plans)
