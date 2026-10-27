"""Setting model – key-value configuration store.

Examples:
    max_days_per_week = 6
"""

from app.extensions import db


class Setting(db.Model):
    __tablename__ = 'settings'

    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        return f'<Setting {self.key}={self.value}>'
