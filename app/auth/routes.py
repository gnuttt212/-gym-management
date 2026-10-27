"""Auth routes – login, logout, dashboard.

Routes only handle HTTP request/response; all business logic
is delegated to AuthService.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.auth.service import AuthService
from app.auth.decorators import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Service instance (default repository injected automatically)
auth_service = AuthService()


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
    """Member self-registration – full implementation in Phase 4."""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return render_template('auth/register.html')

