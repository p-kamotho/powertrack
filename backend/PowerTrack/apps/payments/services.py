from decimal import Decimal, InvalidOperation

from django.db import transaction

from apps.billing.models import Bill
from apps.payments.models import Payment
from apps.notifications.services import create_payment_notification


@transaction.atomic
def record_payment(
    *,
    bill,
    amount,
    method,
    reference="",
):
    """
    Record a payment against a bill.

    This is the single authoritative transaction path for payments.
    """

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid payment amount.")

    if amount <= Decimal("0.00"):
        raise ValueError("Payment amount must be greater than zero.")

    bill = (
        Bill.objects
        .select_for_update()
        .get(pk=bill.pk)
    )

    if bill.status == Bill.Status.CANCELLED:
        raise ValueError("Cannot pay a cancelled bill.")

    if bill.balance <= Decimal("0.00"):
        raise ValueError("Bill has no outstanding balance.")

    if amount > bill.balance:
        raise ValueError(
            f"Payment exceeds outstanding balance of {bill.balance}."
        )

    payment = Payment.objects.create(
        bill=bill,
        amount=amount,
        method=method,
        reference=reference,
    )

    bill.amount_paid += amount
    bill.save()

    create_payment_notification(payment)

    return payment, bill
