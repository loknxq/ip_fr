"""Маршруты интеграционных тестов реальной SQL-панели."""

from django.urls import include, path

urlpatterns = [
    path("", include("vinyl_project.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
