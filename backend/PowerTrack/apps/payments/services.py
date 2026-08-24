from decimal import Decimal

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
    amount = Decimal(str(amount))

    if amount <= Decimal("0.00"):
        raise ValueError("Payment amount must be greater than zero.")

    bill = (
        Bill.objects
        .select_for_update()
        .get(pk=bill.pk)
    )

    if bill.status == Bill.Status.CANCELLED:
        raise ValueError("Cannot pay a cancelled bill.")

    # Calculate new balance
    new_balance = bill.balance - amount
    if new_balance < 0:
        raise ValueError(
            f"Payment exceeds outstanding balance of {bill.balance}."
        )

    payment = Payment.objects.create(
        bill=bill,
        amount=amount,
        method=method,
        reference=reference,
    )

    # Update bill amount paid and save (triggers recalculation of balance and status)
    bill.amount_paid += amount
    bill.save()  # This will recalculate balance and status in the save() method

    create_payment_notification(payment)

    return payment, bill