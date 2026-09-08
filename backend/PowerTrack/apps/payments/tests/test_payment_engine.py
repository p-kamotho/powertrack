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
from apps.payments.services import record_payment


@pytest.fixture
def bill():
    property_obj = Property.objects.create(
        name="Test Property",
    )

    room = Room.objects.create(
        property=property_obj,
        room_number="101",
    )

    tenant = Tenant.objects.create(
        first_name="John",
        last_name="Doe",
        phone_number="0712345678",
        room=room,
    )

    meter = Meter.objects.create(
        meter_number="MTR-TEST-001",
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
        bill_number="BILL-TEST-001",
        tenant=tenant,
        reading=reading,
        billing_period=period,
        tariff=tariff,
    )


@pytest.mark.django_db
def test_partial_payment_updates_bill(bill):
    payment, updated_bill = record_payment(
        bill=bill,
        amount=Decimal("500.00"),
        method=Payment.Method.MPESA,
        reference="MPESA-TEST-001",
    )

    updated_bill.refresh_from_db()

    assert payment.amount == Decimal("500.00")
    assert updated_bill.amount_paid == Decimal("500.00")
    assert updated_bill.balance == Decimal("500.00")
    assert updated_bill.status == Bill.Status.PARTIAL


@pytest.mark.django_db
def test_multiple_payments_complete_bill(bill):
    first_payment, updated_bill = record_payment(
        bill=bill,
        amount=Decimal("500.00"),
        method=Payment.Method.MPESA,
        reference="MPESA-TEST-001",
    )

    second_payment, updated_bill = record_payment(
        bill=updated_bill,
        amount=Decimal("500.00"),
        method=Payment.Method.CASH,
        reference="CASH-TEST-001",
    )

    updated_bill.refresh_from_db()

    assert first_payment.amount == Decimal("500.00")
    assert second_payment.amount == Decimal("500.00")

    assert Payment.objects.filter(bill=updated_bill).count() == 2
    assert updated_bill.amount_paid == Decimal("1000.00")
    assert updated_bill.balance == Decimal("0.00")
    assert updated_bill.status == Bill.Status.PAID


@pytest.mark.django_db
def test_zero_payment_rejected(bill):
    with pytest.raises(ValueError, match="greater than zero"):
        record_payment(
            bill=bill,
            amount=Decimal("0.00"),
            method=Payment.Method.CASH,
        )

    assert Payment.objects.count() == 0


@pytest.mark.django_db
def test_negative_payment_rejected(bill):
    with pytest.raises(ValueError, match="greater than zero"):
        record_payment(
            bill=bill,
            amount=Decimal("-100.00"),
            method=Payment.Method.CASH,
        )

    assert Payment.objects.count() == 0


@pytest.mark.django_db
def test_overpayment_rejected(bill):
    with pytest.raises(ValueError, match="exceeds outstanding balance"):
        record_payment(
            bill=bill,
            amount=Decimal("1001.00"),
            method=Payment.Method.CASH,
        )

    bill.refresh_from_db()

    assert Payment.objects.count() == 0
    assert bill.amount_paid == Decimal("0.00")
    assert bill.balance == Decimal("1000.00")
    assert bill.status == Bill.Status.ISSUED


@pytest.mark.django_db
def test_cancelled_bill_cannot_be_paid(bill):
    bill.status = Bill.Status.CANCELLED
    bill.save(update_fields=["status"])

    with pytest.raises(ValueError, match="cancelled bill"):
        record_payment(
            bill=bill,
            amount=Decimal("100.00"),
            method=Payment.Method.CASH,
        )

    assert Payment.objects.count() == 0


@pytest.mark.django_db
def test_fully_paid_bill_cannot_receive_more_payment(bill):
    record_payment(
        bill=bill,
        amount=Decimal("1000.00"),
        method=Payment.Method.MPESA,
        reference="MPESA-FULL-001",
    )

    bill.refresh_from_db()

    assert bill.status == Bill.Status.PAID
    assert bill.balance == Decimal("0.00")

    with pytest.raises(ValueError, match="no outstanding balance"):
        record_payment(
            bill=bill,
            amount=Decimal("1.00"),
            method=Payment.Method.CASH,
        )

    assert Payment.objects.count() == 1
