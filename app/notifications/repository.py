"""Email log repository – data access for email_logs table."""

from app.extensions import db
from app.models.email_log import EmailLog


class EmailLogRepository:
    """Handles all database queries related to EmailLog."""

    def create(self, to_email: str, subject: str, body: str = '') -> EmailLog:
        """Create a new email log entry with status PENDING.

        Note: Does NOT commit – caller handles transaction.
        """
        log = EmailLog(to_email=to_email, subject=subject, body=body)
        db.session.add(log)
        return log

    def update_status(self, log_id: int, status: str) -> None:
        """Update email log status (PENDING -> SENT or FAILED)."""
        log = db.session.get(EmailLog, log_id)
        if log:
            log.status = status
            if status == 'FAILED':
                log.retry_count += 1
            db.session.commit()

    def find_pending(self, limit: int = 10) -> list[EmailLog]:
        """Find pending emails for retry."""
        return EmailLog.query.filter_by(status='PENDING').limit(limit).all()

    def find_failed(self, max_retries: int = 3, limit: int = 10) -> list[EmailLog]:
        """Find failed emails that can be retried."""
        return EmailLog.query.filter(
            EmailLog.status == 'FAILED',
            EmailLog.retry_count < max_retries
        ).limit(limit).all()
