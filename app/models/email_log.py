"""EmailLog model – tracks outgoing email attempts.

BR5: Failed email must NOT cancel registration.
     Emails are sent asynchronously; this table logs status for retry.
"""

from app.extensions import db
from datetime import datetime, timezone


class EmailLog(db.Model):
    __tablename__ = 'email_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    to_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum('PENDING', 'SENT', 'FAILED', name='email_status'),
        default='PENDING', nullable=False
    )
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f'<EmailLog to={self.to_email} status={self.status}>'
