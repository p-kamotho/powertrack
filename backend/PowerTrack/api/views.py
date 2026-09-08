from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.properties.models import Property, Room
from apps.tenants.models import Tenant
from apps.meters.models import Meter
from apps.readings.models import BillingPeriod, MeterReading
from apps.tariffs.models import Tariff
from apps.billing.models import Bill
from apps.billing.services import generate_bill
from apps.payments.models import Payment
from apps.payments.services import record_payment
from apps.notifications.models import Notification

from .permissions import IsAuthenticatedReadOnlyOrStaff
from .serializers import (
    PropertySerializer,
    RoomSerializer,
    TenantSerializer,
    MeterSerializer,
    BillingPeriodSerializer,
    ReadingSerializer,
    TariffSerializer,
    BillSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    NotificationSerializer,
)


class SecureModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class PropertyViewSet(SecureModelViewSet):
    queryset = Property.objects.all().order_by("name")
    serializer_class = PropertySerializer


class RoomViewSet(SecureModelViewSet):
    queryset = Room.objects.select_related("property").all().order_by(
        "property", "room_number"
    )
    serializer_class = RoomSerializer


class TenantViewSet(SecureModelViewSet):
    queryset = Tenant.objects.select_related("room", "room__property").all().order_by(
        "last_name", "first_name"
    )
    serializer_class = TenantSerializer


class MeterViewSet(SecureModelViewSet):
    queryset = Meter.objects.select_related(
        "room", "room__property"
    ).all().order_by("meter_number")
    serializer_class = MeterSerializer


class BillingPeriodViewSet(SecureModelViewSet):
    queryset = BillingPeriod.objects.all().order_by("-start_date")
    serializer_class = BillingPeriodSerializer


class ReadingViewSet(SecureModelViewSet):
    queryset = MeterReading.objects.select_related(
        "meter",
        "billing_period",
        "meter__room",
        "meter__room__property",
    ).all().order_by("-reading_date", "-id")
    serializer_class = ReadingSerializer


class TariffViewSet(SecureModelViewSet):
    queryset = Tariff.objects.all().order_by("-effective_from")
    serializer_class = TariffSerializer


class BillViewSet(SecureModelViewSet):
    queryset = Bill.objects.select_related(
        "tenant",
        "reading",
        "tariff",
        "billing_period",
    ).all().order_by("-created_at")

    serializer_class = BillSerializer

    def create(self, request, *args, **kwargs):
        """
        Bills must be generated through the billing service.
        Direct Bill.objects.create() is intentionally blocked.
        """
        reading_id = request.data.get("reading")
        tariff_id = request.data.get("tariff")
        due_date = request.data.get("due_date")

        if not reading_id:
            return Response(
                {"detail": "reading is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reading = MeterReading.objects.get(pk=reading_id)
        except MeterReading.DoesNotExist:
            return Response(
                {"detail": "Reading not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        tariff = None

        if tariff_id:
            try:
                tariff = Tariff.objects.get(pk=tariff_id)
            except Tariff.DoesNotExist:
                return Response(
                    {"detail": "Tariff not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            bill = generate_bill(
                reading=reading,
                tariff=tariff,
                due_date=due_date,
            )
        except (TypeError, ValueError) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            BillSerializer(bill).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentViewSet(SecureModelViewSet):
    queryset = Payment.objects.select_related(
        "bill",
        "bill__tenant",
    ).all().order_by("-paid_at")

    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        """
        Payments must pass through record_payment().
        This prevents API clients from manually manipulating bill balances.
        """
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                payment, bill = record_payment(
                    bill=serializer.validated_data["bill"],
                    amount=serializer.validated_data["amount"],
                    method=serializer.validated_data["method"],
                    reference=serializer.validated_data.get("reference", ""),
                )
        except (TypeError, ValueError) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "payment": PaymentSerializer(payment).data,
                "bill": BillSerializer(bill).data,
            },
            status=status.HTTP_201_CREATED,
        )


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Notifications are system-generated.
    API users can inspect them but cannot manually create/delete them.
    """

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.select_related(
        "tenant",
        "bill",
    ).all().order_by("-created_at")
    serializer_class = NotificationSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Session-based API login.

    Because the project already uses Django SessionAuthentication,
    this keeps authentication aligned with the existing application.
    """

    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if user is None:
        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {"detail": "User account is inactive."},
            status=status.HTTP_403_FORBIDDEN,
        )

    login(request, user)

    return Response(
        {
            "detail": "Login successful.",
            "user": {
                "id": user.pk,
                "username": user.get_username(),
                "is_staff": user.is_staff,
            },
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)

    return Response(
        {"detail": "Logout successful."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    user = request.user

    return Response(
        {
            "id": user.pk,
            "username": user.get_username(),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
        }
    )
