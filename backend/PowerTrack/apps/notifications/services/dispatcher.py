from django.utils import timezone

from apps.notifications.models import Notification


def queue_bill_notification(bill, channel="EMAIL"):
    """
    Create a queued notification for a newly generated bill.
    """
    tenant = bill.tenant

    notification = Notification.objects.create(
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

    return notification


def mark_notification_sent(notification):
    notification.status = "SENT"
    notification.sent_at = timezone.now()
    notification.save(
        update_fields=["status", "sent_at"]
    )

    return notification
