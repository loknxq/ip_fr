from django.urls import path

from . import views

app_name = "records"

urlpatterns = [
    path("", views.records, name="records"),
    path("search/", views.search_records, name="search"),
    # Старая ссылка из ПР9 сохранена ради совместимости.
    path("<int:record_id>/", views.record_detail, name="record_detail"),
    path("<slug:slug>/", views.record_detail_by_slug, name="record_by_slug"),
]
