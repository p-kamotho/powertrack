from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PropertyViewSet,
    RoomViewSet,
    TenantViewSet,
    MeterViewSet,
    BillingPeriodViewSet,
    ReadingViewSet,
    TariffViewSet,
    BillViewSet,
    PaymentViewSet,
    NotificationViewSet,
    login_view,
    logout_view,
    current_user_view,
)


router = DefaultRouter()

router.register("properties", PropertyViewSet, basename="property")
router.register("rooms", RoomViewSet, basename="room")
router.register("tenants", TenantViewSet, basename="tenant")
router.register("meters", MeterViewSet, basename="meter")
router.register("billing-periods", BillingPeriodViewSet, basename="billing-period")
router.register("readings", ReadingViewSet, basename="reading")
router.register("tariffs", TariffViewSet, basename="tariff")
router.register("bills", BillViewSet, basename="bill")
router.register("payments", PaymentViewSet, basename="payment")
router.register("notifications", NotificationViewSet, basename="notification")


urlpatterns = [
    path("auth/login/", login_view, name="api-login"),
    path("auth/logout/", logout_view, name="api-logout"),
    path("auth/me/", current_user_view, name="api-current-user"),
]

urlpatterns += router.urls
