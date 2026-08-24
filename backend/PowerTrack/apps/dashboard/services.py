from django.db.models import Sum
from apps.meters.models import Meter
from apps.readings.models import MeterReading
from apps.billing.models import Bill
from apps.payments.models import Payment

def dashboard_metrics():
    billed = Bill.objects.aggregate(total=Sum("total_amount")).get("total") or 0
    paid = Payment.objects.aggregate(total=Sum("amount")).get("total") or 0
    consumption = MeterReading.objects.aggregate(total=Sum("consumption")).get("total") or 0
    return {
        "meter_count": Meter.objects.count(),
        "reading_count": MeterReading.objects.count(),
        "bill_count": Bill.objects.count(),
        "payment_count": Payment.objects.count(),
        "total_consumption": consumption,
        "total_billed": billed,
        "total_paid": paid,
        "outstanding": billed - paid,
    }
