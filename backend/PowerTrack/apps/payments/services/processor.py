from decimal import Decimal, InvalidOperation

from django.db import transaction

from apps.billing.models import Bill
from apps.payments.models import Payment
from apps.notifications.services import queue_payment_notification


@transaction.atomic
def record_payment(
    bill,
    amount,
    method,
    reference="",
):
    """
    Record a payment against a bill.

    This is the authoritative payment transaction service.

    Returns:
        tuple: (payment, updated_bill)
    """

    if not isinstance(bill, Bill):
        raise TypeError("bill must be a Bill instance")

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid payment amount.")

    if amount <= Decimal("0.00"):
        raise ValueError("Payment amount must be greater than zero.")

    # Lock the bill so concurrent payment requests cannot
    # modify the same financial record simultaneously.
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

    # Recalculate the total amount paid from the payment ledger.
    bill.amount_paid = sum(
        (payment.amount for payment in bill.payments.all()),
        Decimal("0.00"),
    )

    # Recalculate outstanding balance.
    bill.balance = max(
        Decimal("0.00"),
        bill.total_amount - bill.amount_paid,
    )

    # Determine the bill's financial status.
    if bill.balance <= Decimal("0.00") and bill.total_amount > Decimal("0.00"):
        bill.status = Bill.Status.PAID
    elif bill.amount_paid > Decimal("0.00"):
        bill.status = Bill.Status.PARTIAL
    else:
        bill.status = Bill.Status.ISSUED

    bill.save()

    # Queue payment notification.
    queue_payment_notification(payment)

    return payment, bill
