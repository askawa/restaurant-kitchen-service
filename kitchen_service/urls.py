"""Root URL configuration for the Restaurant Kitchen Service."""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("kitchen.urls", namespace="kitchen")),
]
