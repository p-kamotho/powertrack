import csv
from io import StringIO
from django.db.models import Sum
from apps.readings.models import MeterReading
from apps.billing.models import Bill
from apps.payments.models import Payment

def consumption_rows():
    return MeterReading.objects.select_related("meter", "billing_period")  # Fixed typo: "billing_period" not "biling_period"

def billing_summary():
    return {
        "billed": Bill.objects.aggregate(v=Sum("total_amount"))["v"] or 0,
        "paid": Payment.objects.aggregate(v=Sum("amount"))["v"] or 0,
        "consumption": MeterReading.objects.aggregate(v=Sum("consumption"))["v"] or 0,
    }

def consumption_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Meter", "Period", "Previous kWh", "Current kWh", "Consumption kWh", "Reading Date"])
    for reading in consumption_rows():
        writer.writerow([
            reading.meter.meter_number,
            reading.billing_period.name,  # Changed from reading.period.name to reading.billing_period.name
            reading.previous_reading,
            reading.current_reading,
            reading.consumption,
            reading.reading_date,
        ])
    return output.getvalue()