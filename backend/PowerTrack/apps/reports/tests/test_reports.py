from decimal import Decimal
from datetime import date

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.models import Bill
from apps.payments.models import Payment

from apps.reports.services import (
    dashboard_summary,
    billing_summary,
    outstanding_bills,
    consumption_rows,
    consumption_csv,
)


@pytest.fixture
def report_data(db):
    property_obj = Property.objects.create(
        name="Report Property",
        address="Nakuru",
    )

    room1 = Room.objects.create(
        property=property_obj,
        room_number="R1",
        status=Room.Status.OCCUPIED,
    )

    room2 = Room.objects.create(
        property=property_obj,
        room_number="R2",
        status=Room.Status.OCCUPIED,
    )

    tenant1 = Tenant.objects.create(
        first_name="John",
        last_name="Kamau",
        phone_number="0712345678",
        room=room1,
        is_active=True,
    )

    tenant2 = Tenant.objects.create(
        first_name="Mary",
        last_name="Wanjiku",
        phone_number="0723456789",
        room=room2,
        is_active=True,
    )

    meter1 = Meter.objects.create(
        meter_number="MTR-001",
        room=room1,
        status=Meter.Status.ACTIVE,
        initial_reading=Decimal("100.00"),
    )

    meter2 = Meter.objects.create(
        meter_number="MTR-002",
        room=room2,
        status=Meter.Status.ACTIVE,
        initial_reading=Decimal("200.00"),
    )

    period = BillingPeriod.objects.create(
        name="August 2026",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 31),
    )

    reading1 = MeterReading.objects.create(
        meter=meter1,
        billing_period=period,
        reading_date=date(2026, 8, 31),
        previous_reading=Decimal("100.00"),
        current_reading=Decimal("150.00"),
    )

    reading2 = MeterReading.objects.create(
        meter=meter2,
        billing_period=period,
        reading_date=date(2026, 8, 31),
        previous_reading=Decimal("200.00"),
        current_reading=Decimal("280.00"),
    )

    tariff = Tariff.objects.create(
        name="Standard",
        rate_per_kwh=Decimal("10.00"),
        effective_from=date(2026, 1, 1),
        is_active=True,
    )

    bill1 = Bill.objects.create(
        bill_number="PT-202608-MTR-001",
        tenant=tenant1,
        reading=reading1,
        billing_period=period,
        tariff=tariff,
        due_date=date(2026, 9, 10),
    )

    bill2 = Bill.objects.create(
        bill_number="PT-202608-MTR-002",
        tenant=tenant2,
        reading=reading2,
        billing_period=period,
        tariff=tariff,
        due_date=date(2026, 9, 10),
    )

    return {
        "property": property_obj,
        "tenant1": tenant1,
        "tenant2": tenant2,
        "meter1": meter1,
        "meter2": meter2,
        "period": period,
        "reading1": reading1,
        "reading2": reading2,
        "tariff": tariff,
        "bill1": bill1,
        "bill2": bill2,
    }


def test_dashboard_summary(report_data):
    bill1 = report_data["bill1"]

    Payment.objects.create(
        bill=bill1,
        amount=Decimal("200.00"),
        method=Payment.Method.CASH,
        reference="PAY-001",
    )

    bill1.amount_paid = Decimal("200.00")
    bill1.save()

    summary = dashboard_summary()

    assert summary["total_billed"] == Decimal("1300.00")
    assert summary["total_collected"] == Decimal("200.00")
    assert summary["total_outstanding"] == Decimal("1100.00")
    assert summary["total_consumption"] == Decimal("130.00")

    assert summary["active_meters"] == 2
    assert summary["active_tenants"] == 2
    assert summary["total_bills"] == 2
    assert summary["partial_bills"] == 1


def test_dashboard_summary_excludes_cancelled_bill(report_data):
    bill = report_data["bill1"]

    bill.status = Bill.Status.CANCELLED
    bill.save(update_fields=["status"])

    summary = dashboard_summary()

    assert summary["total_billed"] == Decimal("800.00")
    assert summary["total_outstanding"] == Decimal("800.00")


def test_billing_summary_collection_rate(report_data):
    bill = report_data["bill1"]

    Payment.objects.create(
        bill=bill,
        amount=Decimal("250.00"),
        method=Payment.Method.MPESA,
        reference="MPESA-001",
    )

    bill.amount_paid = Decimal("250.00")
    bill.save()

    summary = billing_summary()

    assert summary["total_billed"] == Decimal("1300.00")
    assert summary["total_collected"] == Decimal("250.00")
    assert summary["collection_rate"] == (
        Decimal("250.00") / Decimal("1300.00") * Decimal("100")
    )


def test_billing_summary_zero_billing(report_data):
    Bill.objects.all().delete()

    summary = billing_summary()

    assert summary["total_billed"] == Decimal("0.00")
    assert summary["collection_rate"] == Decimal("0.00")


def test_outstanding_bills_only_returns_positive_balances(report_data):
    bill1 = report_data["bill1"]
    bill2 = report_data["bill2"]

    Payment.objects.create(
        bill=bill1,
        amount=Decimal("200.00"),
        method=Payment.Method.CASH,
        reference="PAY-002",
    )

    bill1.amount_paid = Decimal("200.00")
    bill1.save()

    bill2.status = Bill.Status.CANCELLED
    bill2.save(update_fields=["status"])

    bills = list(outstanding_bills())

    assert bills == [bill1]
    assert bills[0].balance == Decimal("0.00") or bills[0].balance > Decimal("0.00")


def test_consumption_rows(report_data):
    rows = consumption_rows()

    assert len(rows) == 2

    first = rows[0]

    assert first["meter_number"] in {"MTR-001", "MTR-002"}
    assert first["billing_period"] == "August 2026"
    assert first["previous_reading"] in {
        Decimal("100.00"),
        Decimal("200.00"),
    }
    assert first["current_reading"] in {
        Decimal("150.00"),
        Decimal("280.00"),
    }


def test_consumption_rows_are_ordered_latest_first(report_data):
    rows = consumption_rows()

    assert rows[0]["reading_date"] >= rows[1]["reading_date"]


def test_consumption_csv(report_data):
    csv_data = consumption_csv()

    assert "Meter Number" in csv_data
    assert "Billing Period" in csv_data
    assert "Previous Reading" in csv_data
    assert "Current Reading" in csv_data
    assert "Consumption" in csv_data

    assert "MTR-001" in csv_data
    assert "MTR-002" in csv_data
    assert "August 2026" in csv_data


@pytest.fixture
def authenticated_client(client, db):
    user_model = get_user_model()

    user = user_model.objects.create_user(
        username="reportuser",
        password="test-password-123",
    )

    client.force_login(user)

    return client


def test_report_home_requires_login(client):
    response = client.get(reverse("report_home"))

    assert response.status_code == 302
    assert "/login" in response.url


def test_consumption_report_requires_login(client):
    response = client.get(reverse("consumption_report"))

    assert response.status_code == 302
    assert "/login" in response.url


def test_consumption_csv_requires_login(client):
    response = client.get(reverse("consumption_csv"))

    assert response.status_code == 302
    assert "/login" in response.url


def test_report_home(authenticated_client, report_data):
    response = authenticated_client.get(reverse("report_home"))

    assert response.status_code == 200
    assert "summary" in response.context


def test_consumption_report(authenticated_client, report_data):
    response = authenticated_client.get(reverse("consumption_report"))

    assert response.status_code == 200
    assert len(response.context["rows"]) == 2


def test_consumption_csv_download(authenticated_client, report_data):
    response = authenticated_client.get(reverse("consumption_csv"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert "attachment" in response["Content-Disposition"]
    assert b"Meter Number" in response.content
