"""Member routes – member CRUD for ADMIN and RECEPTIONIST."""

from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.auth.decorators import roles_required
from app.extensions import db
from app.members.service import MemberService
from app.subscriptions.service import SubscriptionService

members_bp = Blueprint('members', __name__, url_prefix='/members')

member_service = MemberService()
sub_service = SubscriptionService()


@members_bp.route('/')
@roles_required('ADMIN', 'RECEPTIONIST')
def member_list():
    """List all members with search."""
    keyword = request.args.get('q', '').strip()
    if keyword:
        members = member_service.search_members(keyword)
    else:
        members = member_service.get_all_members()

    # Check active status for each member
    members_data = []
    for m in members:
        is_active = sub_service.is_member_active(m.id)
        members_data.append({'member': m, 'is_active': is_active})

    return render_template('members/list.html',
                           members_data=members_data, keyword=keyword)


@members_bp.route('/<int:member_id>')
@roles_required('ADMIN', 'RECEPTIONIST')
def member_detail(member_id):
    """View member detail with subscriptions and invoices."""
    try:
        member = member_service.get_member_by_id(member_id)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('members.member_list'))

    active_sub = sub_service.get_active_subscription(member_id)
    subscriptions = sub_service.get_member_subscriptions(member_id)

    return render_template('members/detail.html',
                           member=member, active_sub=active_sub,
                           subscriptions=subscriptions,
                           today=date.today())


@members_bp.route('/<int:member_id>/edit', methods=['GET', 'POST'])
@roles_required('ADMIN', 'RECEPTIONIST')
def member_edit(member_id):
    """Edit member information."""
    try:
        member = member_service.get_member_by_id(member_id)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('members.member_list'))

    if request.method == 'POST':
        data = {
            'full_name': request.form.get('full_name', '').strip(),
            'gender': request.form.get('gender'),
            'birth_year': int(request.form.get('birth_year', 0)),
            'email': request.form.get('email', '').strip() or None,
        }
        # Handle trainer assignment
        trainer_id = request.form.get('trainer_id')
        if trainer_id:
            data['trainer_id'] = int(trainer_id)
        else:
            data['trainer_id'] = None

        try:
            member_service.update_member(member_id, data)
            db.session.commit()
            flash('Cập nhật hội viên thành công!', 'success')
            return redirect(url_for('members.member_detail', member_id=member_id))
        except (ValueError, Exception) as e:
            db.session.rollback()
            flash(str(e), 'danger')

    from app.models.trainer import Trainer
    trainers = Trainer.query.all()
    return render_template('members/edit.html', member=member, trainers=trainers)
