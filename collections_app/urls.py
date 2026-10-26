from django.urls import path
from . import views

app_name = 'collections_app'

urlpatterns = [
    path(
        "",
        views.collections,
        name="collections"),
    path(
        "statistics/",
        views.statistics,
        name="statistics"),
    path(
        "<int:collection_id>/",
        views.collection_detail,
        name="collection_detail"),
]
