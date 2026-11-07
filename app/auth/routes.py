"""Auth routes – login, logout, dashboard, online registration.

Routes only handle HTTP request/response; all business logic
is delegated to AuthService and related services.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from marshmallow import ValidationError

from app.auth.service import AuthService
from app.auth.decorators import login_required
from app.auth.repository import UserRepository
from app.extensions import db
from app.members.service import MemberService
from app.subscriptions.service import SubscriptionService
from app.subscriptions.schemas import RegistrationSchema
from app.billing.service import BillingService
from app.notifications.service import NotificationService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Service instances (default repositories injected automatically)
auth_service = AuthService()
user_repo = UserRepository()
member_service = MemberService()
sub_service = SubscriptionService()
billing_service = BillingService()
notification_service = NotificationService()
_register_schema = RegistrationSchema()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and form handler."""
    # Already logged in → go to dashboard
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        try:
            user = auth_service.authenticate(username, password)
            auth_service.login(user)
            flash(f'Chào mừng {user.username}!', 'success')

            # Redirect to the page they originally wanted, or dashboard
            next_page = request.args.get('next') or url_for('auth.dashboard')
            return redirect(next_page)

        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    auth_service.logout()
    flash('Đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page – content varies by role."""
    role = session.get('role', '')
    return render_template('auth/dashboard.html', role=role)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Online member self-registration (UC01).

    Creates User (role MEMBER) + Member + Subscription + Invoice
    in ONE transaction. Sends confirmation email asynchronously (BR5).
    """
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))

    plans = sub_service.get_plans()

    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'gender': request.form.get('gender'),
            'birth_year': request.form.get('birth_year', type=int),
            'phone': request.form.get('phone', '').strip(),
            'email': request.form.get('email', '').strip() or None,
            'password': request.form.get('password', ''),
            'plan_id': request.form.get('plan_id', type=int),
        }

        try:
            # Validate input
            validated = _register_schema.load(data)

            plan = sub_service.get_plan_by_id(validated['plan_id'])

            # Check phone uniqueness (will be username)
            existing_user = user_repo.find_by_username(validated['phone'])
            if existing_user:
                raise ValueError(f"SĐT {validated['phone']} đã có tài khoản.")

            # ── ONE TRANSACTION: user + member + subscription + invoice ──
            # 1. Create user account (username = phone number)
            from app.models.user import User
            user = User(username=validated['phone'], role='MEMBER')
            user.set_password(validated['password'])
            db.session.add(user)
            db.session.flush()  # Get user.id

            # 2. Create member profile
            member = member_service.create_member({
                'full_name': validated['full_name'],
                'gender': validated['gender'],
                'birth_year': validated['birth_year'],
                'phone': validated['phone'],
                'email': validated.get('email'),
            })
            member.user_id = user.id
            db.session.flush()  # Get member.id

            # 3. Create subscription (BR1: auto-calculates end_date)
            subscription = sub_service.create_subscription(
                member_id=member.id, plan_id=plan.id
            )
            db.session.flush()  # Get subscription.id

            # 4. Create invoice (BR2: snapshot current plan price)
            billing_service.create_invoice(
                subscription_id=subscription.id,
                price_snapshot=float(plan.price)
            )

            # Commit entire transaction
            db.session.commit()

            # Send email (BR5: async, failure won't cancel registration)
            if member.email:
                notification_service.send_registration_email(
                    to_email=member.email,
                    member_name=member.full_name,
                    plan_name=plan.name,
                    start_date=str(subscription.start_date),
                    end_date=str(subscription.end_date),
                    price=f'{plan.price:,.0f}đ'
                )

            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))

        except ValidationError as e:
            db.session.rollback()
            for field, msgs in e.messages.items():
                for msg in msgs:
                    flash(msg, 'danger')
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi hệ thống: {e}', 'danger')

    return render_template('auth/register.html', plans=plans)
