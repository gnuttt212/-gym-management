"""Exercise model – catalog of gym exercises.

Soft delete: is_active=False (exercise may be referenced in existing workout plans).
"""

from app.extensions import db


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f'<Exercise {self.name} active={self.is_active}>'
