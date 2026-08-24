from rest_framework.routers import DefaultRouter
from .views import MeterViewSet, ReadingViewSet, BillViewSet, PaymentViewSet

router = DefaultRouter()
router.register("meters", MeterViewSet)
router.register("readings", ReadingViewSet)
router.register("bills", BillViewSet)
router.register("payments", PaymentViewSet)
urlpatterns = router.urls
