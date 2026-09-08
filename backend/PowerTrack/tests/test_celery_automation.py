from datetime import date
from decimal import Decimal

import pytest

from apps.billing.models import Bill
from apps.billing.tasks import process_overdue_bills_task
from apps.notifications.models import Notification


@pytest.mark.django_db
def test_overdue_task_marks_bill_overdue_and_queues_notification(
    tenant,
    reading,
    tariff,
):
    bill = Bill.objects.create(
        bill_number="PT-CELERY-001",
        tenant=tenant,
        reading=reading,
        billing_period=reading.billing_period,
        tariff=tariff,
        due_date=date(2026, 8, 1),
    )

    result = process_overdue_bills_task.apply().get()

    bill.refresh_from_db()

    assert bill.status == Bill.Status.OVERDUE
    assert bill.balance > Decimal("0.00")
    assert result["bills_marked_overdue"] == 1
    assert result["notifications_queued"] == 1

    notification = Notification.objects.get(bill=bill)

    assert notification.status == "QUEUED"
    assert notification.subject.startswith("Overdue Bill")


@pytest.mark.django_db
def test_overdue_task_does_not_duplicate_existing_overdue_notification(
    tenant,
    reading,
    tariff,
):
    bill = Bill.objects.create(
        bill_number="PT-CELERY-002",
        tenant=tenant,
        reading=reading,
        billing_period=reading.billing_period,
        tariff=tariff,
        due_date=date(2026, 8, 1),
    )

    first = process_overdue_bills_task.apply().get()
    second = process_overdue_bills_task.apply().get()

    assert first["bills_marked_overdue"] == 1
    assert second["bills_marked_overdue"] == 0

    assert Notification.objects.filter(bill=bill).count() == 1
