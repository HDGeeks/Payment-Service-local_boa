import io
import os
from urllib.parse import urlparse

import environ

# Import the original settings from each template
from .settings import *

# Load the settings from the environment variable
env = environ.Env()

# env = environ.Env(
#     # set casting, default value
#     DEBUG=(bool, True)
# )
env.read_env(io.StringIO(os.environ.get("PAYMENT_SERVICE_SETTINGS", None)))

# Setting this value from django-environ
SECRET_KEY = env('SECRET_KEY')

# If defined, add service URL to Django security settings
PAYMENT_SERVICE_URL = env("PAYMENT_SERVICE_URL", default=None)


if PAYMENT_SERVICE_URL:
    ALLOWED_HOSTS = [urlparse(PAYMENT_SERVICE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [PAYMENT_SERVICE_URL]
else:
    ALLOWED_HOSTS = ["*"]

# Default false. True allows default landing pages to be visible
DEBUG = env("DEBUG", default=True)

# Set this value from django-environ
DATABASES = {"default": env.db()}

# Change database settings if using the Cloud SQL Auth Proxy
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    DATABASES["default"]["HOST"] = "127.0.0.1"
    DATABASES["default"]["PORT"] = 5432

if "core" not in INSTALLED_APPS:
    INSTALLED_APPS += ["core"]  # for custom data migration

# Define static storage via django-storages[google]
GS_BUCKET_NAME = env("GS_BUCKET_NAME")
STATICFILES_DIRS = []
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_DEFAULT_ACL = "publicRead"
