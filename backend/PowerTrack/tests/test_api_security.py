from decimal import Decimal
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.models import Bill
from apps.payments.models import Payment
from apps.notifications.models import Notification
from apps.billing.services import generate_bill


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(
        username="normaluser",
        password="StrongPassword123!",
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staffuser",
        password="StrongPassword123!",
        is_staff=True,
    )


def authenticate(client, user):
    client.force_authenticate(user=user)


@pytest.mark.django_db
def test_anonymous_user_cannot_access_protected_api(api_client):
    response = api_client.get("/api/meters/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_authenticated_user_can_read_meters(api_client, normal_user, meter):
    authenticate(api_client, normal_user)

    response = api_client.get("/api/meters/")

    assert response.status_code == 200
    assert response.data[0]["meter_number"] == meter.meter_number


@pytest.mark.django_db
def test_normal_user_cannot_create_meter(api_client, normal_user, room):
    authenticate(api_client, normal_user)

    response = api_client.post(
        "/api/meters/",
        {
            "meter_number": "FORBIDDEN-MTR",
            "room": room.pk,
            "status": "ACTIVE",
            "initial_reading": "0.00",
        },
        format="json",
    )

    assert response.status_code == 403
    assert not Meter.objects.filter(
        meter_number="FORBIDDEN-MTR"
    ).exists()


@pytest.mark.django_db
def test_staff_user_can_create_meter(api_client, staff_user, room):
    authenticate(api_client, staff_user)

    response = api_client.post(
        "/api/meters/",
        {
            "meter_number": "STAFF-MTR-001",
            "room": room.pk,
            "status": "ACTIVE",
            "initial_reading": "0.00",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Meter.objects.filter(
        meter_number="STAFF-MTR-001"
    ).exists()


@pytest.mark.django_db
def test_bill_financial_fields_cannot_be_forged(
    api_client,
    staff_user,
    bill,
):
    authenticate(api_client, staff_user)

    response = api_client.patch(
        f"/api/bills/{bill.pk}/",
        {
            "amount_paid": "0.00",
            "balance": "0.00",
            "total_amount": "1.00",
            "status": "PAID",
        },
        format="json",
    )

    assert response.status_code == 200

    bill.refresh_from_db()

    assert bill.amount_paid == Decimal("0.00")
    assert bill.balance == Decimal("500.00")
    assert bill.total_amount == Decimal("500.00")
    assert bill.status == Bill.Status.ISSUED


@pytest.mark.django_db
def test_bill_creation_uses_billing_service(
    api_client,
    staff_user,
    reading,
    tariff,
):
    authenticate(api_client, staff_user)

    response = api_client.post(
        "/api/bills/",
        {
            "reading": reading.pk,
            "tariff": tariff.pk,
            "due_date": "2026-09-10",
        },
        format="json",
    )

    assert response.status_code == 201

    bill = Bill.objects.get(reading=reading)

    assert bill.consumption == Decimal("50.00")
    assert bill.energy_charge == Decimal("500.00")
    assert bill.total_amount == Decimal("500.00")
    assert bill.balance == Decimal("500.00")
    assert bill.status == Bill.Status.ISSUED


@pytest.mark.django_db
def test_bill_creation_requires_reading(api_client, staff_user):
    authenticate(api_client, staff_user)

    response = api_client.post(
        "/api/bills/",
        {
            "due_date": "2026-09-10",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_api_updates_bill_through_service(
    api_client,
    staff_user,
    bill,
):
    authenticate(api_client, staff_user)

    response = api_client.post(
        "/api/payments/",
        {
            "bill": bill.pk,
            "amount": "200.00",
            "method": "MPESA",
            "reference": "API-MPESA-001",
        },
        format="json",
    )

    assert response.status_code == 201

    bill.refresh_from_db()

    assert bill.amount_paid == Decimal("200.00")
    assert bill.balance == Decimal("300.00")
    assert bill.status == Bill.Status.PARTIAL

    payment = Payment.objects.get(
        bill=bill,
        reference="API-MPESA-001",
    )

    assert payment.amount == Decimal("200.00")


@pytest.mark.django_db
def test_normal_user_cannot_create_payment(
    api_client,
    normal_user,
    bill,
):
    authenticate(api_client, normal_user)

    response = api_client.post(
        "/api/payments/",
        {
            "bill": bill.pk,
            "amount": "200.00",
            "method": "CASH",
            "reference": "FORBIDDEN-PAYMENT",
        },
        format="json",
    )

    assert response.status_code == 403
    assert not Payment.objects.filter(
        reference="FORBIDDEN-PAYMENT"
    ).exists()


@pytest.mark.django_db
def test_payment_cannot_exceed_bill_balance(
    api_client,
    staff_user,
    bill,
):
    authenticate(api_client, staff_user)

    response = api_client.post(
        "/api/payments/",
        {
            "bill": bill.pk,
            "amount": "600.00",
            "method": "CASH",
            "reference": "OVERPAY-001",
        },
        format="json",
    )

    assert response.status_code == 400

    bill.refresh_from_db()

    assert bill.amount_paid == Decimal("0.00")
    assert bill.balance == Decimal("500.00")
    assert not Payment.objects.filter(
        reference="OVERPAY-001"
    ).exists()


@pytest.mark.django_db
def test_notifications_are_read_only(
    api_client,
    normal_user,
    tenant,
    bill,
):
    authenticate(api_client, normal_user)

    response = api_client.post(
        "/api/notifications/",
        {
            "tenant": tenant.pk,
            "bill": bill.pk,
            "channel": "EMAIL",
            "subject": "Forged notification",
            "message": "This should not be created.",
        },
        format="json",
    )

    assert response.status_code == 405

    assert not Notification.objects.filter(
        subject="Forged notification"
    ).exists()


@pytest.mark.django_db
def test_current_user_endpoint(api_client, normal_user):
    authenticate(api_client, normal_user)

    response = api_client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.data["username"] == "normaluser"
    assert response.data["is_staff"] is False


@pytest.mark.django_db
def test_login_endpoint(api_client, normal_user):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "normaluser",
            "password": "StrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["detail"] == "Login successful."
    assert response.data["user"]["username"] == "normaluser"


@pytest.mark.django_db
def test_invalid_login_is_rejected(api_client, normal_user):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "normaluser",
            "password": "WrongPassword!",
        },
        format="json",
    )

    assert response.status_code == 401
