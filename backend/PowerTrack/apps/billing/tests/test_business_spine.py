from datetime import date
from decimal import Decimal

import pytest

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.models import Bill
from apps.billing.services import generate_bill
from apps.payments.models import Payment
from apps.payments.services import record_payment
from apps.notifications.models import Notification
from apps.reports.services import dashboard_summary


@pytest.mark.django_db
def test_powertrack_business_spine():
    """
    Verify the complete PowerTrack operational chain:

    Property
        -> Room
        -> Tenant
        -> Meter
        -> Reading
        -> Consumption
        -> Tariff
        -> Bill
        -> Payment
        -> Balance
        -> Status
        -> Notification
        -> Reports
    """

    # ---------------------------------------------------------
    # 1. PROPERTY
    # ---------------------------------------------------------
    property_obj = Property.objects.create(
        name="PowerTrack Integration Property",
        address="Nakuru, Kenya",
    )

    assert property_obj.pk is not None

    # ---------------------------------------------------------
    # 2. ROOM
    # ---------------------------------------------------------
    room = Room.objects.create(
        property=property_obj,
        room_number="A-101",
        status=Room.Status.OCCUPIED,
    )

    assert room.property == property_obj
    assert room.room_number == "A-101"

    # ---------------------------------------------------------
    # 3. TENANT
    # ---------------------------------------------------------
    tenant = Tenant.objects.create(
        first_name="Integration",
        last_name="Tenant",
        phone_number="0712345678",
        room=room,
        is_active=True,
    )

    assert tenant.room == room
    assert tenant.full_name == "Integration Tenant"

    # ---------------------------------------------------------
    # 4. METER
    # ---------------------------------------------------------
    meter = Meter.objects.create(
        meter_number="INT-MTR-001",
        room=room,
        status=Meter.Status.ACTIVE,
        initial_reading=Decimal("100.00"),
    )

    assert meter.room == room
    assert meter.status == Meter.Status.ACTIVE

    # ---------------------------------------------------------
    # 5. BILLING PERIOD
    # ---------------------------------------------------------
    period = BillingPeriod.objects.create(
        name="Integration August 2026",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
    )

    # ---------------------------------------------------------
    # 6. METER READING
    # ---------------------------------------------------------
    reading = MeterReading.objects.create(
        meter=meter,
        billing_period=period,
        reading_date=date(2026, 8, 31),
        previous_reading=Decimal("100.00"),
        current_reading=Decimal("175.00"),
    )

    # 100 -> 175 = 75 kWh
    assert reading.consumption == Decimal("75.00")

    # ---------------------------------------------------------
    # 7. TARIFF
    # ---------------------------------------------------------
    tariff = Tariff.objects.create(
        name="Integration Standard Tariff",
        rate_per_kwh=Decimal("10.00"),
        effective_from=date(2026, 1, 1),
        is_active=True,
    )

    assert tariff.rate_per_kwh == Decimal("10.00")

    # ---------------------------------------------------------
    # 8. BILL
    # ---------------------------------------------------------
    bill = generate_bill(
        reading,
        tariff=tariff,
        due_date=date(2026, 9, 10),
    )

    assert bill.tenant == tenant
    assert bill.reading == reading
    assert bill.billing_period == period
    assert bill.tariff == tariff

    # 75 kWh × KSh 10 = KSh 750
    assert bill.consumption == Decimal("75.00")
    assert bill.energy_charge == Decimal("750.00")
    assert bill.total_amount == Decimal("750.00")
    assert bill.amount_paid == Decimal("0.00")
    assert bill.balance == Decimal("750.00")
    assert bill.status == Bill.Status.ISSUED

    # ---------------------------------------------------------
    # 9. FIRST PAYMENT
    # ---------------------------------------------------------
    payment1, updated_bill = record_payment(
        bill=bill,
        amount=Decimal("300.00"),
        method=Payment.Method.MPESA,
        reference="INT-MPESA-001",
    )

    assert payment1.bill == bill
    assert payment1.amount == Decimal("300.00")
    assert payment1.method == Payment.Method.MPESA
    assert payment1.reference == "INT-MPESA-001"

    assert updated_bill.amount_paid == Decimal("300.00")
    assert updated_bill.balance == Decimal("450.00")
    assert updated_bill.status == Bill.Status.PARTIAL

    # ---------------------------------------------------------
    # 10. PAYMENT NOTIFICATION
    # ---------------------------------------------------------
    notification = Notification.objects.filter(
        bill=bill,
        channel="EMAIL",
    ).latest("created_at")

    assert notification.tenant == tenant
    assert notification.bill == bill
    assert notification.status == "QUEUED"
    assert "300.00" in notification.message
    assert "450.00" in notification.message
    assert "INT-MPESA-001" in notification.message

    # ---------------------------------------------------------
    # 11. SECOND PAYMENT
    # ---------------------------------------------------------
    payment2, fully_paid_bill = record_payment(
        bill=bill,
        amount=Decimal("450.00"),
        method=Payment.Method.CASH,
        reference="INT-CASH-001",
    )

    assert payment2.amount == Decimal("450.00")

    assert fully_paid_bill.amount_paid == Decimal("750.00")
    assert fully_paid_bill.balance == Decimal("0.00")
    assert fully_paid_bill.status == Bill.Status.PAID

    # ---------------------------------------------------------
    # 12. PAYMENT LEDGER
    # ---------------------------------------------------------
    payments = Payment.objects.filter(bill=bill)

    assert payments.count() == 2

    total_payments = sum(
        payment.amount for payment in payments
    )

    assert total_payments == Decimal("750.00")

    # ---------------------------------------------------------
    # 13. REPORTING
    # ---------------------------------------------------------
    summary = dashboard_summary()

    assert summary["total_billed"] == Decimal("750.00")
    assert summary["total_collected"] == Decimal("750.00")
    assert summary["total_outstanding"] == Decimal("0.00")
    assert summary["total_consumption"] == Decimal("75.00")

    assert summary["active_meters"] == 1
    assert summary["active_tenants"] == 1
    assert summary["total_bills"] == 1
    assert summary["paid_bills"] == 1
    assert summary["partial_bills"] == 0
    assert summary["overdue_bills"] == 0
