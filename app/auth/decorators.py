"""Authentication & authorization decorators.

Usage:
    @auth_bp.route('/some-page')
    @login_required
    def some_page():
        ...

    @members_bp.route('/list')
    @roles_required('ADMIN', 'RECEPTIONIST')
    def member_list():
        ...
"""

from functools import wraps
from flask import session, redirect, url_for, flash, abort, request


def login_required(f):
    """Ensure the user is logged in (session contains user_id).

    Redirects to login page with a flash message if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            # Remember where the user wanted to go
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def roles_required(*allowed_roles: str):
    """Restrict access to users with specific roles.

    Args:
        allowed_roles: One or more role strings (e.g. 'ADMIN', 'RECEPTIONIST').

    Raises:
        403 Forbidden if the user's role is not in allowed_roles.
        Redirects to login if not authenticated.

    Example:
        @roles_required('ADMIN', 'CASHIER')
        def billing_page(): ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check login first
            if 'user_id' not in session:
                flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
                return redirect(url_for('auth.login', next=request.path))

            # Check role
            user_role = session.get('role')
            if user_role not in allowed_roles:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
