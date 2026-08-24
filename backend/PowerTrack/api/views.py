from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import MeterSerializer, ReadingSerializer, BillSerializer, PaymentSerializer
from apps.meters.models import Meter
from apps.readings.models import MeterReading
from apps.billing.models import Bill
from apps.payments.models import Payment

class AuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

class MeterViewSet(AuthenticatedViewSet):
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer

class ReadingViewSet(AuthenticatedViewSet):
    queryset = MeterReading.objects.all()
    serializer_class = ReadingSerializer

class BillViewSet(AuthenticatedViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class PaymentViewSet(AuthenticatedViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
