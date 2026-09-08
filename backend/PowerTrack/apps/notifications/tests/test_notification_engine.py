import pytest
from decimal import Decimal
from datetime import date

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.models import Bill
from apps.payments.models import Payment
from apps.notifications.models import Notification
from apps.notifications.services import (
    mark_notification_sent,
    queue_bill_notification,
    queue_overdue_notification,
    queue_payment_notification,
)


@pytest.fixture
def bill():
    property_obj = Property.objects.create(
        name="Notification Test Property"
    )

    room = Room.objects.create(
        property=property_obj,
        room_number="101",
    )

    tenant = Tenant.objects.create(
        first_name="Jane",
        last_name="Doe",
        phone_number="0712345678",
        room=room,
    )

    meter = Meter.objects.create(
        meter_number="MTR-NOTIFY-001",
        room=room,
    )

    period = BillingPeriod.objects.create(
        name="August 2026",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
    )

    reading = MeterReading.objects.create(
        meter=meter,
        billing_period=period,
        reading_date=date(2026, 8, 31),
        previous_reading=Decimal("100"),
        current_reading=Decimal("150"),
    )

    tariff = Tariff.objects.create(
        name="Standard",
        rate_per_kwh=Decimal("20.00"),
        effective_from=date(2026, 1, 1),
    )

    return Bill.objects.create(
        bill_number="BILL-NOTIFY-001",
        tenant=tenant,
        reading=reading,
        billing_period=period,
        tariff=tariff,
    )


@pytest.mark.django_db
def test_bill_notification_is_queued(bill):
    notification = queue_bill_notification(bill)

    assert notification.tenant == bill.tenant
    assert notification.bill == bill
    assert notification.channel == "EMAIL"
    assert notification.status == "QUEUED"
    assert notification.sent_at is None
    assert bill.bill_number in notification.subject
    assert "electricity bill" in notification.message


@pytest.mark.django_db
def test_payment_notification_is_queued(bill):
    payment = Payment.objects.create(
        bill=bill,
        amount=Decimal("500.00"),
        method=Payment.Method.MPESA,
        reference="MPESA-NOTIFY-001",
    )

    notification = queue_payment_notification(payment)

    assert notification.tenant == bill.tenant
    assert notification.bill == bill
    assert notification.status == "QUEUED"
    assert notification.channel == "EMAIL"
    assert "Payment Received" in notification.subject
    assert "MPESA-NOTIFY-001" in notification.message


@pytest.mark.django_db
def test_overdue_notification_is_queued(bill):
    notification = queue_overdue_notification(bill)

    assert notification.tenant == bill.tenant
    assert notification.bill == bill
    assert notification.status == "QUEUED"
    assert "Overdue Bill" in notification.subject
    assert "Outstanding balance" in notification.message


@pytest.mark.django_db
def test_notification_can_be_marked_sent(bill):
    notification = queue_bill_notification(bill)

    assert notification.sent_at is None

    mark_notification_sent(notification)

    notification.refresh_from_db()

    assert notification.status == "SENT"
    assert notification.sent_at is not None


@pytest.mark.django_db
def test_multiple_notifications_can_exist_for_same_bill(bill):
    first = queue_bill_notification(bill)
    second = queue_overdue_notification(bill)

    assert first.pk != second.pk
    assert Notification.objects.filter(bill=bill).count() == 2


@pytest.mark.django_db
def test_payment_notification_contains_updated_balance(bill):
    payment = Payment.objects.create(
        bill=bill,
        amount=Decimal("500.00"),
        method=Payment.Method.CASH,
        reference="CASH-NOTIFY-001",
    )

    bill.amount_paid = Decimal("500.00")
    bill.balance = Decimal("500.00")
    bill.status = Bill.Status.PARTIAL
    bill.save()

    notification = queue_payment_notification(payment)

    assert "KSh 500.00" in notification.message
    assert "Reference: CASH-NOTIFY-001" in notification.message
