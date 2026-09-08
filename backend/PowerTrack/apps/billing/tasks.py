from celery import shared_task
from django.utils import timezone

from apps.billing.models import Bill
from apps.billing.services.workflow import process_billing_period
from apps.billing.services.lifecycle import mark_bill_overdue
from apps.notifications.services import queue_overdue_notification
from apps.notifications.tasks import process_notification
from apps.readings.models import BillingPeriod


@shared_task
def process_billing_period_task(period_id):
    period = BillingPeriod.objects.get(pk=period_id)

    result = process_billing_period(period)

    for notification in result["notifications"]:
        process_notification.delay(notification.pk)

    return {
        "period_id": period.pk,
        "bills_created": len(result["bills"]),
        "notifications_queued": len(result["notifications"]),
    }


@shared_task
def process_overdue_bills_task():
    today = timezone.localdate()

    bills = (
        Bill.objects
        .select_related("tenant")
        .filter(
            due_date__lt=today,
            balance__gt=0,
            status__in=[
                Bill.Status.ISSUED,
                Bill.Status.PARTIAL,
            ],
        )
    )

    processed = 0
    notifications = 0

    for bill in bills:
        previous_status = bill.status

        bill = mark_bill_overdue(bill)

        if (
            previous_status != Bill.Status.OVERDUE
            and bill.status == Bill.Status.OVERDUE
        ):
            notification = queue_overdue_notification(bill)
            process_notification.delay(notification.pk)

            processed += 1
            notifications += 1

    return {
        "date": str(today),
        "bills_marked_overdue": processed,
        "notifications_queued": notifications,
    }
