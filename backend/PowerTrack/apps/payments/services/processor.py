from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.billing.models import Bill
from apps.payments.models import Payment
from apps.notifications.models import Notification


@transaction.atomic
def record_payment(
    bill,
    amount,
    method,
    reference="",
):
    """
    Record a payment and immediately synchronize the bill balance.
    Returns a tuple of (payment, updated_bill).
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

    # Recalculate amount paid from all payments
    bill.amount_paid = sum(
        (p.amount for p in bill.payments.all()),
        Decimal("0.00"),
    )

    # Recalculate balance
    bill.balance = bill.total_amount - bill.amount_paid
    
    # Update status based on payment
    if bill.balance <= 0 and bill.total_amount > 0:
        bill.status = Bill.Status.PAID
    elif bill.amount_paid > 0:
        bill.status = Bill.Status.PARTIAL
    else:
        bill.status = Bill.Status.ISSUED

    bill.save()

    # Create payment notification
    tenant = bill.tenant
    Notification.objects.create(
        tenant=tenant,
        bill=bill,
        channel="EMAIL",
        subject=f"Payment Received - {bill.bill_number}",
        message=(
            f"Dear {tenant.full_name},\n\n"
            f"Payment of KSh {amount} has been received for "
            f"bill {bill.bill_number}.\n\n"
            f"Amount paid: KSh {bill.amount_paid}\n"
            f"Outstanding balance: KSh {bill.balance}\n\n"
            f"Thank you."
        ),
        status="QUEUED",
    )

    return payment, bill
