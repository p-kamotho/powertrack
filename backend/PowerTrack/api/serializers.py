from rest_framework import serializers
from apps.meters.models import Meter
from apps.readings.models import MeterReading
from apps.billing.models import Bill
from apps.payments.models import Payment

class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = "__all__"

class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterReading
        fields = "__all__"

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
