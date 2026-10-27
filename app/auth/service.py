"""Authentication service – business logic for login/logout/session."""

from flask import session

from app.models.user import User
from app.auth.repository import UserRepository


class AuthService:
    """Handles authentication business logic.

    Depends on UserRepository (injected via constructor) to follow
    the Dependency Inversion Principle.
    """

    def __init__(self, user_repo: UserRepository | None = None):
        self.user_repo = user_repo or UserRepository()

    def authenticate(self, username: str, password: str) -> User:
        """Verify credentials and return the User object.

        Args:
            username: The username (phone number for MEMBER).
            password: The plaintext password.

        Returns:
            The authenticated User object.

        Raises:
            ValueError: If credentials are invalid or account is inactive.
        """
        if not username or not password:
            raise ValueError('Tên đăng nhập và mật khẩu không được để trống.')

        user = self.user_repo.find_by_username(username)

        if user is None or not user.check_password(password):
            raise ValueError('Tên đăng nhập hoặc mật khẩu không đúng.')

        if not user.is_active:
            raise ValueError('Tài khoản đã bị vô hiệu hóa.')

        return user

    def login(self, user: User) -> None:
        """Store user info in server-side session (Redis).

        Session data is stored in Redis; only a signed session ID
        is sent to the client as an HttpOnly cookie.
        """
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session.permanent = True

    def logout(self) -> None:
        """Clear the current session."""
        session.clear()

    def get_current_user(self) -> User | None:
        """Retrieve the currently logged-in user from session.

        Returns:
            User object or None if not logged in.
        """
        user_id = session.get('user_id')
        if user_id is None:
            return None
        return self.user_repo.find_by_id(user_id)
