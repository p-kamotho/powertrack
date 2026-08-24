from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-change-me")

DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = [x.strip() for x in config("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.accounts.apps.AccountsConfig",
    "apps.properties.apps.PropertiesConfig",
    "apps.tenants.apps.TenantsConfig",
    "apps.meters.apps.MetersConfig",
    "apps.readings.apps.ReadingsConfig",
    "apps.tariffs.apps.TariffsConfig",
    "apps.billing.apps.BillingConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.reports.apps.ReportsConfig",
    "apps.dashboard.apps.DashboardConfig"
]

MIDDLEWARE = [
"django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware",
"django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware",
"django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware",
"django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF="config.urls"
TEMPLATES=[{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],
"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request",
"django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION="config.wsgi.application"; ASGI_APPLICATION="config.asgi.application"

DATABASES={
    "default":{
        "ENGINE":"django.db.backends.postgresql",
        "NAME":config("POSTGRES_DB",default="powertrack"),
        "USER":config("POSTGRES_USER",default="powertrack"),
        "PASSWORD":config("POSTGRES_PASSWORD",default="powertrack"),
        "HOST":config("POSTGRES_HOST",default="127.0.0.1"),
        "PORT":config("POSTGRES_PORT",default="5432")
    }
}

AUTH_USER_MODEL="accounts.User"
AUTH_PASSWORD_VALIDATORS=[{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"}]
LANGUAGE_CODE="en-us"; TIME_ZONE="Africa/Nairobi"; USE_I18N=True; USE_TZ=True
STATIC_URL="/static/"; STATIC_ROOT=BASE_DIR/"staticfiles"; STATICFILES_DIRS=[BASE_DIR/"static"]
MEDIA_URL="/media/"; MEDIA_ROOT=BASE_DIR/"media"; DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
LOGIN_URL="login"; LOGIN_REDIRECT_URL="dashboard"; LOGOUT_REDIRECT_URL="login"
REST_FRAMEWORK={"DEFAULT_PERMISSION_CLASSES":["rest_framework.permissions.IsAuthenticated"],
"DEFAULT_AUTHENTICATION_CLASSES":["rest_framework.authentication.SessionAuthentication"]}
CELERY_BROKER_URL=config("REDIS_URL",default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND=CELERY_BROKER_URL
