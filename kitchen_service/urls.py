"""Root URL configuration for the Restaurant Kitchen Service."""

from django.contrib import admin
from django.urls import path


urlpatterns = [
    path("admin/", admin.site.urls),
]
