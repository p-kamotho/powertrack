from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone

from apps.billing.models import Bill
from apps.readings.models import MeterReading, BillingPeriod
from apps.tariffs.models import Tariff


def get_active_tariff(date=None):
    """
    Return the tariff applicable on the supplied date.
    """
    date = date or timezone.localdate()

    return (
        Tariff.objects
        .filter(
            is_active=True,
            effective_from__lte=date,
        )
        .filter(
            effective_to__isnull=True
        )
        .union(
            Tariff.objects.filter(
                is_active=True,
                effective_from__lte=date,
                effective_to__gte=date,
            )
        )
        .order_by("-effective_from")
        .first()
    )


def calculate_energy_charge(consumption, tariff):
    return (
        Decimal(consumption) * Decimal(tariff.rate_per_kwh)
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@transaction.atomic
def generate_bill(reading, tariff=None, due_date=None):
    """
    Generate a bill for one meter reading.

    A meter can only have one reading per billing period,
    and a reading can only have one bill.
    """
    if not isinstance(reading, MeterReading):
        raise TypeError("reading must be a MeterReading instance")

    if hasattr(reading, "bill"):
        return reading.bill

    tariff = tariff or get_active_tariff(reading.reading_date)

    if tariff is None:
        raise ValueError(
            f"No active tariff exists for {reading.reading_date}."
        )

    consumption = Decimal(reading.consumption)
    energy_charge = calculate_energy_charge(consumption, tariff)

    bill_number = (
        f"PT-{reading.billing_period.start_date:%Y%m}-"
        f"{reading.meter.meter_number}"
    )

    bill = Bill(
        bill_number=bill_number,
        tenant=reading.meter.room.tenant,
        reading=reading,
        billing_period=reading.billing_period,
        tariff=tariff,
        consumption=consumption,
        energy_charge=energy_charge,
        due_date=due_date,
    )

    bill.save()

    return bill


@transaction.atomic
def generate_period_bills(period, tariff=None, due_date=None):
    """
    Generate bills for every eligible reading in a billing period.
    """
    if not isinstance(period, BillingPeriod):
        raise TypeError("period must be a BillingPeriod instance")

    readings = (
        MeterReading.objects
        .select_related(
            "meter",
            "meter__room",
            "meter__room__tenant",
            "billing_period",
        )
        .filter(
            billing_period=period,
            meter__status="ACTIVE",
            meter__room__tenant__is_active=True,
        )
    )

    generated = []

    for reading in readings:
        if not hasattr(reading, "bill"):
            generated.append(
                generate_bill(
                    reading,
                    tariff=tariff,
                    due_date=due_date,
                )
            )

    return generated
