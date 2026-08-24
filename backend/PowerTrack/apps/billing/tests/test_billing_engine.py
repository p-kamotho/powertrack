import pytest
from decimal import Decimal
from datetime import date

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.models import Bill


@pytest.mark.django_db
def test_bill_calculation():
    property_obj = Property.objects.create(
        name="PowerTrack Property",
        address="Test Address",
    )

    room = Room.objects.create(
        property=property_obj,
        room_number="101",
        floor="1",
    )

    tenant = Tenant.objects.create(
        first_name="Test",
        last_name="Tenant",
        phone_number="0712345678",
        room=room,
    )

    meter = Meter.objects.create(
        meter_number="MTR-001",
        room=room,
        initial_reading=Decimal("100"),
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
        name="Standard Tariff",
        rate_per_kwh=Decimal("25.00"),
        effective_from=date(2026, 1, 1),
    )

    bill = Bill.objects.create(
        bill_number="INV-0001",
        tenant=tenant,
        reading=reading,
        billing_period=period,
        tariff=tariff,
    )

    bill.refresh_from_db()

    assert bill.consumption == Decimal("50")
    assert bill.energy_charge == Decimal("1250.00")
    assert bill.total_amount == Decimal("1250.00")
    assert bill.amount_paid == Decimal("0")
    assert bill.balance == Decimal("1250.00")
    assert bill.status == Bill.Status.ISSUED
