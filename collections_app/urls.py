from django.urls import path
from . import views

app_name = 'collections_app'

urlpatterns = [
    path("", views.collections, name="collections"),
    path("<int:collection_id>/", views.collection_detail, name="collection_detail"),
]