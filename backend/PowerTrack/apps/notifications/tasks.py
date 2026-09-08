from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from apps.notifications.models import Notification
from apps.notifications.services import mark_notification_sent


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def process_notification(self, notification_id):
    notification = Notification.objects.select_related("tenant").get(
        pk=notification_id
    )

    if notification.status == "SENT":
        return notification_id

    if notification.status != "QUEUED":
        return notification_id

    if notification.channel == "EMAIL":
        recipient = notification.tenant.email

        if recipient:
            send_mail(
                subject=notification.subject,
                message=notification.message,
                from_email=None,
                recipient_list=[recipient],
                fail_silently=False,
            )

    mark_notification_sent(notification)

    return notification_id
