from django.db import transaction

from apps.billing.services.calculator import generate_period_bills
from apps.notifications.services import queue_bill_notification


@transaction.atomic
def process_billing_period(period, tariff=None, due_date=None):
    """
    Complete the server-side monthly billing workflow.

    Reading
        -> Bill
        -> Notification
    """
    bills = generate_period_bills(
        period,
        tariff=tariff,
        due_date=due_date,
    )

    notifications = []

    for bill in bills:
        notifications.append(
            queue_bill_notification(bill)
        )

    return {
        "period": period,
        "bills": bills,
        "notifications": notifications,
    }
