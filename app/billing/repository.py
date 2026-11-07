"""Invoice repository – data access for invoices table."""

from datetime import datetime, timezone

from app.extensions import db
from app.models.invoice import Invoice


class InvoiceRepository:
    """Handles all database queries related to Invoice."""

    def find_by_id(self, invoice_id: int) -> Invoice | None:
        """Find an invoice by primary key."""
        return db.session.get(Invoice, invoice_id)

    def find_by_subscription(self, subscription_id: int) -> Invoice | None:
        """Find the invoice for a subscription."""
        return Invoice.query.filter_by(subscription_id=subscription_id).first()

    def find_by_member(self, member_id: int) -> list[Invoice]:
        """Find all invoices for a member (via subscriptions)."""
        from app.models.subscription import Subscription
        return Invoice.query.join(Subscription).filter(
            Subscription.member_id == member_id
        ).order_by(Invoice.created_at.desc()).all()

    def find_unpaid(self) -> list[Invoice]:
        """Find all unpaid invoices."""
        return Invoice.query.filter_by(status='UNPAID') \
            .order_by(Invoice.created_at.desc()).all()

    def find_all(self) -> list[Invoice]:
        """Return all invoices (newest first)."""
        return Invoice.query.order_by(Invoice.created_at.desc()).all()

    def create(self, subscription_id: int, price_snapshot: float) -> Invoice:
        """Create a new invoice with status UNPAID.

        BR2: price_snapshot captures the plan price at creation time.
        Note: Does NOT commit – caller handles transaction.
        """
        invoice = Invoice(
            subscription_id=subscription_id,
            price_snapshot=price_snapshot,
            status='UNPAID'
        )
        db.session.add(invoice)
        return invoice

    def mark_paid(self, invoice: Invoice, payment_method: str,
                  cashier_id: int) -> Invoice:
        """Mark an invoice as PAID.

        Note: Does NOT commit – caller handles transaction.
        """
        invoice.status = 'PAID'
        invoice.payment_method = payment_method
        invoice.cashier_id = cashier_id
        invoice.paid_at = datetime.now(timezone.utc)
        return invoice
