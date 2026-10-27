"""Invoice model – one invoice per subscription.

BR2: price_snapshot captures the plan price AT THE TIME of creation.
     Changing plan prices does NOT affect existing invoices.
"""

from app.extensions import db
from datetime import datetime, timezone


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subscription_id = db.Column(
        db.Integer, db.ForeignKey('subscriptions.id'), nullable=False, unique=True
    )

    # BR2: Snapshot of the plan price when invoice was created
    price_snapshot = db.Column(db.Numeric(12, 0), nullable=False)

    status = db.Column(
        db.Enum('UNPAID', 'PAID', name='invoice_status'),
        default='UNPAID', nullable=False
    )
    payment_method = db.Column(
        db.Enum('CASH', 'TRANSFER', name='payment_method_enum'),
        nullable=True  # NULL until payment is confirmed
    )
    paid_at = db.Column(db.DateTime, nullable=True)
    cashier_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True
    )

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    cashier = db.relationship('User', foreign_keys=[cashier_id])

    def __repr__(self) -> str:
        return f'<Invoice #{self.id} {self.status} {self.price_snapshot}VND>'
