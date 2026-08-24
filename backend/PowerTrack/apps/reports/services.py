from decimal import Decimal
import csv
from io import StringIO

from django.db.models import Sum

from apps.billing.models import Bill
from apps.payments.models import Payment
from apps.readings.models import MeterReading
from apps.meters.models import Meter
from apps.tenants.models import Tenant


def dashboard_summary():
    billed = (
        Bill.objects
        .exclude(status=Bill.Status.CANCELLED)
        .aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    collected = (
        Payment.objects
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    outstanding = (
        Bill.objects
        .exclude(status=Bill.Status.CANCELLED)
        .aggregate(total=Sum("balance"))["total"]
        or Decimal("0.00")
    )

    consumption = (
        MeterReading.objects
        .aggregate(total=Sum("consumption"))["total"]
        or Decimal("0.00")
    )

    return {
        "total_billed": billed,
        "total_collected": collected,
        "total_outstanding": outstanding,
        "total_consumption": consumption,
        "active_meters": Meter.objects.filter(
            status=Meter.Status.ACTIVE
        ).count(),
        "active_tenants": Tenant.objects.filter(
            is_active=True
        ).count(),
        "total_bills": Bill.objects.count(),
        "paid_bills": Bill.objects.filter(
            status=Bill.Status.PAID
        ).count(),
        "partial_bills": Bill.objects.filter(
            status=Bill.Status.PARTIAL
        ).count(),
        "overdue_bills": Bill.objects.filter(
            status=Bill.Status.OVERDUE
        ).count(),
    }


def billing_summary():
    """
    Compatibility wrapper used by the reports views.
    """

    summary = dashboard_summary()

    summary["collection_rate"] = (
        (summary["total_collected"] / summary["total_billed"]) * Decimal("100")
        if summary["total_billed"] > 0
        else Decimal("0.00")
    )

    return summary


def outstanding_bills():
    return (
        Bill.objects
        .select_related(
            "tenant",
            "reading",
            "tariff",
            "billing_period",
        )
        .filter(balance__gt=0)
        .exclude(status=Bill.Status.CANCELLED)
        .order_by("-due_date", "-created_at")
    )


def consumption_rows():
    """
    Return consumption data for the reporting page.
    """

    readings = (
        MeterReading.objects
        .select_related(
            "meter",
            "billing_period",
        )
        .order_by(
            "-reading_date",
            "-id",
        )
    )

    rows = []

    for reading in readings:
        rows.append({
            "meter_number": reading.meter.meter_number,
            "billing_period": reading.billing_period.name,
            "reading_date": reading.reading_date,
            "previous_reading": reading.previous_reading,
            "current_reading": reading.current_reading,
            "consumption": reading.consumption,
        })

    return rows


def consumption_csv():
    """
    Generate a CSV export of meter consumption.
    """

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Meter Number",
        "Billing Period",
        "Reading Date",
        "Previous Reading",
        "Current Reading",
        "Consumption",
    ])

    for row in consumption_rows():
        writer.writerow([
            row["meter_number"],
            row["billing_period"],
            row["reading_date"],
            row["previous_reading"],
            row["current_reading"],
            row["consumption"],
        ])

    return output.getvalue()
