from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path("", views.records, name="records"),
    path("search/", views.search_records, name="search"),
    path("<int:record_id>/", views.record_detail, name="record_detail"),
]
