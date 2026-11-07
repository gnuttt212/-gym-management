"""Member service – business logic for member management."""

from marshmallow import ValidationError

from app.extensions import db
from app.models.member import Member
from app.members.repository import MemberRepository
from app.members.schemas import MemberCreateSchema, MemberUpdateSchema


class MemberService:
    """Handles member business logic.

    Rules:
        - Phone number must be unique (raise ValueError if duplicate).
        - BR4: Each member has at most 1 personal trainer.
    """

    def __init__(self, member_repo: MemberRepository | None = None):
        self.member_repo = member_repo or MemberRepository()
        self._create_schema = MemberCreateSchema()
        self._update_schema = MemberUpdateSchema()

    def get_all_members(self) -> list[Member]:
        """Return all members."""
        return self.member_repo.find_all()

    def get_member_by_id(self, member_id: int) -> Member:
        """Get a member by ID or raise ValueError."""
        member = self.member_repo.find_by_id(member_id)
        if member is None:
            raise ValueError('Hội viên không tồn tại.')
        return member

    def get_member_for_user(self, user_id: int) -> Member | None:
        """Get the member linked to a user account."""
        return self.member_repo.find_by_user_id(user_id)

    def create_member(self, data: dict) -> Member:
        """Validate and create a new member.

        Args:
            data: Dict with full_name, gender, birth_year, phone, email, trainer_id.

        Returns:
            The created Member.

        Raises:
            ValidationError: If input data is invalid.
            ValueError: If phone number is duplicate.
        """
        # Validate input
        validated = self._create_schema.load(data)

        # Check phone uniqueness
        existing = self.member_repo.find_by_phone(validated['phone'])
        if existing:
            raise ValueError(
                f"SĐT {validated['phone']} đã được đăng ký cho hội viên khác."
            )

        # Create member (does NOT commit – caller handles transaction)
        member = self.member_repo.create(**validated)
        return member

    def update_member(self, member_id: int, data: dict) -> Member:
        """Validate and update an existing member.

        Phone number cannot be changed (it's the unique identifier).

        Raises:
            ValidationError: If input data is invalid.
            ValueError: If member not found.
        """
        member = self.get_member_by_id(member_id)
        validated = self._update_schema.load(data)

        # Update (does NOT commit)
        self.member_repo.update(member, **validated)
        return member

    def search_members(self, keyword: str) -> list[Member]:
        """Search members by name or phone."""
        return self.member_repo.search(keyword)

    def assign_trainer(self, member_id: int, trainer_id: int | None) -> Member:
        """Assign or remove a personal trainer for a member (BR4: max 1).

        Args:
            member_id: The member to update.
            trainer_id: The trainer ID, or None to remove.
        """
        member = self.get_member_by_id(member_id)
        member.trainer_id = trainer_id
        return member
