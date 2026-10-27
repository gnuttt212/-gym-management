"""Seed data script – populates the database with initial data.

Creates:
    - 5 user accounts (1 per role): admin, receptionist, trainer, cashier, member
    - 1 trainer record linked to TRAINER user
    - 4 membership plans (1/3/6/12 months)
    - 10 sample exercises
    - Default settings (max_days_per_week)

Usage:
    python -m seeds.seed
"""

import sys
import os

# Ensure project root is in path when running as script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.trainer import Trainer
from app.models.membership_plan import MembershipPlan
from app.models.exercise import Exercise
from app.models.setting import Setting


def seed():
    """Insert seed data into database."""
    print('Seeding database...')

    # ── Users (password: 123456 for all) ──────────────────────────────────
    users_data = [
        {'username': 'admin', 'role': 'ADMIN'},
        {'username': 'receptionist', 'role': 'RECEPTIONIST'},
        {'username': 'trainer01', 'role': 'TRAINER'},
        {'username': 'cashier', 'role': 'CASHIER'},
        {'username': '0901234567', 'role': 'MEMBER'},
    ]

    created_users = {}
    for data in users_data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            print(f"  [SKIP] User '{data['username']}' already exists.")
            created_users[data['role']] = existing
            continue

        user = User(username=data['username'], role=data['role'])
        user.set_password('123456')
        db.session.add(user)
        created_users[data['role']] = user
        print(f"  [ADD] User '{data['username']}' ({data['role']})")

    db.session.flush()  # Get IDs for trainer FK

    # ── Trainer record ────────────────────────────────────────────────────
    trainer_user = created_users.get('TRAINER')
    if trainer_user:
        existing = Trainer.query.filter_by(user_id=trainer_user.id).first()
        if not existing:
            trainer = Trainer(user_id=trainer_user.id, full_name='Nguyễn Văn HLV')
            db.session.add(trainer)
            print("  [ADD] Trainer 'Nguyễn Văn HLV'")
        else:
            print("  [SKIP] Trainer already exists.")

    # ── Membership Plans ──────────────────────────────────────────────────
    plans_data = [
        {'name': 'Gói 1 tháng',  'duration_months': 1,  'price': 500000},
        {'name': 'Gói 3 tháng',  'duration_months': 3,  'price': 1200000},
        {'name': 'Gói 6 tháng',  'duration_months': 6,  'price': 2000000},
        {'name': 'Gói 12 tháng', 'duration_months': 12, 'price': 3500000},
    ]

    for data in plans_data:
        existing = MembershipPlan.query.filter_by(
            duration_months=data['duration_months']
        ).first()
        if existing:
            print(f"  [SKIP] Plan '{data['name']}' already exists.")
            continue

        plan = MembershipPlan(**data)
        db.session.add(plan)
        print(f"  [ADD] Plan '{data['name']}' – {data['price']:,.0f}đ")

    # ── Exercises ─────────────────────────────────────────────────────────
    exercises_data = [
        'Bench Press',
        'Squat',
        'Deadlift',
        'Overhead Press',
        'Barbell Row',
        'Pull-up',
        'Dumbbell Curl',
        'Tricep Pushdown',
        'Leg Press',
        'Plank',
    ]

    for name in exercises_data:
        existing = Exercise.query.filter_by(name=name).first()
        if existing:
            print(f"  [SKIP] Exercise '{name}' already exists.")
            continue

        exercise = Exercise(name=name)
        db.session.add(exercise)
        print(f"  [ADD] Exercise '{name}'")

    # ── Settings ──────────────────────────────────────────────────────────
    settings_data = [
        {'key': 'max_days_per_week', 'value': '6'},
    ]

    for data in settings_data:
        existing = Setting.query.filter_by(key=data['key']).first()
        if existing:
            print(f"  [SKIP] Setting '{data['key']}' already exists.")
            continue

        setting = Setting(**data)
        db.session.add(setting)
        print(f"  [ADD] Setting '{data['key']}' = '{data['value']}'")

    # ── Commit all ────────────────────────────────────────────────────────
    db.session.commit()
    print('\nSeed completed successfully!')


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed()
