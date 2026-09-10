from .base import *


DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "same-origin"

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        default="",
    ).split(",")
    if origin.strip()
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
