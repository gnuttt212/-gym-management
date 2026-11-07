"""Billing service – business logic for invoices and payments.

BR2: Invoice stores price_snapshot (plan price at creation time).
     Changing plan prices does NOT affect existing invoices.

Payment rules:
    - Only CASHIER can confirm payment.
    - payment_method must be CASH or TRANSFER.
    - Invoice already PAID cannot be paid again.
"""

from app.extensions import db
from app.models.invoice import Invoice
from app.billing.repository import InvoiceRepository


class BillingService:
    """Handles invoice and payment business logic."""

    def __init__(self, invoice_repo: InvoiceRepository | None = None):
        self.invoice_repo = invoice_repo or InvoiceRepository()

    def create_invoice(self, subscription_id: int,
                       price_snapshot: float) -> Invoice:
        """Create an invoice for a subscription.

        BR2: Captures the plan price at the time of creation.
        Note: Does NOT commit – caller handles transaction.
        """
        return self.invoice_repo.create(subscription_id, price_snapshot)

    def get_invoice_by_id(self, invoice_id: int) -> Invoice:
        """Get an invoice or raise ValueError."""
        invoice = self.invoice_repo.find_by_id(invoice_id)
        if invoice is None:
            raise ValueError('Hóa đơn không tồn tại.')
        return invoice

    def get_all_invoices(self) -> list[Invoice]:
        """Return all invoices."""
        return self.invoice_repo.find_all()

    def get_unpaid_invoices(self) -> list[Invoice]:
        """Return all unpaid invoices."""
        return self.invoice_repo.find_unpaid()

    def get_member_invoices(self, member_id: int) -> list[Invoice]:
        """Return all invoices for a specific member."""
        return self.invoice_repo.find_by_member(member_id)

    def confirm_payment(self, invoice_id: int, payment_method: str,
                        cashier_id: int) -> Invoice:
        """Confirm payment for an invoice.

        Args:
            invoice_id: The invoice to pay.
            payment_method: 'CASH' or 'TRANSFER'.
            cashier_id: The user ID of the cashier confirming payment.

        Raises:
            ValueError: If invoice not found, already paid, or invalid method.
        """
        invoice = self.get_invoice_by_id(invoice_id)

        # Cannot pay an already-paid invoice
        if invoice.status == 'PAID':
            raise ValueError('Hóa đơn này đã được thanh toán.')

        # Validate payment method
        if payment_method not in ('CASH', 'TRANSFER'):
            raise ValueError('Phương thức thanh toán không hợp lệ (CASH hoặc TRANSFER).')

        # Mark as paid (does NOT commit)
        self.invoice_repo.mark_paid(invoice, payment_method, cashier_id)
        db.session.commit()
        return invoice
