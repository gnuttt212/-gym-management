"""Training service – business logic for exercises and workout plans.

BR3: Total distinct weekdays across all items in a plan must NOT exceed
     the max_days_per_week setting (read from settings table, value 1..7).

BR4: Each member has at most 1 personal trainer. A trainer can only
     create workout plans for members assigned to them.
"""

from marshmallow import ValidationError

from app.extensions import db
from app.models.exercise import Exercise
from app.models.workout_plan import WorkoutPlan
from app.models.member import Member
from app.models.trainer import Trainer
from app.training.repository import (
    ExerciseRepository, WorkoutPlanRepository, SettingRepository
)
from app.training.schemas import ExerciseSchema, WorkoutPlanSchema


class TrainingService:
    """Handles training business logic (exercises + workout plans)."""

    def __init__(
        self,
        exercise_repo: ExerciseRepository | None = None,
        plan_repo: WorkoutPlanRepository | None = None,
        setting_repo: SettingRepository | None = None,
    ):
        self.exercise_repo = exercise_repo or ExerciseRepository()
        self.plan_repo = plan_repo or WorkoutPlanRepository()
        self.setting_repo = setting_repo or SettingRepository()
        self._exercise_schema = ExerciseSchema()

    # ── Exercises ──────────────────────────────────────────────────

    def get_exercises(self, active_only: bool = True) -> list[Exercise]:
        """Return all exercises."""
        return self.exercise_repo.find_all(active_only)

    def get_exercise_by_id(self, exercise_id: int) -> Exercise:
        """Get an exercise or raise ValueError."""
        exercise = self.exercise_repo.find_by_id(exercise_id)
        if exercise is None:
            raise ValueError('Bài tập không tồn tại.')
        return exercise

    def create_exercise(self, name: str) -> Exercise:
        """Create a new exercise.

        Raises:
            ValidationError: If name is invalid.
            ValueError: If name already exists.
        """
        validated = self._exercise_schema.load({'name': name.strip()})

        existing = self.exercise_repo.find_by_name(validated['name'])
        if existing:
            if not existing.is_active:
                # Re-activate soft-deleted exercise
                existing.is_active = True
                db.session.commit()
                return existing
            raise ValueError(f"Bài tập '{validated['name']}' đã tồn tại.")

        exercise = self.exercise_repo.create(validated['name'])
        db.session.commit()
        return exercise

    def update_exercise(self, exercise_id: int, name: str) -> Exercise:
        """Update an exercise name."""
        exercise = self.get_exercise_by_id(exercise_id)
        validated = self._exercise_schema.load({'name': name.strip()})

        # Check uniqueness
        existing = self.exercise_repo.find_by_name(validated['name'])
        if existing and existing.id != exercise_id:
            raise ValueError(f"Bài tập '{validated['name']}' đã tồn tại.")

        self.exercise_repo.update(exercise, name=validated['name'])
        db.session.commit()
        return exercise

    def delete_exercise(self, exercise_id: int) -> Exercise:
        """Soft-delete an exercise (is_active=False).

        Soft delete because the exercise may be referenced in existing plans.
        """
        exercise = self.get_exercise_by_id(exercise_id)
        self.exercise_repo.soft_delete(exercise)
        db.session.commit()
        return exercise

    # ── Workout Plans ──────────────────────────────────────────────

    def get_max_days_per_week(self) -> int:
        """Read max_days_per_week from settings table."""
        value = self.setting_repo.get('max_days_per_week', '6')
        return int(value)

    def get_plan_by_id(self, plan_id: int) -> WorkoutPlan:
        """Get a workout plan or raise ValueError."""
        plan = self.plan_repo.find_by_id(plan_id)
        if plan is None:
            raise ValueError('Kế hoạch tập không tồn tại.')
        return plan

    def get_plans_for_member(self, member_id: int) -> list[WorkoutPlan]:
        """Get all workout plans for a member."""
        return self.plan_repo.find_by_member(member_id)

    def get_plans_for_trainer(self, trainer_id: int) -> list[WorkoutPlan]:
        """Get all workout plans created by a trainer."""
        return self.plan_repo.find_by_trainer(trainer_id)

    def get_trainer_by_user_id(self, user_id: int) -> Trainer:
        """Find the Trainer record linked to a user account."""
        trainer = Trainer.query.filter_by(user_id=user_id).first()
        if trainer is None:
            raise ValueError('Tài khoản này không phải huấn luyện viên.')
        return trainer

    def get_assigned_members(self, trainer_id: int) -> list[Member]:
        """Get all members assigned to a trainer (BR4)."""
        return Member.query.filter_by(trainer_id=trainer_id).all()

    def create_workout_plan(self, trainer_id: int, member_id: int,
                            items_data: list[dict]) -> WorkoutPlan:
        """Create a workout plan with validation.

        BR3: Validate total distinct weekdays <= max_days_per_week.
        BR4: Trainer can only create plans for members assigned to them.

        Args:
            trainer_id: The trainer creating the plan.
            member_id: The member receiving the plan.
            items_data: List of dicts with exercise_id, sets, reps_per_set, weekdays.

        Raises:
            ValueError: If BR3 or BR4 violated, or invalid data.
        """
        # BR4: Verify trainer is assigned to this member
        member = db.session.get(Member, member_id)
        if member is None:
            raise ValueError('Hội viên không tồn tại.')
        if member.trainer_id != trainer_id:
            raise ValueError(
                'Bạn chỉ có thể tạo kế hoạch cho hội viên được gán cho mình (BR4).'
            )

        if not items_data:
            raise ValueError('Kế hoạch phải có ít nhất 1 bài tập.')

        # Validate each item and collect all weekdays
        all_weekdays = set()
        validated_items = []
        for item in items_data:
            exercise = self.exercise_repo.find_by_id(item.get('exercise_id'))
            if exercise is None or not exercise.is_active:
                raise ValueError(
                    f"Bài tập ID={item.get('exercise_id')} không tồn tại hoặc đã bị xóa."
                )

            sets = item.get('sets', 0)
            reps = item.get('reps_per_set', 0)
            if sets < 1 or sets > 20:
                raise ValueError('Số hiệp phải từ 1 đến 20.')
            if reps < 1 or reps > 100:
                raise ValueError('Số lần/hiệp phải từ 1 đến 100.')

            weekdays_str = item.get('weekdays', '')
            # Parse and validate weekdays
            weekday_nums = self._parse_weekdays(weekdays_str)
            all_weekdays.update(weekday_nums)

            validated_items.append({
                'exercise_id': exercise.id,
                'sets': sets,
                'reps_per_set': reps,
                'weekdays': ','.join(str(d) for d in sorted(weekday_nums)),
            })

        # BR3: Check total distinct weekdays against max_days_per_week
        max_days = self.get_max_days_per_week()
        if len(all_weekdays) > max_days:
            raise ValueError(
                f'Tổng số ngày tập ({len(all_weekdays)}) vượt quá '
                f'giới hạn {max_days} ngày/tuần (BR3).'
            )

        # Create plan + items in one transaction
        plan = self.plan_repo.create(
            member_id=member_id,
            trainer_id=trainer_id,
            items_data=validated_items,
        )
        db.session.commit()
        return plan

    def delete_workout_plan(self, plan_id: int, trainer_id: int) -> None:
        """Delete a workout plan (only by its trainer)."""
        plan = self.get_plan_by_id(plan_id)
        if plan.trainer_id != trainer_id:
            raise ValueError('Bạn chỉ có thể xóa kế hoạch do mình tạo.')
        self.plan_repo.delete(plan)
        db.session.commit()

    @staticmethod
    def _parse_weekdays(weekdays_str: str) -> set[int]:
        """Parse weekdays string (e.g. '1,3,5') into a set of ints.

        Validates each value is 1..7 (ISO: 1=Monday, 7=Sunday).
        """
        if not weekdays_str or not weekdays_str.strip():
            raise ValueError('Phải chọn ít nhất 1 ngày tập.')

        try:
            nums = {int(d.strip()) for d in weekdays_str.split(',')}
        except ValueError:
            raise ValueError('Ngày tập không hợp lệ (phải là số 1-7).')

        for n in nums:
            if n < 1 or n > 7:
                raise ValueError(f'Ngày tập {n} không hợp lệ (1=T2, 7=CN).')

        return nums

    @staticmethod
    def weekday_name(num: int) -> str:
        """Convert weekday number to Vietnamese name."""
        names = {
            1: 'Thứ 2', 2: 'Thứ 3', 3: 'Thứ 4',
            4: 'Thứ 5', 5: 'Thứ 6', 6: 'Thứ 7', 7: 'CN'
        }
        return names.get(num, '?')
