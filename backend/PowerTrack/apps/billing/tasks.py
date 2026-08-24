from celery import shared_task

from apps.billing.services.workflow import process_billing_period
from apps.readings.models import BillingPeriod
from apps.notifications.tasks import notify_bill


@shared_task
def process_billing_period_task(period_id):
    """
    Run the complete billing workflow for a billing period.
    """
    period = BillingPeriod.objects.get(pk=period_id)

    result = process_billing_period(period)

    for notification in result["notifications"]:
        notify_bill.delay(notification.pk)

    return {
        "period_id": period.pk,
        "bills_created": len(result["bills"]),
        "notifications_queued": len(result["notifications"]),
    }
