from datetime import date

from django.db import transaction

from apps.billing.models import Bill


ALLOWED_TRANSITIONS = {
    Bill.Status.ISSUED: {
        Bill.Status.PARTIAL,
        Bill.Status.PAID,
        Bill.Status.OVERDUE,
        Bill.Status.CANCELLED,
    },
    Bill.Status.PARTIAL: {
        Bill.Status.PAID,
        Bill.Status.OVERDUE,
        Bill.Status.CANCELLED,
    },
    Bill.Status.OVERDUE: {
        Bill.Status.PARTIAL,
        Bill.Status.PAID,
        Bill.Status.CANCELLED,
    },
    Bill.Status.PAID: set(),
    Bill.Status.CANCELLED: set(),
}


@transaction.atomic
def transition_bill_status(bill, new_status):
    """
    Perform a validated bill status transition.

    Returns:
        Bill: refreshed bill instance.
    """

    if not isinstance(bill, Bill):
        raise TypeError("bill must be a Bill instance")

    valid_statuses = {
        choice[0]
        for choice in Bill.Status.choices
    }

    if new_status not in valid_statuses:
        raise ValueError(f"Invalid bill status: {new_status}")

    bill = (
        Bill.objects
        .select_for_update()
        .get(pk=bill.pk)
    )

    current_status = bill.status

    if current_status == new_status:
        return bill

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())

    if new_status not in allowed:
        raise ValueError(
            f"Invalid bill status transition: "
            f"{current_status} -> {new_status}."
        )

    if new_status == Bill.Status.PAID:
        if bill.total_amount <= 0:
            raise ValueError(
                "A bill with no positive total cannot be marked as paid."
            )

        if bill.balance > 0:
            raise ValueError(
                "A bill with an outstanding balance cannot be marked as paid."
            )

    if new_status == Bill.Status.PARTIAL:
        if bill.amount_paid <= 0:
            raise ValueError(
                "A bill with no payment cannot be marked as partially paid."
            )

        if bill.balance <= 0:
            raise ValueError(
                "A fully paid bill cannot be marked as partially paid."
            )

    if new_status == Bill.Status.OVERDUE:
        if bill.balance <= 0:
            raise ValueError(
                "A fully paid bill cannot be marked as overdue."
            )

        if bill.due_date is None:
            raise ValueError(
                "A bill without a due date cannot be marked as overdue."
            )

        if bill.due_date >= date.today():
            raise ValueError(
                "A bill cannot be marked as overdue before its due date."
            )

    if new_status == Bill.Status.CANCELLED:
        if bill.amount_paid > 0:
            raise ValueError(
                "A bill with recorded payments cannot be cancelled."
            )

    bill.status = new_status
    bill.save(update_fields=["status"])

    return bill


@transaction.atomic
def mark_bill_overdue(bill):
    """
    Mark a bill overdue when its due date has passed
    and it still has an outstanding balance.
    """

    if not isinstance(bill, Bill):
        raise TypeError("bill must be a Bill instance")

    bill = (
        Bill.objects
        .select_for_update()
        .get(pk=bill.pk)
    )

    if bill.due_date is None:
        return bill

    if bill.due_date >= date.today():
        return bill

    if bill.balance <= 0:
        return bill

    if bill.status in {
        Bill.Status.ISSUED,
        Bill.Status.PARTIAL,
    }:
        return transition_bill_status(
            bill,
            Bill.Status.OVERDUE,
        )

    return bill


@transaction.atomic
def cancel_bill(bill):
    """
    Cancel an unpaid bill.

    Bills with recorded payments cannot be cancelled.
    """

    return transition_bill_status(
        bill,
        Bill.Status.CANCELLED,
    )
