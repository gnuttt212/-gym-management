"""Member repository – data access layer for members table."""

from app.extensions import db
from app.models.member import Member


class MemberRepository:
    """Handles all database queries related to Member."""

    def find_all(self) -> list[Member]:
        """Return all members ordered by creation date (newest first)."""
        return Member.query.order_by(Member.created_at.desc()).all()

    def find_by_id(self, member_id: int) -> Member | None:
        """Find a member by primary key."""
        return db.session.get(Member, member_id)

    def find_by_phone(self, phone: str) -> Member | None:
        """Find a member by phone number (unique)."""
        return Member.query.filter_by(phone=phone).first()

    def find_by_user_id(self, user_id: int) -> Member | None:
        """Find a member by linked user account."""
        return Member.query.filter_by(user_id=user_id).first()

    def create(self, **kwargs) -> Member:
        """Create a new member.

        Note: Does NOT commit – caller handles transaction.
        """
        member = Member(**kwargs)
        db.session.add(member)
        return member

    def update(self, member: Member, **kwargs) -> Member:
        """Update member fields.

        Note: Does NOT commit – caller handles transaction.
        """
        for key, value in kwargs.items():
            if hasattr(member, key):
                setattr(member, key, value)
        return member

    def search(self, keyword: str) -> list[Member]:
        """Search members by name or phone."""
        pattern = f'%{keyword}%'
        return Member.query.filter(
            db.or_(
                Member.full_name.ilike(pattern),
                Member.phone.like(pattern)
            )
        ).order_by(Member.created_at.desc()).all()
