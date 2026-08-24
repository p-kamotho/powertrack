from django.utils import timezone

from apps.notifications.models import Notification


def create_bill_notification(bill):
    """
    Queue a notification when a bill is issued.
    """

    notification = Notification.objects.create(
        tenant=bill.tenant,
        bill=bill,
        channel="EMAIL",
        subject=f"PowerTrack Bill {bill.bill_number}",
        message=(
            f"Dear {bill.tenant.full_name},\n\n"
            f"Your electricity bill {bill.bill_number} "
            f"has been issued.\n\n"
            f"Consumption: {bill.consumption} kWh\n"
            f"Amount: KSh {bill.total_amount}\n"
            f"Balance: KSh {bill.balance}\n\n"
            f"Thank you for using PowerTrack."
        ),
        status="QUEUED",
    )

    return notification


def create_payment_notification(payment):
    """
    Queue a payment receipt notification.
    """

    bill = payment.bill

    return Notification.objects.create(
        tenant=bill.tenant,
        bill=bill,
        channel="EMAIL",
        subject=f"Payment Received - {bill.bill_number}",
        message=(
            f"Dear {bill.tenant.full_name},\n\n"
            f"We received your payment of "
            f"KSh {payment.amount}.\n\n"
            f"Bill: {bill.bill_number}\n"
            f"Reference: {payment.reference or 'N/A'}\n"
            f"Remaining balance: KSh {bill.balance}\n\n"
            f"Thank you."
        ),
        status="QUEUED",
    )


def create_overdue_notification(bill):
    """
    Queue an overdue bill notification.
    """

    return Notification.objects.create(
        tenant=bill.tenant,
        bill=bill,
        channel="EMAIL",
        subject=f"Overdue Bill - {bill.bill_number}",
        message=(
            f"Dear {bill.tenant.full_name},\n\n"
            f"Your bill {bill.bill_number} is overdue.\n\n"
            f"Outstanding balance: KSh {bill.balance}\n\n"
            f"Please make payment as soon as possible."
        ),
        status="QUEUED",
    )
