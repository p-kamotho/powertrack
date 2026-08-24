from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.billing.models import Bill
from apps.tariffs.models import Tariff
from apps.readings.models import MeterReading


@transaction.atomic
def generate_bill(
    *,
    tenant,
    reading,
    billing_period,
    bill_number,
    tariff=None,
    additional_charges=Decimal("0.00"),
    discount=Decimal("0.00"),
    due_date=None,
):
    """
    Generate a bill from a meter reading.

    The reading determines consumption.
    The tariff determines the energy rate.
    """

    if tariff is None:
        tariff = (
            Tariff.objects
            .filter(
                is_active=True,
                effective_from__lte=reading.reading_date,
            )
            .filter(
                effective_to__isnull=True
            )
            .order_by("-effective_from")
            .first()
        )

    if tariff is None:
        raise ValueError("No active tariff is available for this reading date.")

    if Bill.objects.filter(reading=reading).exists():
        raise ValueError("A bill already exists for this meter reading.")

    return Bill.objects.create(
        bill_number=bill_number,
        tenant=tenant,
        reading=reading,
        billing_period=billing_period,
        tariff=tariff,
        additional_charges=Decimal(str(additional_charges)),
        discount=Decimal(str(discount)),
        due_date=due_date,
    )


@transaction.atomic
def recalculate_bill(bill):
    """
    Recalculate a bill after a change in payment or charges.
    """

    bill.amount_paid = max(
        Decimal("0.00"),
        Decimal(str(bill.amount_paid)),
    )

    bill.additional_charges = max(
        Decimal("0.00"),
        Decimal(str(bill.additional_charges)),
    )

    bill.discount = max(
        Decimal("0.00"),
        Decimal(str(bill.discount)),
    )

    bill.save()

    return bill


def mark_overdue(bill):
    """
    Mark an unpaid bill overdue when its due date has passed.
    """

    if (
        bill.due_date
        and bill.due_date < timezone.localdate()
        and bill.balance > Decimal("0.00")
        and bill.status not in {
            Bill.Status.PAID,
            Bill.Status.CANCELLED,
        }
    ):
        bill.status = Bill.Status.OVERDUE
        bill.save(update_fields=["status"])

    return bill
