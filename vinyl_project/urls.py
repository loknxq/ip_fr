"""
URL configuration for vinyl_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("records/", include("records.urls")),
    path("collections/", include("collections_app.urls")),
]

handler404 = "homepage.views.custom_404"