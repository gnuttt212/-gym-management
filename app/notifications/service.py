"""Email notification service.

BR5: Email failures must NOT cancel registration.
     Emails are sent asynchronously via threading.
     All attempts are logged in email_logs table (PENDING -> SENT/FAILED).

Architecture:
    EmailSender (abstract) -> SmtpEmailSender (production)
                           -> FakeEmailSender (testing)
"""

import threading
from abc import ABC, abstractmethod

from flask import current_app
from flask_mail import Message

from app.extensions import db, mail
from app.notifications.repository import EmailLogRepository


class EmailSender(ABC):
    """Abstract interface for sending emails (Dependency Inversion)."""

    @abstractmethod
    def send(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email. Returns True on success, False on failure."""
        ...


class SmtpEmailSender(EmailSender):
    """Send emails via Flask-Mail (SMTP)."""

    def send(self, to_email: str, subject: str, body: str) -> bool:
        """Send email via SMTP."""
        try:
            msg = Message(subject=subject, recipients=[to_email], html=body)
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f'SMTP send failed: {e}')
            return False


class FakeEmailSender(EmailSender):
    """Fake email sender for testing – just logs the attempt."""

    def __init__(self):
        self.sent_emails: list[dict] = []

    def send(self, to_email: str, subject: str, body: str) -> bool:
        """Simulate sending – always succeeds."""
        self.sent_emails.append({
            'to': to_email, 'subject': subject, 'body': body
        })
        return True


class NotificationService:
    """Handles email notifications asynchronously.

    BR5: Email is sent in a background thread. Failure is logged
    but does NOT affect the calling transaction (e.g. registration).
    """

    def __init__(self, email_sender: EmailSender | None = None,
                 email_log_repo: EmailLogRepository | None = None):
        self.email_sender = email_sender or SmtpEmailSender()
        self.email_log_repo = email_log_repo or EmailLogRepository()

    def send_registration_email(self, to_email: str, member_name: str,
                                plan_name: str, start_date: str,
                                end_date: str, price: str) -> None:
        """Send registration confirmation email asynchronously.

        BR5: Creates email_log (PENDING), then sends in background thread.
        On success -> SENT, on failure -> FAILED (retry_count incremented).
        """
        subject = 'Xác nhận đăng ký – GYM Manager'
        body = f"""
        <h2>Chào {member_name},</h2>
        <p>Bạn đã đăng ký thành công tại phòng tập GYM Manager!</p>
        <table border="1" cellpadding="8" style="border-collapse: collapse;">
            <tr><td><strong>Gói tập</strong></td><td>{plan_name}</td></tr>
            <tr><td><strong>Ngày bắt đầu</strong></td><td>{start_date}</td></tr>
            <tr><td><strong>Ngày hết hạn</strong></td><td>{end_date}</td></tr>
            <tr><td><strong>Số tiền</strong></td><td>{price}</td></tr>
        </table>
        <p>Vui lòng thanh toán tại quầy thu ngân.</p>
        <p>Trân trọng,<br>GYM Manager</p>
        """

        # Create log entry BEFORE sending (in caller's transaction)
        log = self.email_log_repo.create(to_email, subject, body)
        db.session.flush()  # Get log.id
        log_id = log.id

        # Send asynchronously in background thread (BR5)
        self._send_async(log_id, to_email, subject, body)

    def _send_async(self, log_id: int, to_email: str,
                    subject: str, body: str) -> None:
        """Send email in a background thread.

        BR5: Uses a copy of the Flask app context so the main
        request thread is not blocked and not affected by failures.
        """
        # Get app reference before spawning thread
        app = current_app._get_current_object()

        def _do_send():
            with app.app_context():
                success = self.email_sender.send(to_email, subject, body)
                status = 'SENT' if success else 'FAILED'
                self.email_log_repo.update_status(log_id, status)
                app.logger.info(
                    f'Email to {to_email}: {status} (log_id={log_id})'
                )

        thread = threading.Thread(target=_do_send, daemon=True)
        thread.start()
