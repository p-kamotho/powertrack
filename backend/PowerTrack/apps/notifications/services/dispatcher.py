from django.utils import timezone

from apps.notifications.models import Notification


def queue_bill_notification(bill, channel="EMAIL"):
    """
    Create a queued notification for a newly issued bill.
    """
    tenant = bill.tenant

    return Notification.objects.create(
        tenant=tenant,
        bill=bill,
        channel=channel,
        subject=f"PowerTrack Bill {bill.bill_number}",
        message=(
            f"Dear {tenant.full_name},\n\n"
            f"Your electricity bill for {bill.billing_period.name} "
            f"is ready.\n\n"
            f"Consumption: {bill.consumption} kWh\n"
            f"Total: KSh {bill.total_amount}\n"
            f"Amount paid: KSh {bill.amount_paid}\n"
            f"Balance: KSh {bill.balance}\n\n"
            f"Thank you."
        ),
        status="QUEUED",
    )


def queue_payment_notification(payment, channel="EMAIL"):
    """
    Create a queued notification for a successful payment.
    """
    bill = payment.bill
    tenant = bill.tenant

    return Notification.objects.create(
        tenant=tenant,
        bill=bill,
        channel=channel,
        subject=f"Payment Received - {bill.bill_number}",
        message=(
            f"Dear {tenant.full_name},\n\n"
            f"Payment of KSh {payment.amount} has been received "
            f"for bill {bill.bill_number}.\n\n"
            f"Amount paid: KSh {bill.amount_paid}\n"
            f"Outstanding balance: KSh {bill.balance}\n"
            f"Reference: {payment.reference or 'N/A'}\n\n"
            f"Thank you."
        ),
        status="QUEUED",
    )


def queue_overdue_notification(bill, channel="EMAIL"):
    """
    Create a queued notification for an overdue bill.
    """
    tenant = bill.tenant

    return Notification.objects.create(
        tenant=tenant,
        bill=bill,
        channel=channel,
        subject=f"Overdue Bill - {bill.bill_number}",
        message=(
            f"Dear {tenant.full_name},\n\n"
            f"Your bill {bill.bill_number} is overdue.\n\n"
            f"Outstanding balance: KSh {bill.balance}\n\n"
            f"Please make payment as soon as possible."
        ),
        status="QUEUED",
    )


def mark_notification_sent(notification):
    """
    Mark a successfully processed notification as sent.
    """
    notification.status = "SENT"
    notification.sent_at = timezone.now()
    notification.save(
        update_fields=["status", "sent_at"]
    )

    return notification
