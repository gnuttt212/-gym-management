"""User repository – data access layer for users table."""

from app.extensions import db
from app.models.user import User


class UserRepository:
    """Handles all database queries related to the User model."""

    def find_by_id(self, user_id: int) -> User | None:
        """Find a user by primary key."""
        return db.session.get(User, user_id)

    def find_by_username(self, username: str) -> User | None:
        """Find a user by username (case-sensitive)."""
        return User.query.filter_by(username=username).first()

    def create(self, username: str, password: str, role: str) -> User:
        """Create a new user with hashed password.

        Note: Does NOT commit – caller is responsible for transaction.
        """
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        return user
