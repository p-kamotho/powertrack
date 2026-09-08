import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.billing.models import Bill
from apps.billing.services.lifecycle import (
    cancel_bill,
    mark_bill_overdue,
    transition_bill_status,
)
from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff


@pytest.fixture
def bill():
    property_obj = Property.objects.create(
        name="Lifecycle Property",
        address="Test Address",
    )

    room = Room.objects.create(
        property=property_obj,
        room_number="201",
        floor="2",
    )

    tenant = Tenant.objects.create(
        first_name="Lifecycle",
        last_name="Tenant",
        phone_number="0711111111",
        room=room,
    )

    meter = Meter.objects.create(
        meter_number="LIFE-MTR-001",
        room=room,
        initial_reading=Decimal("100"),
    )

    period = BillingPeriod.objects.create(
        name="Lifecycle August 2026",
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
        name="Lifecycle Tariff",
        rate_per_kwh=Decimal("25.00"),
        effective_from=date(2026, 1, 1),
    )

    return Bill.objects.create(
        bill_number="LIFE-BILL-001",
        tenant=tenant,
        reading=reading,
        billing_period=period,
        tariff=tariff,
        due_date=date.today() + timedelta(days=10),
    )


@pytest.mark.django_db
def test_issued_to_partial_requires_payment(bill):
    bill.amount_paid = Decimal("500.00")
    bill.save()

    updated = transition_bill_status(
        bill,
        Bill.Status.PARTIAL,
    )

    assert updated.status == Bill.Status.PARTIAL


@pytest.mark.django_db
def test_issued_to_paid_requires_zero_balance(bill):
    bill.amount_paid = bill.total_amount
    bill.save()

    updated = transition_bill_status(
        bill,
        Bill.Status.PAID,
    )

    assert updated.status == Bill.Status.PAID
    assert updated.balance == Decimal("0.00")


@pytest.mark.django_db
def test_cannot_mark_unpaid_bill_as_paid(bill):
    with pytest.raises(
        ValueError,
        match="outstanding balance",
    ):
        transition_bill_status(
            bill,
            Bill.Status.PAID,
        )


@pytest.mark.django_db
def test_bill_becomes_overdue_after_due_date(bill):
    bill.due_date = date.today() - timedelta(days=1)
    bill.save()

    updated = mark_bill_overdue(bill)

    assert updated.status == Bill.Status.OVERDUE


@pytest.mark.django_db
def test_bill_cannot_be_overdue_before_due_date(bill):
    with pytest.raises(
        ValueError,
        match="before its due date",
    ):
        transition_bill_status(
            bill,
            Bill.Status.OVERDUE,
        )


@pytest.mark.django_db
def test_paid_bill_cannot_become_overdue(bill):
    bill.amount_paid = bill.total_amount
    bill.save()

    with pytest.raises(ValueError):
        transition_bill_status(
            bill,
            Bill.Status.OVERDUE,
        )


@pytest.mark.django_db
def test_cancelled_bill_is_terminal(bill):
    cancel_bill(bill)

    bill.refresh_from_db()

    assert bill.status == Bill.Status.CANCELLED

    with pytest.raises(ValueError):
        transition_bill_status(
            bill,
            Bill.Status.ISSUED,
        )


@pytest.mark.django_db
def test_paid_bill_is_terminal(bill):
    bill.amount_paid = bill.total_amount
    bill.save()

    transition_bill_status(
        bill,
        Bill.Status.PAID,
    )

    with pytest.raises(ValueError):
        transition_bill_status(
            bill,
            Bill.Status.PARTIAL,
        )


@pytest.mark.django_db
def test_bill_with_payment_cannot_be_cancelled(bill):
    bill.amount_paid = Decimal("100.00")
    bill.save()

    with pytest.raises(
        ValueError,
        match="recorded payments",
    ):
        cancel_bill(bill)


@pytest.mark.django_db
def test_overdue_bill_can_be_paid(bill):
    bill.due_date = date.today() - timedelta(days=1)
    bill.save()

    mark_bill_overdue(bill)

    bill.refresh_from_db()

    assert bill.status == Bill.Status.OVERDUE

    bill.amount_paid = bill.total_amount
    bill.save()

    updated = transition_bill_status(
        bill,
        Bill.Status.PAID,
    )

    assert updated.status == Bill.Status.PAID
