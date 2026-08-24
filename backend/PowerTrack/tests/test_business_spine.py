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
from apps.notifications.models import Notification
from apps.reports.services import dashboard_summary


@pytest.mark.django_db
def test_complete_powertrack_business_spine():

    # PROPERTY
    property_obj = Property.objects.create(
        name="PowerTrack Apartments",
        address="Karatina",
    )

    # ROOM
    room = Room.objects.create(
        property=property_obj,
        room_number="A-101",
        floor="Ground",
    )

    # TENANT
    tenant = Tenant.objects.create(
        first_name="Stan",
        last_name="Test",
        phone_number="0712345678",
        room=room,
    )

    # METER
    meter = Meter.objects.create(
        meter_number="PT-MTR-001",
        room=room,
        initial_reading=Decimal("100"),
    )

    # BILLING PERIOD
    period = BillingPeriod.objects.create(
        name="August 2026",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
    )

    # READING
    reading = MeterReading.objects.create(
        meter=meter,
        billing_period=period,
        reading_date=date(2026, 8, 31),
        previous_reading=Decimal("100"),
        current_reading=Decimal("200"),
    )

    # TARIFF
    tariff = Tariff.objects.create(
        name="Standard Electricity",
        rate_per_kwh=Decimal("15.00"),
        effective_from=date(2026, 1, 1),
    )

    # BILL
    bill = Bill.objects.create(
        bill_number="PT-2026-0001",
        tenant=tenant,
        reading=reading,
        billing_period=period,
        tariff=tariff,
    )

    assert bill.consumption == Decimal("100")
    assert bill.total_amount == Decimal("1500.00")
    assert bill.balance == Decimal("1500.00")

    # PAYMENT
    payment, bill = record_payment(
        bill=bill,
        amount=Decimal("1000.00"),
        method=Payment.Method.MPESA,
        reference="RCP-001",
    )

    bill.refresh_from_db()

    assert payment.amount == Decimal("1000.00")
    assert bill.amount_paid == Decimal("1000.00")
    assert bill.balance == Decimal("500.00")
    assert bill.status == Bill.Status.PARTIAL

    # NOTIFICATION
    assert Notification.objects.filter(
        bill=bill,
        tenant=tenant,
    ).exists()

    # FINAL PAYMENT
    record_payment(
        bill=bill,
        amount=Decimal("500.00"),
        method=Payment.Method.MPESA,
        reference="RCP-002",
    )

    bill.refresh_from_db()

    assert bill.amount_paid == Decimal("1500.00")
    assert bill.balance == Decimal("0.00")
    assert bill.status == Bill.Status.PAID

    # REPORTING
    summary = dashboard_summary()

    assert summary["total_billed"] == Decimal("1500.00")
    assert summary["total_collected"] == Decimal("1500.00")
    assert summary["total_outstanding"] == Decimal("0.00")
    assert summary["total_consumption"] == Decimal("100")
    assert summary["paid_bills"] == 1
