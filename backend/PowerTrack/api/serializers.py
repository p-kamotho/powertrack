from decimal import Decimal
from rest_framework import serializers

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.models import Bill
from apps.payments.models import Payment
from apps.notifications.models import Notification


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class TenantSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Tenant
        fields = "__all__"


class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = "__all__"


class BillingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingPeriod
        fields = "__all__"


class ReadingSerializer(serializers.ModelSerializer):
    consumption = serializers.ReadOnlyField()

    class Meta:
        model = MeterReading
        fields = "__all__"


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = "__all__"


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = "__all__"

        read_only_fields = (
            "bill_number",
            "consumption",
            "energy_charge",
            "total_amount",
            "amount_paid",
            "balance",
            "status",
            "created_at",
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

        read_only_fields = (
            "paid_at",
        )


class PaymentCreateSerializer(serializers.Serializer):
    bill = serializers.PrimaryKeyRelatedField(
        queryset=Bill.objects.all()
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    method = serializers.ChoiceField(
        choices=Payment.Method.choices
    )
    reference = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

        read_only_fields = (
            "created_at",
            "sent_at",
        )
