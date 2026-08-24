from celery import shared_task
@shared_task
def notify_bill(notification_id): return notification_id
