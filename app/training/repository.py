"""Training repository – data access for exercises and workout plans."""

from app.extensions import db
from app.models.exercise import Exercise
from app.models.workout_plan import WorkoutPlan, WorkoutPlanItem
from app.models.setting import Setting


class ExerciseRepository:
    """Handles all database queries related to Exercise."""

    def find_all(self, active_only: bool = True) -> list[Exercise]:
        """Return exercises, optionally only active ones."""
        query = Exercise.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Exercise.name).all()

    def find_by_id(self, exercise_id: int) -> Exercise | None:
        """Find an exercise by primary key."""
        return db.session.get(Exercise, exercise_id)

    def find_by_name(self, name: str) -> Exercise | None:
        """Find an exercise by exact name."""
        return Exercise.query.filter_by(name=name).first()

    def create(self, name: str) -> Exercise:
        """Create a new exercise. Does NOT commit."""
        exercise = Exercise(name=name)
        db.session.add(exercise)
        return exercise

    def update(self, exercise: Exercise, **kwargs) -> Exercise:
        """Update exercise fields. Does NOT commit."""
        for key, value in kwargs.items():
            if hasattr(exercise, key):
                setattr(exercise, key, value)
        return exercise

    def soft_delete(self, exercise: Exercise) -> Exercise:
        """Soft-delete: set is_active=False. Does NOT commit."""
        exercise.is_active = False
        return exercise


class WorkoutPlanRepository:
    """Handles all database queries related to WorkoutPlan."""

    def find_by_id(self, plan_id: int) -> WorkoutPlan | None:
        """Find a workout plan by primary key (items eagerly loaded)."""
        return db.session.get(WorkoutPlan, plan_id)

    def find_by_member(self, member_id: int) -> list[WorkoutPlan]:
        """Find all workout plans for a member (newest first)."""
        return WorkoutPlan.query.filter_by(member_id=member_id) \
            .order_by(WorkoutPlan.created_at.desc()).all()

    def find_by_trainer(self, trainer_id: int) -> list[WorkoutPlan]:
        """Find all workout plans created by a trainer (newest first)."""
        return WorkoutPlan.query.filter_by(trainer_id=trainer_id) \
            .order_by(WorkoutPlan.created_at.desc()).all()

    def create(self, member_id: int, trainer_id: int,
               items_data: list[dict]) -> WorkoutPlan:
        """Create a workout plan with items.

        Args:
            member_id: The member this plan belongs to.
            trainer_id: The trainer who created it.
            items_data: List of dicts with keys:
                exercise_id, sets, reps_per_set, weekdays (str "1,3,5").

        Note: Does NOT commit – caller handles transaction.
        """
        plan = WorkoutPlan(member_id=member_id, trainer_id=trainer_id)
        db.session.add(plan)
        db.session.flush()  # Get plan.id

        for item_data in items_data:
            item = WorkoutPlanItem(
                plan_id=plan.id,
                exercise_id=item_data['exercise_id'],
                sets=item_data['sets'],
                reps_per_set=item_data['reps_per_set'],
                weekdays=item_data['weekdays'],
            )
            db.session.add(item)

        return plan

    def delete(self, plan: WorkoutPlan) -> None:
        """Delete a workout plan and its items (cascade). Does NOT commit."""
        db.session.delete(plan)


class SettingRepository:
    """Handles database queries for the settings table."""

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get a setting value by key."""
        setting = db.session.get(Setting, key)
        return setting.value if setting else default

    def set(self, key: str, value: str) -> Setting:
        """Create or update a setting. Does NOT commit."""
        setting = db.session.get(Setting, key)
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        return setting
