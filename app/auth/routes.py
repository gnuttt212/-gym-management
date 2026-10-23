from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login():
    """Login page – implemented in Phase 3."""
    return render_template('auth/login.html')


@auth_bp.route('/dashboard')
def dashboard():
    """Dashboard page – implemented in Phase 3."""
    return render_template('auth/dashboard.html')
