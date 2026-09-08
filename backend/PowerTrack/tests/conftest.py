from datetime import date
from decimal import Decimal

import pytest

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.services import generate_bill


@pytest.fixture
def property_obj(db):
    return Property.objects.create(
        name="API Security Property",
        address="Nakuru, Kenya",
    )


@pytest.fixture
def room(property_obj):
    return Room.objects.create(
        property=property_obj,
        room_number="SEC-101",
        status=Room.Status.OCCUPIED,
    )


@pytest.fixture
def tenant(room):
    return Tenant.objects.create(
        first_name="API",
        last_name="Tenant",
        phone_number="0712345678",
        room=room,
        is_active=True,
    )


@pytest.fixture
def meter(room, tenant):
    return Meter.objects.create(
        meter_number="API-MTR-001",
        room=room,
        status=Meter.Status.ACTIVE,
        initial_reading=Decimal("100.00"),
    )


@pytest.fixture
def reading(meter):
    period = BillingPeriod.objects.create(
        name="API Security Period",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
    )

    return MeterReading.objects.create(
        meter=meter,
        billing_period=period,
        reading_date=date(2026, 8, 31),
        previous_reading=Decimal("100.00"),
        current_reading=Decimal("150.00"),
    )


@pytest.fixture
def tariff():
    return Tariff.objects.create(
        name="API Security Tariff",
        rate_per_kwh=Decimal("10.00"),
        effective_from=date(2026, 1, 1),
        is_active=True,
    )


@pytest.fixture
def bill(reading, tariff, tenant):
    return generate_bill(
        reading=reading,
        tariff=tariff,
        due_date=date(2026, 9, 10),
    )
