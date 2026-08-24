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


@pytest.mark.django_db
def test_payment_updates_bill():
    property_obj = Property.objects.create(
        name="Test Property"
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

    bill = Bill.objects.create(
        bill_number="BILL-TEST-001",
        tenant=tenant,
        reading=reading,
        billing_period=period,
        tariff=tariff,
    )

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
