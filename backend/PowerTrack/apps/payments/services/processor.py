from decimal import Decimal
from django.db import transaction

from apps.billing.models import Bill
from apps.payments.models import Payment


@transaction.atomic
def record_payment(
    bill,
    amount,
    method,
    reference="",
):
    """
    Record a payment and immediately synchronize the bill balance.
    """
    if not isinstance(bill, Bill):
        raise TypeError("bill must be a Bill instance")

    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

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

    bill.amount_paid = sum(
        (payment.amount for payment in bill.payments.all()),
        Decimal("0.00"),
    )

    bill.save()

    return payment
