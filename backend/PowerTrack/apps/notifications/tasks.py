from celery import shared_task

from apps.notifications.models import Notification
from apps.notifications.services import mark_notification_sent


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def notify_bill(self, notification_id):
    """
    Process a queued bill notification.

    This implementation marks the notification as sent.
    Real email/SMS provider integration can be connected later.
    """
    notification = Notification.objects.get(
        pk=notification_id
    )

    if notification.status == "SENT":
        return notification_id

    mark_notification_sent(notification)

    return notification_id
