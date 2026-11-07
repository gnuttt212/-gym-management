"""Training routes – exercise management and workout plan CRUD.

- ADMIN: manage exercises (add/edit/soft-delete)
- TRAINER: create/view/delete workout plans for assigned members
- MEMBER: view own workout plans
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.auth.decorators import login_required, roles_required
from app.extensions import db
from app.training.service import TrainingService
from app.members.service import MemberService

training_bp = Blueprint('training', __name__, url_prefix='/training')

training_service = TrainingService()
member_service = MemberService()


# ── Exercise Management (ADMIN) ──────────────────────────────────

@training_bp.route('/exercises')
@roles_required('ADMIN', 'TRAINER')
def exercise_list():
    """List all exercises. ADMIN can manage; TRAINER can view."""
    show_inactive = request.args.get('all', '') == '1'
    exercises = training_service.get_exercises(active_only=not show_inactive)
    return render_template('training/exercises.html',
                           exercises=exercises, show_inactive=show_inactive)


@training_bp.route('/exercises/add', methods=['POST'])
@roles_required('ADMIN')
def exercise_add():
    """Add a new exercise."""
    name = request.form.get('name', '').strip()
    try:
        training_service.create_exercise(name)
        flash(f'Đã thêm bài tập "{name}".', 'success')
    except (ValueError, Exception) as e:
        flash(str(e), 'danger')
    return redirect(url_for('training.exercise_list'))


@training_bp.route('/exercises/<int:exercise_id>/edit', methods=['POST'])
@roles_required('ADMIN')
def exercise_edit(exercise_id):
    """Rename an exercise."""
    name = request.form.get('name', '').strip()
    try:
        training_service.update_exercise(exercise_id, name)
        flash('Đã cập nhật bài tập.', 'success')
    except (ValueError, Exception) as e:
        flash(str(e), 'danger')
    return redirect(url_for('training.exercise_list'))


@training_bp.route('/exercises/<int:exercise_id>/delete', methods=['POST'])
@roles_required('ADMIN')
def exercise_delete(exercise_id):
    """Soft-delete an exercise."""
    try:
        training_service.delete_exercise(exercise_id)
        flash('Đã xóa bài tập (xóa mềm).', 'success')
    except (ValueError, Exception) as e:
        flash(str(e), 'danger')
    return redirect(url_for('training.exercise_list'))


# ── Workout Plans (TRAINER) ──────────────────────────────────────

@training_bp.route('/plans')
@roles_required('TRAINER')
def trainer_plans():
    """Trainer views all their workout plans + assigned members."""
    user_id = session.get('user_id')
    try:
        trainer = training_service.get_trainer_by_user_id(user_id)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('auth.dashboard'))

    plans = training_service.get_plans_for_trainer(trainer.id)
    assigned_members = training_service.get_assigned_members(trainer.id)

    return render_template('training/trainer_plans.html',
                           trainer=trainer, plans=plans,
                           assigned_members=assigned_members)


@training_bp.route('/plans/create/<int:member_id>', methods=['GET', 'POST'])
@roles_required('TRAINER')
def plan_create(member_id):
    """Create a workout plan for an assigned member."""
    user_id = session.get('user_id')
    try:
        trainer = training_service.get_trainer_by_user_id(user_id)
        member = member_service.get_member_by_id(member_id)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('training.trainer_plans'))

    # BR4: Check assignment
    if member.trainer_id != trainer.id:
        flash('Hội viên này không được gán cho bạn (BR4).', 'danger')
        return redirect(url_for('training.trainer_plans'))

    exercises = training_service.get_exercises(active_only=True)
    max_days = training_service.get_max_days_per_week()

    if request.method == 'POST':
        # Parse dynamic form: items sent as item_0_exercise_id, item_0_sets, etc.
        items_data = []
        i = 0
        while True:
            exercise_id = request.form.get(f'item_{i}_exercise_id')
            if exercise_id is None:
                break

            sets = request.form.get(f'item_{i}_sets', type=int, default=0)
            reps = request.form.get(f'item_{i}_reps', type=int, default=0)

            # Collect checked weekdays for this item
            weekdays = request.form.getlist(f'item_{i}_weekdays')
            weekdays_str = ','.join(weekdays) if weekdays else ''

            items_data.append({
                'exercise_id': int(exercise_id),
                'sets': sets,
                'reps_per_set': reps,
                'weekdays': weekdays_str,
            })
            i += 1

        try:
            plan = training_service.create_workout_plan(
                trainer_id=trainer.id,
                member_id=member.id,
                items_data=items_data,
            )
            flash(f'Đã tạo kế hoạch tập #{plan.id} cho {member.full_name}!', 'success')
            return redirect(url_for('training.plan_detail', plan_id=plan.id))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('training/plan_create.html',
                           member=member, exercises=exercises,
                           max_days=max_days)


@training_bp.route('/plans/<int:plan_id>')
@login_required
def plan_detail(plan_id):
    """View a workout plan. Accessible by TRAINER (owner) or MEMBER (own plan)."""
    try:
        plan = training_service.get_plan_by_id(plan_id)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('auth.dashboard'))

    role = session.get('role')
    user_id = session.get('user_id')

    # Access control: TRAINER who owns the plan, or MEMBER who owns the plan
    if role == 'TRAINER':
        trainer = training_service.get_trainer_by_user_id(user_id)
        if plan.trainer_id != trainer.id:
            flash('Bạn không có quyền xem kế hoạch này.', 'danger')
            return redirect(url_for('training.trainer_plans'))
    elif role == 'MEMBER':
        member = member_service.get_member_for_user(user_id)
        if member is None or plan.member_id != member.id:
            flash('Bạn không có quyền xem kế hoạch này.', 'danger')
            return redirect(url_for('auth.dashboard'))
    elif role != 'ADMIN':
        flash('Không có quyền truy cập.', 'danger')
        return redirect(url_for('auth.dashboard'))

    return render_template('training/plan_detail.html', plan=plan,
                           weekday_name=training_service.weekday_name)


@training_bp.route('/plans/<int:plan_id>/delete', methods=['POST'])
@roles_required('TRAINER')
def plan_delete(plan_id):
    """Delete a workout plan."""
    user_id = session.get('user_id')
    try:
        trainer = training_service.get_trainer_by_user_id(user_id)
        training_service.delete_workout_plan(plan_id, trainer.id)
        flash('Đã xóa kế hoạch tập.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('training.trainer_plans'))


# ── My Plans (MEMBER) ─────────────────────────────────────────────

@training_bp.route('/my-plans')
@login_required
def my_plans():
    """Member views their own workout plans."""
    if session.get('role') != 'MEMBER':
        flash('Chức năng dành cho hội viên.', 'warning')
        return redirect(url_for('auth.dashboard'))

    user_id = session.get('user_id')
    member = member_service.get_member_for_user(user_id)
    if member is None:
        flash('Không tìm thấy thông tin hội viên.', 'warning')
        return redirect(url_for('auth.dashboard'))

    plans = training_service.get_plans_for_member(member.id)
    return render_template('training/my_plans.html',
                           member=member, plans=plans)
