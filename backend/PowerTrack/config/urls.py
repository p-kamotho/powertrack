from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
urlpatterns=[
    path("admin/",admin.site.urls),
    path("api/",include("api.api_urls")),
    path("",include("apps.dashboard.urls")),
    path("auth/",include("apps.accounts.urls")),
    path("properties/",include("apps.properties.urls")),
    path("tenants/",include("apps.tenants.urls")),
    path("meters/",include("apps.meters.urls")),
    path("readings/",include("apps.readings.urls")),
    path("tariffs/",include("apps.tariffs.urls")),
    path("billing/",include("apps.billing.urls")),
    path("payments/",include("apps.payments.urls")),
    path("notifications/",include("apps.notifications.urls")),
    path("reports/",include("apps.reports.urls"))
]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
